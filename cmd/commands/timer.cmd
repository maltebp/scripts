@echo off

call "%~dp0..\config.cmd"

set hourglass_path="%~dp0..\..\external\hourglass\HourglassPortable.exe"

start "" %hourglass_path% --theme black-dark --window-state minimized --sound "Quiet beep" %*