@echo off
setlocal
cd /d %~dp0

if not exist .venv\Scripts\python.exe (
  echo [Setup] Creating virtual environment...
  python -m venv .venv
  if errorlevel 1 (
    echo [Error] Failed to create virtual environment. Make sure Python is installed.
    pause
    exit /b 1
  )
)

echo [Check] Verifying required modules...
.venv\Scripts\python.exe -c "import numpy, soundcard, deep_translator, faster_whisper" >nul 2>nul
if errorlevel 1 (
  echo [Setup] Installing required packages...
  .venv\Scripts\python.exe -m pip install --upgrade pip
  .venv\Scripts\python.exe -m pip install -r requirements-desktop-translator.txt
  if errorlevel 1 (
    echo [Error] Failed to install required packages.
    pause
    exit /b 1
  )
)

echo [Start] Launching translator...
.venv\Scripts\python.exe desktop_realtime_translator.py
if errorlevel 1 (
  echo [Error] The app exited with an error.
  pause
  exit /b 1
)
