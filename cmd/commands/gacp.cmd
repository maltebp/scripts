:: @echo off

if "%~1"=="" (
    git add -A && git commit && git push
) else (
    git add -A && git commit -m "%~1" && git push
)