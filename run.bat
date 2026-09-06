@echo off
chcp 65001 >nul

:: Check whether we are running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

title WinDebloater
cd /d "%~dp0"
python "%~dp0src\main.py"
if %errorlevel% neq 0 pause
