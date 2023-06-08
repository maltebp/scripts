@echo off

CALL "%~dp0..\config.cmd"

%s_path_python% "%~dp0..\python\typo.py" %s_path_typora% %*