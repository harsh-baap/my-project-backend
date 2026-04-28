@echo off
REM Startup script for SafeGuard AI Project (Windows)

echo.
echo 🚀 SafeGuard AI - Multi-Threat Detection System
echo =============================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist uploads mkdir uploads
if not exist outputs mkdir outputs
if not exist DataModel\models mkdir DataModel\models

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from .env.example...
    copy .env.example .env
    echo ✏️  Please update .env with your settings
)

REM Build and start services
echo.
echo 🔨 Building Docker images...
docker-compose build --no-cache

echo.
echo 🟢 Starting services...
docker-compose up -d

REM Wait for services
echo.
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak

REM Check health
echo.
echo 🏥 Checking service health...
setlocal enabledelayedexpansion
for /L %%i in (1,1,30) do (
    curl -s http://localhost:5000/api/health >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Detection API is healthy
        goto :health_ok
    )
    timeout /t 1 /nobreak >nul
)
echo ⚠️  Detection API health check timed out
:health_ok

echo.
echo ✅ SafeGuard AI is now running!
echo.
echo 📊 Access Points:
echo   • Frontend: http://localhost:80
echo   • Backend API: http://localhost:3000
echo   • Detection API: http://localhost:5000
echo   • MongoDB: localhost:27017
echo.
echo 📝 View logs:
echo   • docker-compose logs -f
echo.
echo 🛑 To stop all services:
echo   • docker-compose down
echo.
pause
