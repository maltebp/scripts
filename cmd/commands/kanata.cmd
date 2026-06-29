:: Failed attempt at starting Kanata via CMD
@REM CALL "%~dp0..\config.cmd"

@REM set kanata_config="%~dp0..\..\configs\kanata-config.kbd"
@REM set kanata_exe=%s_kanata_dir_path%\kanata_windows_tty_winIOv2_x64.exe

@REM %s_path_python_dir%\pythonw.exe "%~dp0..\python\run_process.py" --log-file "kanata.log" %kanata_exe% --cfg %kanata_config%
