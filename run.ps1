# FRES Web - Quick Run Script
# Run this script to start the server locally

$ErrorActionPreference = "Stop"

Write-Host "Starting FRES Web Server..." -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "`nWARNING: .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env with your OpenRouter API key:" -ForegroundColor Yellow
    Write-Host "  OPENROUTER_API_KEY=your-api-key-here" -ForegroundColor Gray
    Write-Host "  OPENROUTER_MODEL=openrouter/auto" -ForegroundColor Gray
    Write-Host "  OPENROUTER_BASE_URL=https://openrouter.ai/api/v1" -ForegroundColor Gray
    Write-Host ""
    $createEnv = Read-Host "Create .env.example file? (y/n)"
    if ($createEnv -eq "y") {
        "@"
        "OPENROUTER_API_KEY=sk-or-v1-your-key-here"
        "OPENROUTER_MODEL=openrouter/auto"
        "OPENROUTER_BASE_URL=https://openrouter.ai/api/v1" | Out-File -FilePath ".env.example" -Encoding utf8
        Write-Host ".env.example created!" -ForegroundColor Green
    }
    exit 1
}

# Check for API key
$envContent = Get-Content ".env" -Raw
if ($envContent -notmatch "OPENROUTER_API_KEY=sk-or-v1") {
    Write-Host "`nWARNING: OPENROUTER_API_KEY not set in .env!" -ForegroundColor Red
    Write-Host "Get your free API key at: https://openrouter.ai" -ForegroundColor Yellow
    exit 1
}

# Start server
Write-Host "`nStarting server at http://127.0.0.1:5000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

python server.py