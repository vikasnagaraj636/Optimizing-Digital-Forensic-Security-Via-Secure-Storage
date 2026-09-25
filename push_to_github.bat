@echo off
title Push Project to GitHub
cd /d "%~dp0"
set "PATH=%LOCALAPPDATA%\Programs\Git\cmd;%PATH%"

echo =====================================================================
echo   PUSHING TO GITHUB REPOSITORY:
echo   https://github.com/vikasnagaraj636/Optimizing-Digital-Forensic-Security-Via-Secure-Storage.git
echo =====================================================================
echo.

git push -u origin main

echo.
if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Code pushed successfully to GitHub!
) else (
    echo [ERROR] Push failed. If prompted, please complete browser login or provide GitHub token.
)
echo.
pause
