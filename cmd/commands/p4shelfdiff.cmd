@echo off

CALL "%~dp0..\config.cmd"

%s_path_python% "%~dp0..\python\p4shelfdiff.py" %s_path_winmerge% %*
