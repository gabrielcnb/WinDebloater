@echo off
chcp 65001 >nul
title WinDebloater
cd /d "%~dp0"
python "%~dp0src\main.py"
if %errorlevel% neq 0 pause
