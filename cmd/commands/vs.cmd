@echo off

CALL "%~dp0..\config.cmd"

%s_path_python% "%~dp0..\python\vs.py" %s_path_vs% %*