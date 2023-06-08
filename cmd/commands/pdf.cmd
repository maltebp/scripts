@echo off

CALL "%~dp0..\config.cmd"

%s_path_python% "%~dp0..\python\pdf.py" %s_pdf_reader_path% %*