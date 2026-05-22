@echo off
setlocal

set "PORT=%~2"
if "%PORT%"=="" set "PORT=4000"

set "PY_CMD=python"
set "THIS_DIR=%~dp0"
set "SRC_DIR=%THIS_DIR:~0,-1%"

for %%I in ("%THIS_DIR%..\..\..\..") do set "ROOT=%%~fI"

set "COMBINED=%THIS_DIR%__combined_main.py"

echo Wokwi simulator should be running in VS Code.
echo Creating combined upload file...

%PY_CMD% -c "import os, pathlib; p=pathlib.Path(os.environ['SRC_DIR']); out=p/'__combined_main.py'; out.write_text((p/'goku_bitmap.py').read_text(encoding='utf-8') + '\n\n' + (p/'main.py').read_text(encoding='utf-8'), encoding='utf-8')"

if errorlevel 1 (
  echo Failed to create combined file.
  exit /b 1
)

%PY_CMD% "%ROOT%\tools\wokwi_run.py" --port %PORT% "%COMBINED%"

set "RC=%ERRORLEVEL%"
exit /b %RC%