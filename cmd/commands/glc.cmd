@echo off

call "%~dp0..\config.cmd"

%s_path_python% "%~dp0..\python\g2.py" %*