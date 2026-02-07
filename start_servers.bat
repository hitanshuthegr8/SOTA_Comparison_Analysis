@echo off
echo ============================================================
echo 🧠 AI Research Ideation Pipeline - Starting Servers
echo ============================================================
echo.

:: Check if Python is available
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo Starting Backend API on port 9001...
echo Starting Frontend on port 9002...
echo.
echo ============================================================
echo 📌 URLs:
echo    Frontend: http://localhost:9002
echo    Backend API: http://localhost:9001
echo ============================================================
echo.
echo Press Ctrl+C to stop all servers
echo.

:: Start the backend in background
start "Backend API - Port 9001" cmd /c "cd /d %~dp0 && python app.py"

:: Wait a moment for backend to start
timeout /t 2 /nobreak >nul

:: Start frontend server
cd frontend
python -m http.server 9002
