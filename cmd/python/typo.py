import subprocess
import os
import sys

from scripts_core import *

expect(len(sys.argv) > 1, "Missing Typora path (no arguments passed)")

typora_path = sys.argv[1]
expect(not os.path.isdir(typora_path), f"'Typora path '{typora_path}' is a directory")
expect(os.path.isfile(typora_path), f"Typora path '{typora_path}' does not exist")

if len(sys.argv) == 2:
    # Just open typora
    DETACHED_PROCESS=0x00000008 # Windows only
    subprocess.Popen([typora_path], close_fds=True, creationflags=DETACHED_PROCESS)
else:
    expect(len(sys.argv) == 3, "Too many paths")

    path_to_open = sys.argv[2]
    if not os.path.exists(path_to_open):
        answer = input(f"'{path_to_open}' does not exist. Do want to create it? [y/n] ")
        
        if answer == "y" or answer == "Y":
            open(path_to_open, "x").close()
        else:
            sys.exit()
    DETACHED_PROCESS=0x00000008 # Windows only
    subprocess.Popen([typora_path, path_to_open], close_fds=True, creationflags=DETACHED_PROCESS)