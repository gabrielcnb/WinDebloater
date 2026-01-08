@echo off
chcp 65001 >nul

:: Verifica se está rodando como admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando privilégios de administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

title WinDebloater
cd /d "%~dp0"
python "%~dp0src\main.py"
if %errorlevel% neq 0 pause
