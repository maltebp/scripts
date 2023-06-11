@echo off

if "%~1"=="" (
    git add -A && git commit
) else (
    git add -A && git commit -m "%~1"
)