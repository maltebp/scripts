@echo off

call "%~dp0..\config.cmd"

start "" %s_path_hourglass% --theme black-dark --window-state minimized --sound "Quiet beep" %*