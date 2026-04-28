@echo off
setlocal

set BACKEND_PORT=3000
set FLASK_PORT=5000
set MONGO_URI=mongodb://127.0.0.1:27017/project

echo.
echo SafeGuard AI (Local) - Starting services
echo Backend: http://127.0.0.1:%BACKEND_PORT%
echo Detection API: http://127.0.0.1:%FLASK_PORT%
echo.

if not exist "venv\Scripts\python.exe" (
  echo [ERROR] Python venv not found.
  echo Create it with:
  echo   python -m venv venv
  echo   venv\Scripts\python.exe -m pip install -r requirements.txt
  exit /b 1
)

echo Starting Detection API...
start "Detection API" cmd /k "set FLASK_PORT=%FLASK_PORT% && set FLASK_DEBUG=False && venv\Scripts\python.exe app.py"

echo Starting Backend...
start "Backend" cmd /k "cd backend && set MONGO_URI=%MONGO_URI% && set SESSION_SECRET=dev_secret && set PYTHON_API_URL=http://127.0.0.1:%FLASK_PORT% && set PORT=%BACKEND_PORT% && npm start"

timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:%BACKEND_PORT%/"

echo.
echo Done. Close the two opened windows to stop services.
echo.
endlocal

