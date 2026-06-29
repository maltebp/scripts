@echo off

if "%~1"=="" (
 echo Error: Missing directory argument
 exit /b 1
)

:: Removing double backslashes (del doesn't support it)
set "targetdir=%~1"
set "targetdir=%targetdir:\\=\%"

if not exist "%targetdir%" (
    echo Directory '%targetdir%' not found
    exit /b 1 
)

echo Recursively deleting directory '%targetdir%'

echo Deleting directory content...
del /f /s /q "%targetdir%" > nul
if %errorlevel% NEQ 0 (
    echo Error: Failed to delete directory content
    exit /b 1
)

echo Deleting directory structure...
rmdir /s/q "%targetdir%"
if %errorlevel% NEQ 0 (
    echo Error: Failed to delete directory structure
    exit /b 1
)

if not exist "%targetdir%" (
    echo Success: directory was fully deleted
) else (
    echo Error: directory was not fully deleted 
    exit /b 1
)