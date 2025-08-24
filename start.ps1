# PowerShell launcher for Windows users
# Usage: Right-click and "Run with PowerShell" or: pwsh -ExecutionPolicy Bypass -File .\start.ps1

param(
  [switch]$UIOnly
)

Write-Host "🚀 Starting OSS Community Agent (Windows)" -ForegroundColor Cyan

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

# Detect Python
$python = $null
try {
  $python = & py -3 --version 2>$null | Out-Null; 'py -3'
} catch {}
if (-not $python) {
  try { $python = & python --version 2>$null | Out-Null; 'python' } catch {}
}
if (-not $python) {
  Write-Error "Python not found. Please install Python 3 and ensure it is in PATH."
  exit 1
}

# Create .env from example if missing
if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
  Copy-Item .env.example .env
  Write-Warning "Created .env from .env.example. Edit it with your credentials before running."
}

# Install dependencies if streamlit is missing
$streamlitCheck = & $python -c "import importlib, sys; sys.exit(0 if importlib.util.find_spec('streamlit') else 1)"
if ($LASTEXITCODE -ne 0) {
  Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
  & $python -m pip install -r infra/requirements.txt
}

if ($UIOnly) {
  Push-Location apps/ui
  & $python -m streamlit run streamlit_app.py --server.port 8501 --server.address localhost --browser.gatherUsageStats false
  Pop-Location
} else {
  & $python run_full_system.py
}

