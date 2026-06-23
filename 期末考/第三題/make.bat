@echo off
setlocal

set THIS_DIR=%~dp0
set ROOT_DIR=%THIS_DIR%..\..
set PORT=4003

if exist "%ROOT_DIR%\.venv\Scripts\python.exe" (
  set PY_CMD=%ROOT_DIR%\.venv\Scripts\python.exe
) else (
  set PY_CMD=python
)

echo ^>^>^> Make sure the Wokwi simulator is running in VS Code.
"%PY_CMD%" "%THIS_DIR%run.py" --port %PORT%

endlocal
