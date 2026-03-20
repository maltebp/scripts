# FAILED ATTEMPT AT STARTING KANATA FROM CLI

# import sys
# import argparse
# from pathlib import Path
# from scripts_core import *

# process_args_start_index = 1

# print(sys.argv)

# if len(sys.argv) == 1:
#     user_error_and_exit("Missing process path (no arguments provided)")

# log_file_name = None
# if sys.argv[1] == "--log-file":
#     if len(sys.argv) == 2:
#         user_error_and_exit("--log-file is missing value")

#     log_file_name = sys.argv[2]
#     process_args_start_index = 3

# if len(sys.argv) <= process_args_start_index:
#     user_error_and_exit("Missing process path")

# executable_path = Path(sys.argv[process_args_start_index]).resolve()
# if not executable_path.exists():
#     user_error_and_exit(f"Executable to run '{executable_path}' does not exist")


# process_args = sys.argv[process_args_start_index : ]

# if log_file_name is not None:
#     log_dir = get_log_dir()
#     if not log_dir.exists():
#         log_dir.mkdir()

#     log_file_path = log_dir / log_file_name

#     # TODO: replace quotes with escaped quotes
#     command_line_string = " ".join([f'"{x}"' for x in process_args])

#     with open(log_file_path, "a") as log_file:
#         log_file.write("\n")
#         log_file.write(f"Starting process: {command_line_string}\n")
#         log_file.write(f"Time: {datetime.now()}\n")
#         log_file.flush()

#         subprocess.run(
#             process_args, 
#             #stdout=log_file,
#             #stderr=log_file,
#             shell=True # Needed for Kanata to work correctly
#         )

# else:
#     subprocess.Popen(
#         process_args
#     )


# # start_background_process(
# #     [
# #         str(kanata_exe_path), 
# #         "--cfg", 
# #         str(kanata_config_path),
# #     ], 
# #     log_file_name="kanata.log")



# # parser = argparse.ArgumentParser("kanatastart")
# # parser.add_argument("kanatadir")
# # parser.add_argument("config")
# # args = parser.parse_args()

# # kanata_dir = Path(args.kanatadir).absolute()
# # if not kanata_dir.exists():
# #     user_error_and_exit(f"Kanata directory '{kanata_dir}' does not exist");

# # kanata_exe_path = kanata_dir / "kanata_windows_gui_winIOv2_cmd_allowed_x64.exe"
# # if not kanata_exe_path.exists():
# #     user_error_and_exit(f"Kanata exe '{kanata_exe_path}' does not exist");

# # kanata_config_path = Path(args.config).absolute()
# # if not kanata_config_path.is_file():
# #     user_error_and_exit(f"Kanata config file '{kanata_exe_path}' is not an existing file");

