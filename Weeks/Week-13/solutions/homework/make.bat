@echo off
setlocal

set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=run"

if /I "%TARGET%"=="help" goto :usage
if /I "%TARGET%"=="run" goto :valid
if /I "%TARGET%"=="send" goto :valid
if /I "%TARGET%"=="flash" goto :valid

echo [ERROR] Unsupported target: %TARGET%
goto :usage

:valid
set "PORT=%~2"
if "%PORT%"=="" set "PORT=4000"

:python_ready

set "THIS_DIR=%~dp0"
for %%I in ("%THIS_DIR%..\..\..\..") do set "ROOT=%%~fI"

set "PY_CMD="
if exist "%ROOT%\.venv\Scripts\python.exe" set "PY_CMD=%ROOT%\.venv\Scripts\python.exe"
if exist "%ROOT%\.venv\Scripts\python.exe" goto :python_ready2

if defined PYTHON goto :use_python_from_env

where python >nul 2>nul && set "PY_CMD=python"
if defined PY_CMD goto :python_ready2

where py >nul 2>nul && set "PY_CMD=py -3"
if defined PY_CMD goto :python_ready2

goto :python_missing

:use_python_from_env
set "PY_CMD=%PYTHON%"
goto :python_ready2

:python_missing
echo [ERROR] Python not found. Install Python and ensure it is in PATH.
echo         Or run: set PYTHON=python (or py -3) then make.bat
exit /b 9009

:python_ready2

echo ^>^>^> Make sure the Wokwi simulator is running in VS Code
%PY_CMD% "%ROOT%\tools\wokwi_run.py" --port %PORT% "%THIS_DIR%main.py"
set "RC=%ERRORLEVEL%"
exit /b %RC%

:usage
echo Usage:
echo   make.bat [run^|send^|flash] [PORT]
echo.
echo Examples:
echo   make.bat
echo   make.bat run 4000
echo   set PYTHON=py -3 ^&^& make.bat flash 4001
exit /b 1
