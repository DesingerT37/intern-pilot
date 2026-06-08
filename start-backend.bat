@echo off
echo ========================================
echo   InternPilot Backend Startup Script
echo ========================================
echo.

cd intern-pilot-api

echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/3] Checking dependencies...
pip list | findstr fastapi

echo [3/3] Starting FastAPI server...
echo.
echo Backend will start at: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
python main.py
