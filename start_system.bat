@echo off
title SentinelAI - Unified Surveillance Workstation Launcher
echo ======================================================================
echo   SENTINELAI - QUALITY-AWARE INTELLIGENT BORDER SURVEILLANCE PLATFORM
echo   Unified Launch: Backend (FastAPI) + Database (SQLite) + Frontend (Vite)
echo ======================================================================
echo.

cd /d "%~dp0backend"
echo [1/3] Initializing SQLite Database Schema & Indexes...
python -c "from database.schema import Schema; Schema().create_tables(); print('      Database ready at: backend/database/sentinel.db')"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to initialize database schema.
    pause
    exit /b 1
)

echo.
echo [2/3] Starting FastAPI Backend on http://127.0.0.1:8000...
start "SentinelAI Backend API" cmd /k "cd /d %~dp0backend && python -m uvicorn api.app:app --host 127.0.0.1 --port 8000"

timeout /t 2 /nobreak >nul

echo.
echo [3/3] Starting Frontend Workstation on http://localhost:5173...
cd /d "%~dp0frontend"
start "SentinelAI Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ======================================================================
echo   ALL SYSTEMS ONLINE AND FULLY INTEGRATED:
echo     - Frontend Workstation : http://localhost:5173
echo     - Backend API Engine   : http://127.0.0.1:8000
echo     - API Documentation    : http://127.0.0.1:8000/docs
echo     - Database Storage     : %~dp0backend\database\sentinel.db (WAL Mode)
echo ======================================================================
echo.
pause
