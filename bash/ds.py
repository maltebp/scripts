import os
import argparse
import sys
import string

def validate_shortcut_name(shortcut_name: str):
    # Check for white space
    return not any([c in shortcut_name for c in string.whitespace])


def read_shortcuts():
    data_file_path = os.environ["HOME"] + "/AppData/Local/cds/shortcuts"
    
    if not os.path.exists(data_file_path):
        return {}

    data_file = open(data_file_path, "r")
    lines = data_file.read().split('\n')

    shortcuts = {}
    for line in lines:
        line_elements = line.split()
        if len(line_elements) < 2:
            continue
        shortcuts[line_elements[0]] = " ".join(line_elements[1:]).replace('"', '')

    return shortcuts


def store_shortcuts(shortcuts):
    data_dir_path = os.environ["HOME"] + "/AppData/Local/cds/"

    if not os.path.exists(data_dir_path):
        os.makedirs(data_dir_path)

    data_file_path = data_dir_path + "shortcuts"
    data_file = open(data_file_path, "wt")
    
    for name in shortcuts:
        data_file.write(f"{name} \"{shortcuts[name]}\"\n")
    
    data_file.close()


def list_shortcuts():
    shortcuts = read_shortcuts()

    if len(shortcuts) == 0:
        print("No shortcuts defined")

    for name in shortcuts:
        print(f"{name} = '{shortcuts[name]}'")


def add_shortcut(name: str, path: str, force: bool):
    shortcuts = read_shortcuts()

    if not force and name in shortcuts:
        print(f"error: '{name}' is already a shortcut to '{shortcuts[name]}'")
        sys.exit(-1)

    absolute_path = os.path.abspath(path)
    shortcuts[name] = absolute_path
    store_shortcuts(shortcuts)
    print(f"Mapped '{name}' to '{absolute_path}'")

    if not os.path.exists(absolute_path):
        print(f"Warning: the shortcut path does not exist")


def delete_shortcuts(names):
    shortcuts = read_shortcuts()

    for name in names:
        if not name in shortcuts:
            print(f"No shortcut named '{name}' exists") 
            continue
        dir = shortcuts[name]
        del shortcuts[name]
        print(f"Deleted shortcut '{name}' (it was mapped to '{dir}')")
    
    store_shortcuts(shortcuts)


def use_shortcut(name: str):
    shortcuts = read_shortcuts()
    if not name in shortcuts:
        print(f"Unknown shortcut '{name}'")
        sys.exit(-1)
    if not os.path.exists(shortcuts[name]):
        print(f"Shortcut directory '{shortcuts[name]}' does not exist")
        sys.exit(-1)
    
    # Because we can't change dir from within the script, we must output
    # the dir to target, and call a cd from bash
    print(shortcuts[name])
    

parser = argparse.ArgumentParser('ds')
parser.add_argument("shortcut", type=str, nargs='?' )
parser.add_argument("-l","--list", help="Lists the defined shortcuts", action="store_true")
parser.add_argument("-s", "--set", help="Assigns <dir> to the shortcut", metavar="<dir>", type=str)
parser.add_argument("-f", "--force-set", help="Overwrite existing shortcut with <dir>", action="store_true", dest="force")
parser.add_argument("-d", "--delete", metavar="<shortcuts>", type=str, nargs="*")


args = parser.parse_args()

if args.list is False and args.shortcut is None and args.delete is None:
    parser.error("missing argument: dir")    

if args.list is True:
    list_shortcuts()
    sys.exit(1)

if args.set is not None:
    shortcut_path = args.set
    if not validate_shortcut_name(args.shortcut):
        print(f"Invalid shortcut name '{args.shortcut}'")
        sys.exit(-1)
    add_shortcut(args.shortcut, shortcut_path, args.force)
    sys.exit(1)

if args.delete is not None:
    shortcut_names = []
    shortcut_names += args.delete
    if not args.shortcut is None:
        shortcut_names += args.shortcut
    delete_shortcuts(shortcut_names)
    sys.exit(1)

use_shortcut(args.shortcut)



    



