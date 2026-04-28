param(
  [int]$BackendPort = 3000,
  [int]$FlaskPort = 5000,
  [string]$MongoUri = "mongodb://127.0.0.1:27017/project"
)

$ErrorActionPreference = "Stop"

function Test-PortInUse {
  param([int]$Port)
  try {
    $c = Get-NetTCPConnection -LocalPort $Port -ErrorAction Stop | Select-Object -First 1
    return $true
  } catch {
    return $false
  }
}

Write-Host ""
Write-Host "SafeGuard AI (Local) - Starting services"
Write-Host "Backend: http://127.0.0.1:$BackendPort"
Write-Host "Detection API: http://127.0.0.1:$FlaskPort"
Write-Host ""

if (!(Test-Path ".\venv\Scripts\python.exe")) {
  throw "Python venv not found. Create it first: python -m venv venv ; .\venv\Scripts\python.exe -m pip install -r requirements.txt"
}

if (Test-PortInUse -Port $FlaskPort) {
  throw "Port $FlaskPort already in use. Stop the process and retry."
}
if (Test-PortInUse -Port $BackendPort) {
  throw "Port $BackendPort already in use. Stop the process and retry."
}

Write-Host "Starting Detection API..."
Start-Process -WindowStyle Normal -FilePath ".\venv\Scripts\python.exe" -ArgumentList "app.py" -WorkingDirectory (Get-Location) | Out-Null

Write-Host "Starting Backend..."
$backendArgs = @(
  "-NoExit",
  "-Command",
  "`$env:MONGO_URI='$MongoUri'; `$env:SESSION_SECRET='dev_secret'; `$env:PYTHON_API_URL='http://127.0.0.1:$FlaskPort'; `$env:PORT=$BackendPort; npm start"
)
Start-Process -WindowStyle Normal -FilePath "powershell.exe" -ArgumentList $backendArgs -WorkingDirectory (Join-Path (Get-Location) "backend") | Out-Null

Start-Sleep -Seconds 2
Write-Host "Opening browser..."
Start-Process "http://127.0.0.1:$BackendPort/"

Write-Host ""
Write-Host "Done. Close the two opened windows to stop services."

