import sys
import argparse
import re

from pathlib import Path


def print_error_and_exit(error):
    print(f'Error: ' + error, file=sys.stderr)
    sys.exit(1)


def remove_empty_recursively(path, dry_run, print_removed, exclusions):

    num_removed_directories = 0

    for item in path.iterdir():
        if item.is_dir():
            num_removed_directories += remove_empty_recursively(item, dry_run, print_removed, exclusions)

    is_empty = True
    for item in path.iterdir():
        matched_exclusion = False

        for exclusion in exclusions:
            if exclusion.findall(str(item)):
                matched_exclusion = True
                break
        
        if not matched_exclusion:
            is_empty = False
            break

    if is_empty:

        for item in path.iterdir():
            # Only excluded items remain
            if print_removed:
                print("Deleted: " + str(item))    
            item.unlink()

        if print_removed:
            print("Deleted: " + str(path))
        path.rmdir()
        num_removed_directories += 1
    
    return num_removed_directories


def root_command(args):
    path = Path(args.path)

    if not path.exists():
        print_error_and_exit(f"Cannot find directory: '{path}'")

    if path.is_file():
        print_error_and_exit(f"Path is a file, not a directory: '{path}'");
    
    exclusions = []
    if args.exclude is not None:
        filters = args.exclude.split(';')

        for filter in filters:
            if len(filter) == 0: continue

            unsupported_regex = ".^$+?{}[]\|()"

            cleaned_filter = ""
            for c in filter:
                if c in unsupported_regex:
                    cleaned_filter += "\\" + c
                elif c == "*":
                    cleaned_filter += ".*"
                else:
                    cleaned_filter += c

            pattern = re.compile(cleaned_filter)
            exclusions.append(pattern)

    #dry_run = args.dry_run is not None
    list_removed_items = args.list_removed# or dry_run

    num_removed_directories = remove_empty_recursively(path, False, list_removed_items, exclusions)
    print(f'Items removed: {num_removed_directories}')

parser = argparse.ArgumentParser('rmempty')
parser.set_defaults(func=root_command)
parser.add_argument("path", help="The path to recursively remove empty directories from (including the directory itself)", action="store")
parser.add_argument("-l", "--list-removed", help="Print all removed directories", action="store_true")
parser.add_argument("-e", "--exclude", help="List of files that counts as non-existent items (if a directory contains only files that these filters they will be removed). Separated by semi-colon and supports wildcards *.", action="store")

# TODO: Didn't fully implement this, because it was more complicated than I thought (current behavior relies on sub-items being deleted)
#parser.add_argument("--dry-run", help="Runs the command and lists all items that will be deleted without actually deleting them (--list-removed flag is implicitly added)", action="store_true")

args = parser.parse_args()
args.func(args)