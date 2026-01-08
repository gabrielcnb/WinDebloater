@echo off
chcp 65001 >nul
title WinDebloater - Setup
color 0A

:: Vai para o diretório do script
cd /d "%~dp0"

echo.
echo  ================================================
echo     WinDebloater - Instalador
echo  ================================================
echo.

:: Verifica se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python não encontrado!
    echo.
    echo Por favor, instale Python 3.10 ou superior:
    echo https://www.python.org/downloads/
    echo.
    echo Marque a opção "Add Python to PATH" durante a instalação.
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version

:: Verifica pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] pip não encontrado!
    pause
    exit /b 1
)

echo [OK] pip encontrado

:: Instala dependências
echo.
echo Instalando dependências...
echo.

pip install -r "%~dp0requirements.txt"

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha ao instalar dependências!
    pause
    exit /b 1
)

echo.
echo [OK] Dependências instaladas com sucesso!
echo.

:: Pergunta se quer executar
set /p run="Deseja executar o WinDebloater agora? (S/N): "
if /i "%run%"=="S" (
    echo.
    echo Iniciando WinDebloater...
    python "%~dp0src\main.py"
)

pause
