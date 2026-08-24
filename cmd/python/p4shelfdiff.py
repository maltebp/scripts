"""Folder-diffs the local files of a Perforce changelist against its shelve.

Usage (via 'p4shelfdiff.cmd'): p4shelfdiff <changelist>

The left side of the comparison is the workspace itself, so the real files are
diffed and any edit made in WinMerge lands on the actual file. The right side is
the shelve, fetched with 'p4 print' into '%TEMP%\\p4shelfdiff\\<changelist>' and
opened read-only, since it is a throwaway copy.

Because the workspace side stays writable, the workspace files are copied to
'local-backup' next to the fetched shelve before WinMerge starts. A stray 'copy to
left' in the comparison would otherwise overwrite work that exists only on disk,
with nothing to recover it from - the shelve holds the older content by
definition.

Note that 'p4 print' writes the workspace line endings (CRLF here), so a file that
was added with LF endings reads as different on every line. That is left visible
rather than suppressed, so what is on disk is what is reported.

Showing only the changelist's files, without WinMerge walking the whole branch, is
done with a generated file filter. WinMerge prunes excluded folders instead of
enumerating and then hiding them, so the comparison stays fast however large the
branch is (measured at 0.16s against a 418k-file tree).

The filter is rooted at the deepest common folder of the changelist's files and
holds one 'd:' rule per folder level on the way down, plus one 'fe: RelPath' rule
per file. Both rule kinds match a path relative to the compare root, so the same
filter serves the workspace side and the temp side despite their different roots.
Matching is case-insensitive, which matters because Perforce reports depot casing
rather than on-disk casing.

WinMerge only accepts a filter by *name*, out of its own filter folder - a path to
a '.flt' passed to '/f' is silently taken as a filename mask that matches nothing.
So the filter is installed into '%APPDATA%\\WinMerge\\Filters' as one file per
changelist, and stale ones from previous runs are cleaned up.

Files with no content on a side (a delete, or a file no longer open locally) are
simply absent there and show up as one-sided in the comparison.

Erroring cases: the changelist does not exist, is not pending, has no shelved
files, has no files open in the current client, or WinMerge is not configured
('s_path_winmerge').
"""

import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

from scripts_core import *

# Perforce actions where the file has no content on that side.
ACTIONS_WITHOUT_CONTENT = ["delete", "move/delete", "purge"]

FILTER_PREFIX = "p4shelfdiff-"


def run_p4(arguments, stdin_input=None):
    try:
        return subprocess.run(
            ["p4", "-ztag", *arguments],
            input=stdin_input,
            capture_output=True,
            text=True
        )
    except FileNotFoundError:
        user_error_and_exit("'p4' was not found on PATH - is the Perforce command line client installed?")


def parse_ztag(output):
    """Parses 'p4 -ztag' output into one dict per record.

    A repeated key starts a new record. Blank lines cannot be used as the
    separator, because multi-line values (such as a changelist description)
    contain them. Continuation lines of such values carry no '... ' prefix and
    are dropped - none of the fields read here are multi-line.
    """
    records = []
    current = {}

    for line in output.splitlines():
        if not line.startswith("... "):
            continue
        key, _, value = line[4:].partition(" ")
        if key in current:
            records.append(current)
            current = {}
        current[key] = value

    if current:
        records.append(current)

    return records


def indexed_records(fields, keys):
    """Expands 'depotFile0, depotFile1, ...' style fields into a list of dicts."""
    records = []
    index = 0
    while f"{keys[0]}{index}" in fields:
        records.append({key: fields.get(f"{key}{index}") for key in keys})
        index += 1
    return records


def force_remove_tree(directory):
    # 'p4 print -o' writes read-only files, which plain deletion refuses.
    def make_writable_and_retry(function, path, exception):
        os.chmod(path, stat.S_IWRITE)
        function(path)

    shutil.rmtree(directory, onexc=make_writable_and_retry)


def get_current_client():
    result = run_p4(["info"])
    records = parse_ztag(result.stdout)
    return records[0].get("clientName") if len(records) > 0 else None


def get_shelved_files(changelist):
    result = run_p4(["describe", "-S", "-s", changelist])

    # A missing or malformed changelist is reported on stderr, with an empty
    # stdout and an exit code of 0.
    describe_records = parse_ztag(result.stdout)
    if len(describe_records) == 0:
        user_error_and_exit(result.stderr.strip() or f"Changelist '{changelist}' could not be described")

    fields = describe_records[0]

    status = fields.get("status")
    if status != "pending":
        user_error_and_exit(
            f"Changelist {changelist} is {status or 'not pending'} - only pending changelists can hold a shelve")

    shelved_files = indexed_records(fields, ["depotFile", "action"])
    if len(shelved_files) == 0:
        user_error_and_exit(f"Changelist {changelist} has no shelved files")

    return shelved_files, fields.get("client")


def get_local_files(changelist, changelist_client):
    result = run_p4(["opened", "-c", changelist])
    if result.returncode != 0:
        user_error_and_exit(result.stderr.strip() or f"Could not list the files open in changelist {changelist}")

    opened_files = parse_ztag(result.stdout)
    if len(opened_files) == 0:
        message = f"Changelist {changelist} has no local files"
        current_client = get_current_client()
        # 'p4 opened' only ever reports the current client, so a changelist owned
        # by another client looks empty here however many files it holds.
        if changelist_client and current_client and changelist_client != current_client:
            message += f" in client '{current_client}' - it belongs to client '{changelist_client}'"
        user_error_and_exit(message)

    return opened_files


def get_workspace_paths(depot_paths):
    """Maps depot paths to their workspace paths, in on-disk casing.

    'p4 opened' reports clientFile in client syntax ('//client/...') rather than
    as a filesystem path, so 'p4 where' has to do the mapping. The depot paths go
    in on stdin ('-x -') to keep long changelists off the command line.
    """
    result = run_p4(["-x", "-", "where"], stdin_input="\n".join(depot_paths) + "\n")

    workspace_paths = {}
    for record in parse_ztag(result.stdout):
        if "path" not in record:
            continue
        # 'p4 where' answers in depot casing; resolve() recovers the real casing
        # so the temp tree does not read as a case mismatch next to the workspace.
        workspace_paths[record["depotFile"]] = str(Path(record["path"]).resolve())

    # A single unmapped file only costs that one file, but nothing mapped at all
    # means the lookup itself failed.
    if len(workspace_paths) == 0:
        user_error_and_exit(result.stderr.strip() or "Could not map the changelist files to workspace paths")

    return workspace_paths


def get_common_root(workspace_paths):
    directories = [os.path.dirname(path) for path in workspace_paths]
    try:
        return os.path.commonpath(directories)
    except ValueError:
        user_error_and_exit("The changelist spans more than one drive, which cannot be compared as one folder pair")


def populate_shelved_tree(shelved_files, changelist, relative_paths, target_directory):
    printed_count = 0

    for file in shelved_files:
        depot_path = file["depotFile"]

        if file["action"] in ACTIONS_WITHOUT_CONTENT:
            print(f"  shelved as {file['action']}, nothing to fetch: {depot_path}")
            continue

        relative_path = relative_paths.get(depot_path)
        if relative_path is None:
            print(f"  skipped (not in client view) {depot_path}", file=sys.stderr)
            continue

        destination = os.path.join(target_directory, relative_path)
        os.makedirs(os.path.dirname(destination), exist_ok=True)

        result = run_p4(["print", "-q", "-o", destination, f"{depot_path}@={changelist}"])
        if result.returncode != 0 or not os.path.isfile(destination):
            print(f"  skipped (could not print) {depot_path}: {result.stderr.strip()}", file=sys.stderr)
            continue

        printed_count += 1

    return printed_count


def backup_local_files(local_files, workspace_paths, relative_paths, backup_directory):
    """Copies the workspace files aside before WinMerge is pointed at them.

    The workspace side is deliberately left writable, which is the whole point of
    comparing the real files - but it also means a mis-click on 'copy to left'
    overwrites work that only exists on disk. These copies make that recoverable.
    """
    backed_up_count = 0

    for file in local_files:
        depot_path = file["depotFile"]
        workspace_path = workspace_paths.get(depot_path)
        relative_path = relative_paths.get(depot_path)

        if workspace_path is None or relative_path is None:
            continue
        if not os.path.isfile(workspace_path):
            continue

        destination = os.path.join(backup_directory, relative_path)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copyfile(workspace_path, destination)
        backed_up_count += 1

    return backed_up_count


def path_to_regex(path):
    """Turns a relative path into the backslash-escaped regex a filter rule wants."""
    return "\\\\".join(re.escape(part) for part in path.split(os.sep))


def build_filter(filter_name, relative_paths):
    """Builds an inclusive-only filter: exactly these files, and the folders to reach them.

    'def: exclude' inverts the usual meaning - rules say what to let *through*, so
    the rule count grows with the depth of the tree rather than with its width.
    """
    directories = set()
    for relative_path in relative_paths:
        parts = relative_path.split(os.sep)[:-1]
        for depth in range(1, len(parts) + 1):
            directories.add(os.sep.join(parts[:depth]))

    lines = [
        f"name: {filter_name}",
        "desc: Generated by p4shelfdiff - do not edit",
        "def: exclude"
    ]

    for directory in sorted(directories):
        lines.append("d: \\\\" + path_to_regex(directory) + "$")

    # 'f:' rules only ever see the file name, so a path-precise rule needs 'fe:'
    # (WinMerge 2.16.19+), whose RelPath is the path relative to the compare root,
    # without a leading separator. The '^' matters: unanchored, a rule for a file
    # near the root would also let through a same-named file further down.
    for relative_path in sorted(relative_paths):
        lines.append(f'fe: RelPath matches "^{path_to_regex(relative_path)}$"')

    return "\n".join(lines) + "\n"


def install_filter(changelist, relative_paths):
    filter_directory = os.path.join(os.environ["APPDATA"], "WinMerge", "Filters")
    os.makedirs(filter_directory, exist_ok=True)

    filter_name = f"{FILTER_PREFIX}{changelist}"
    filter_path = os.path.join(filter_directory, f"{filter_name}.flt")

    # Previous runs leave a filter behind; it is only of use while its comparison
    # window is open, so clear out the ones that are not being written now.
    for entry in os.listdir(filter_directory):
        if entry.startswith(FILTER_PREFIX) and entry != os.path.basename(filter_path):
            os.remove(os.path.join(filter_directory, entry))

    with open(filter_path, "w") as filter_file:
        filter_file.write(build_filter(filter_name, relative_paths))

    return filter_name


NOT_CONFIGURED_MESSAGE = "WinMerge is not configured - set 's_path_winmerge' in 'cmd\\config.cmd'"

expect(len(sys.argv) > 1, "Missing WinMerge path (no arguments passed)")

# An unconfigured 's_path_winmerge' expands to nothing at all, so a single
# argument is either the WinMerge path with no changelist after it, or the
# changelist with no WinMerge path in front of it.
if len(sys.argv) == 2:
    if os.path.isfile(sys.argv[1]):
        user_error_and_exit("Missing argument: the changelist number")
    user_error_and_exit(NOT_CONFIGURED_MESSAGE)

winmerge_path = sys.argv[1]
if winmerge_path == "":
    user_error_and_exit(NOT_CONFIGURED_MESSAGE)

if not os.path.isfile(winmerge_path):
    user_error_and_exit(f"WinMerge was not found at '{winmerge_path}' - check 's_path_winmerge' in 'cmd\\config.cmd'")

if len(sys.argv) != 3:
    user_error_and_exit(f"Expected 1 argument (the changelist number), got {len(sys.argv) - 2}")

changelist = sys.argv[2]
if not changelist.isdigit():
    user_error_and_exit(f"'{changelist}' is not a changelist number")

shelved_files, changelist_client = get_shelved_files(changelist)
local_files = get_local_files(changelist, changelist_client)

# The shelve and the local files need not hold the same set, so both contribute
# to the compare root and to the filter - that is what makes a file present on
# only one of the two sides show up as such.
depot_paths = {file["depotFile"] for file in shelved_files}
depot_paths.update(file["depotFile"] for file in local_files)

workspace_paths = get_workspace_paths(sorted(depot_paths))
workspace_root = get_common_root(workspace_paths.values())

relative_paths = {
    depot_path: os.path.relpath(workspace_path, workspace_root)
    for depot_path, workspace_path in workspace_paths.items()
}

changelist_directory = os.path.join(tempfile.gettempdir(), "p4shelfdiff", changelist)
shelved_directory = os.path.join(changelist_directory, "shelved")
backup_directory = os.path.join(changelist_directory, "local-backup")

if os.path.isdir(changelist_directory):
    force_remove_tree(changelist_directory)
os.makedirs(shelved_directory)
os.makedirs(backup_directory)

print(f"Comparing against workspace folder '{workspace_root}'")
print(f"Fetching {len(shelved_files)} shelved file(s) to '{shelved_directory}'")
shelved_count = populate_shelved_tree(shelved_files, changelist, relative_paths, shelved_directory)

backed_up_count = backup_local_files(local_files, workspace_paths, relative_paths, backup_directory)
print(f"Backed up {backed_up_count} workspace file(s) to '{backup_directory}'")

filter_name = install_filter(changelist, sorted(relative_paths.values()))
print(f"Comparing {len(relative_paths)} file(s) of changelist {changelist} ({shelved_count} shelved)")

# The left side is the workspace itself and stays writable so that edits reach the
# real files; only the shelved copy is forced read-only (/wr).
winmerge_arguments = [
    winmerge_path,
    "/r", "/u", "/e", "/wr",
    "/f", filter_name,
    "/dl", f"Local - CL {changelist}",
    "/dr", f"Shelved - CL {changelist}",
    workspace_root,
    shelved_directory
]

DETACHED_PROCESS = 0x00000008  # Windows only
subprocess.Popen(winmerge_arguments, close_fds=True, creationflags=DETACHED_PROCESS)
