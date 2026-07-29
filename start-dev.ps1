$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
$python = Join-Path $backend ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Backend environment is missing. Create backend/.venv and install backend/requirements.txt first."
}

$backendLog = Join-Path $backend "server.log"
$backendErrorLog = Join-Path $backend "server.error.log"
$frontendLog = Join-Path $frontend "server.log"
$frontendErrorLog = Join-Path $frontend "server.error.log"

Start-Process -FilePath $python `
    -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001" `
    -WorkingDirectory $backend `
    -WindowStyle Hidden `
    -RedirectStandardOutput $backendLog `
    -RedirectStandardError $backendErrorLog

Start-Process -FilePath "npm.cmd" `
    -ArgumentList "run", "dev", "--", "--host", "127.0.0.1" `
    -WorkingDirectory $frontend `
    -WindowStyle Hidden `
    -RedirectStandardOutput $frontendLog `
    -RedirectStandardError $frontendErrorLog

Write-Output "Frontend: http://127.0.0.1:5173"
Write-Output "Backend docs: http://127.0.0.1:8001/docs"
