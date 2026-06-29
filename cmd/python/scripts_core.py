import sys
import subprocess
from datetime import datetime
from pathlib import Path

def get_log_dir() -> Path:
    script_path = Path(__file__).resolve()
    return script_path.parent.parent.parent / "logs"

def user_error_and_exit(message: str):
    print(f"[Error] {message}", file=sys.stderr)
    sys.exit(1)

def expect(expression: bool, failure_message: str):
    if expression: return
    print(f'[Internal Error] {failure_message}')
    sys.exit()

# def start_background_process(command_line, log_file_name):

#     log_dir = get_log_dir()
#     if not log_dir.exists():
#         log_dir.mkdir()

#     log_file_path = log_dir / log_file_name
    
#     # TODO: replace quotes with escaped quotes
#     command_line_string = " ".join([f'"{x}"' for x in command_line])

#     with open(log_file_path, "a") as log_file:
#         log_file.write("\n")
#         log_file.write(f"Starting process: {command_line_string}\n")
#         log_file.write(f"Time: {datetime.now()}\n")

#     adjusted_args = [
#         "start",
#         "",
#         "/b",
#         *command_line,
#         "^>",
#         str(log_file_path)
#     ]

#     DETACHED_PROCESS=0x00000008 # Windows only
#     subprocess.Popen(adjusted_args, close_fds=True, shell=True, creationflags=DETACHED_PROCESS)
    