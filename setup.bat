@echo off
REM Setup script for SafeGuard AI Project (Windows)

echo.
echo 🚀 SafeGuard AI - Setup Script
echo ==============================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 is required but not installed.
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ %PYTHON_VERSION%

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo 📦 Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create directories
echo 📁 Creating directories...
if not exist uploads mkdir uploads
if not exist outputs mkdir outputs
if not exist DataModel\models mkdir DataModel\models

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Node.js is required but not installed.
    echo    Download from: https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node %NODE_VERSION%

REM Install backend dependencies
if exist "backend" (
    echo 📦 Installing backend dependencies...
    cd backend
    call npm install
    cd ..
)

REM Create .env if doesn't exist
if not exist ".env" (
    echo 🔧 Configuration...
    copy .env.example .env
    echo ✏️  Created .env - Please update with your configuration
)

echo.
echo ✅ Setup complete!
echo.
echo 📝 Next steps:
echo 1. Update .env configuration file
echo 2. Run 'docker-compose up -d' to start services
echo 3. Or run 'python app.py' for Python API only
echo.
pause
