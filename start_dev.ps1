Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " Starting TraceX Sahyog / CryptoTrace LEA Development Environment" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan

$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "`n[1/2] Starting FastAPI Backend on http://localhost:8765 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir'; & '.\.venv\Scripts\Activate.ps1'; python -m uvicorn app:app --host 0.0.0.0 --port 8765 --reload"

Write-Host "[2/2] Starting Next.js Frontend on http://localhost:3000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir\frontend'; npm run dev"

Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "Both servers launched in dedicated PowerShell windows." -ForegroundColor Green
Write-Host "Backend API & Swagger Docs : http://localhost:8765/docs" -ForegroundColor White
Write-Host "Frontend Application UI    : http://localhost:3000" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Cyan
