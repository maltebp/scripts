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
cd %ds_target%
goto :end

:err
type %ds_temp_file%

:end
del %ds_temp_file%
@echo on