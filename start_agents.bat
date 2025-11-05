@echo off
REM Quick start script for LiveKit Voice Agents (Windows)

echo 🚀 Starting LiveKit Voice Agent System
echo ======================================
echo.

REM Check if .env exists
if not exist "backend\.env" (
    echo ❌ backend\.env not found!
    echo Please create backend\.env with required credentials:
    echo   OPENAI_API_KEY=...
    echo   LIVEKIT_URL=...
    echo   LIVEKIT_API_KEY=...
    echo   LIVEKIT_API_SECRET=...
    exit /b 1
)

echo ✅ Environment configuration found
echo.

echo Select what to start:
echo 1) All services (4 terminals)
echo 2) Backend API only
echo 3) Dispatcher Agent only
echo 4) Driver Agent only
echo 5) Frontend only
echo.
set /p choice="Enter choice [1-5]: "

if "%choice%"=="1" (
    echo.
    echo 📝 Instructions:
    echo You need to open 4 terminals and run:
    echo.
    echo Terminal 1 (Backend API^):
    echo   cd backend
    echo   .venv\Scripts\activate
    echo   uvicorn src.api.main:app --reload --port 8000
    echo.
    echo Terminal 2 (Dispatcher Agent^):
    echo   cd backend
    echo   .venv\Scripts\activate
    echo   python agents\dispatcher_agent.py
    echo.
    echo Terminal 3 (Driver Agent^):
    echo   cd backend
    echo   .venv\Scripts\activate
    echo   python agents\driver_agent.py
    echo.
    echo Terminal 4 (Frontend^):
    echo   cd frontend
    echo   npm run dev
    echo.
    pause
) else if "%choice%"=="2" (
    cd backend
    call .venv\Scripts\activate
    uvicorn src.api.main:app --reload --port 8000
) else if "%choice%"=="3" (
    cd backend
    call .venv\Scripts\activate
    python agents\dispatcher_agent.py
) else if "%choice%"=="4" (
    cd backend
    call .venv\Scripts\activate
    python agents\driver_agent.py
) else if "%choice%"=="5" (
    cd frontend
    npm run dev
) else (
    echo Invalid choice
    exit /b 1
)

