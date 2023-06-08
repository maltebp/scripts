import subprocess
import os
import sys

from scripts_core import *

expect(len(sys.argv) > 1, "Missing PDF Reader path (no arguments passed)")

pdf_reader_path = sys.argv[1]
expect(not os.path.isdir(pdf_reader_path), f"'PDF reader path '{pdf_reader_path}' is a directory")
expect(os.path.isfile(pdf_reader_path), f"PDF reader path '{pdf_reader_path}' does not exist")

expect(len(sys.argv) == 3, f"Expected 1 argument, got {len(sys.argv)-2}")

pdf_path = sys.argv[2]
expect(os.path.exists(pdf_path), f"'{pdf_path}' does not exist")
expect(not os.path.isdir(pdf_path), f"'{pdf_path}' is a directory")

DETACHED_PROCESS=0x00000008 # Windows only
subprocess.Popen([pdf_reader_path, pdf_path], close_fds=True, creationflags=DETACHED_PROCESS)