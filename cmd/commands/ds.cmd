@echo off

call "%~dp0..\config.cmd"

set ds_temp_dir=%USERPROFILE%\AppData\Local\Temp\

if not exist %ds_temp_dir%  (
    echo User temp directory '%ds_temp_dir%' was not found
    exit /b 1
)

set ds_temp_file=%ds_temp_dir%ds_bat_output.tmp
%s_path_python% "%~dp0..\python\ds.py" %* >%ds_temp_file% 2>&1

if %errorlevel% NEQ 0 goto:err
set /p ds_target=<%ds_temp_file%
cd /d %ds_target%
set failed=0
goto :end

:err
type %ds_temp_file%
set failed=1

:end
del %ds_temp_file%

:: Why this? Apparently, exit /b 1 does not report the exit code in a way such that && understands it.
:: Meaning a subsequent && would not respect it failing. So we have to call this as the very last
:: command in the script for it to propagate correctly.
cmd /c exit %failed%