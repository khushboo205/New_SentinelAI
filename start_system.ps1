# SentinelAI Unified System Launcher (PowerShell)
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  SENTINELAI - QUALITY-AWARE INTELLIGENT BORDER SURVEILLANCE PLATFORM" -ForegroundColor White
Write-Host "  Unified Integration: Backend (FastAPI) + Database (SQLite) + Frontend" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$RootPath = $PSScriptRoot
if (-not $RootPath) { $RootPath = Get-Location }

# 1. Initialize Database
Write-Host "`n[1/3] Verifying SQLite Database Schema & Migrations..." -ForegroundColor Yellow
Set-Location "$RootPath\backend"
python -c "from database.schema import Schema; Schema().create_tables(); print('      Database ready at: backend/database/sentinel.db')"

# 2. Start Backend API
Write-Host "`n[2/3] Launching FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootPath\backend'; python -m uvicorn api.app:app --host 127.0.0.1 --port 8000"

Start-Sleep -Seconds 2

# 3. Start Frontend Dev Server
Write-Host "`n[3/3] Launching Frontend Workstation on http://localhost:5173..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootPath\frontend'; npm run dev"

Write-Host "`n======================================================================" -ForegroundColor Green
Write-Host "  ALL SYSTEMS ONLINE AND FULLY INTEGRATED:" -ForegroundColor White
Write-Host "    - Frontend Workstation : http://localhost:5173" -ForegroundColor Cyan
Write-Host "    - Backend API Engine   : http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "    - Interactive API Docs : http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "    - SQLite Database      : $RootPath\backend\database\sentinel.db (WAL)" -ForegroundColor Cyan
Write-Host "======================================================================`n" -ForegroundColor Green
