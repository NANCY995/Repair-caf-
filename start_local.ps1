# Script de démarrage local du serveur BUTUS WhatsApp Bot
Write-Host "==========================================" -ForegroundColor Green
Write-Host "🚀 Démarrage de BUTUS Repair (Local)" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

$backendDir = Join-Path $PSScriptRoot "mvp-alternative\backend\whatsapp_bot"
if (-not (Test-Path $backendDir)) {
    $backendDir = $PSScriptRoot
}
Set-Location $backendDir

# Ouvrir le navigateur
Start-Process "http://127.0.0.1:8000/test"
Start-Process "http://127.0.0.1:8000/dashboard"

Write-Host "🌐 Serveur : http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "📱 Simulateur Web : http://127.0.0.1:8000/test" -ForegroundColor Cyan
Write-Host "📊 Dashboard : http://127.0.0.1:8000/dashboard" -ForegroundColor Cyan
Write-Host "🔑 Identifiant / Token admin : butus_admin_token_2026" -ForegroundColor Yellow

python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
