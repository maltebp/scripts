import subprocess
import os
import sys

from scripts_core import *

expect(len(sys.argv) > 1, "Missing Visual Studio path (no arguments passed)")

vs_path = sys.argv[1]
expect(not os.path.isdir(vs_path), f"'Visual Studio path '{vs_path}' is a directory")
expect(os.path.isfile(vs_path), f"Visual Studio '{vs_path}' does not exist")

if len(sys.argv) == 2:
    # Just open Visual Studio
    DETACHED_PROCESS=0x00000008 # Windows only
    subprocess.Popen([vs_path], close_fds=True, creationflags=DETACHED_PROCESS)
else:
    expect(len(sys.argv) == 3, "Too many paths")

    path_to_open = os.path.realpath(sys.argv[2])

    expect(os.path.exists(path_to_open), (f"'{path_to_open}' does not exist"))

    solution_file = None

    if os.path.isdir(path_to_open):
        files_in_dir = os.listdir(path_to_open)
        solution_files = [f for f in files_in_dir if f.endswith('.sln')]
        print(solution_file)
        expect(len(solution_files) > 0, f"No solution files found in directory '{path_to_open}'")
        solution_file = path_to_open + '\\' + solution_files[0]
    else:
        expect(path_to_open.endswith('.sln'), f"'{path_to_open}' does not seem to be a solution file (not ending with .sln)")
        solution_file = path_to_open

    DETACHED_PROCESS=0x00000008 # Windows only
    subprocess.Popen([vs_path, solution_file], close_fds=True, creationflags=DETACHED_PROCESS)