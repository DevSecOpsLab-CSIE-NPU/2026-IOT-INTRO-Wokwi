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
if "%PORT%"=="" set "PORT=4001"

set "PY_CMD="
if defined PYTHON (
  set "PY_CMD=%PYTHON%"
) else (
  where python >nul 2>nul && set "PY_CMD=python"
  if not defined PY_CMD (
    where py >nul 2>nul && set "PY_CMD=py -3"
  )
)

if not defined PY_CMD (
  echo [ERROR] Python not found. Install Python and ensure it is in PATH.
  exit /b 9009
)

set "THIS_DIR=%~dp0"
for %%I in ("%THIS_DIR%..\..\..") do set "ROOT=%%~fI"

set "UPLOAD_ONLY="
if /I "%TARGET%"=="send" set "UPLOAD_ONLY=--upload-only"
if /I "%TARGET%"=="flash" set "UPLOAD_ONLY=--upload-only"

%PY_CMD% "%ROOT%\tools\wokwi_run.py" --port %PORT% %UPLOAD_ONLY% "%THIS_DIR%main.py"
set "RC=%ERRORLEVEL%"
exit /b %RC%

:usage
echo Usage:
echo   make.bat [run^|send^|flash] [PORT]
exit /b 1
