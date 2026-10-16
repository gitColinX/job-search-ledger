@echo off
rem Job Search Ledger launcher for Windows. First run creates .venv and installs packages.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Setting up Job Search Ledger for the first time...
  py -3 -m venv .venv || python -m venv .venv
  ".venv\Scripts\python.exe" -m pip install --upgrade pip
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt -r requirements-windows.txt
)
start "" ".venv\Scripts\pythonw.exe" "%~dp0launch.pyw"
