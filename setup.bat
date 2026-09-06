@echo off
chcp 65001 >nul

:: Check whether we are running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

title WinDebloater - Setup
color 0A

:: Move to the script directory
cd /d "%~dp0"

echo.
echo  ================================================
echo     WinDebloater - Instalador
echo  ================================================
echo.

:: Check that Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo.
    echo Por favor, instale Python 3.10 ou superior:
    echo https://www.python.org/downloads/
    echo.
    echo Tick "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version

:: Check pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip not found!
    pause
    exit /b 1
)

echo [OK] pip encontrado

:: Install dependencies
echo.
echo Installing dependencies...
echo.

pip install -r "%~dp0requirements.txt"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo [OK] Dependencies installed.
echo.

:: Pergunta se quer executar
set /p run="Deseja executar o WinDebloater agora? (S/N): "
if /i "%run%"=="S" (
    echo.
    echo Iniciando WinDebloater...
    python "%~dp0src\main.py"
)

pause
