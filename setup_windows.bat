@echo off
setlocal
cd /d "%~dp0"
echo ==========================================
echo        ResearchMind AI - Setup
echo ==========================================
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher not found. Install Python 3.10+ and enable Add Python to PATH.
  pause
  exit /b 1
)
py -3 -m venv .venv
if errorlevel 1 (
  echo Could not create virtual environment.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed. Check your internet connection and Python version.
  pause
  exit /b 1
)
if not exist data mkdir data
echo.
echo Setup complete. Run run_windows.bat to start ResearchMind AI.
pause
