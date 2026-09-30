@echo off
echo ======================================================================
echo  Starting TraceX Sahyog / CryptoTrace LEA Development Environment
echo ======================================================================

echo [1/2] Starting FastAPI Backend on http://localhost:8765 ...
start "CryptoTrace Backend" cmd /k "cd /d "%~dp0" && .venv\Scripts\activate && python -m uvicorn app:app --host 0.0.0.0 --port 8765 --reload"

echo [2/2] Starting Next.js Frontend on http://localhost:3000 ...
start "CryptoTrace Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo ======================================================================
echo Both servers are starting in separate windows.
echo Backend Docs: http://localhost:8765/docs
echo Frontend UI : http://localhost:3000
echo ======================================================================
