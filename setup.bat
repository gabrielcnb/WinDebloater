@echo off
title WinDebloater - Setup
color 0A

echo.
echo  ================================================
echo     WinDebloater - Instalador
echo  ================================================
echo.

:: Verifica se Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Por favor, instale Python 3.10 ou superior:
    echo https://www.python.org/downloads/
    echo.
    echo Marque a opcao "Add Python to PATH" durante a instalacao.
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version

:: Verifica pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] pip nao encontrado!
    pause
    exit /b 1
)

echo [OK] pip encontrado

:: Instala dependencias
echo.
echo Instalando dependencias...
echo.

pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha ao instalar dependencias!
    pause
    exit /b 1
)

echo.
echo [OK] Dependencias instaladas com sucesso!
echo.

:: Pergunta se quer executar
set /p run="Deseja executar o WinDebloater agora? (S/N): "
if /i "%run%"=="S" (
    echo.
    echo Iniciando WinDebloater...
    python src\main.py
)

pause
