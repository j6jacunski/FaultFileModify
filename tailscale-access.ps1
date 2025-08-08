# Tailscale Remote Access Script for Excel Processor
# Run this script to get your Tailscale IP and access URLs

Write-Host "🔗 Setting up Tailscale Remote Access..." -ForegroundColor Green

# Check if Tailscale is running
try {
    $tailscaleIP = tailscale ip
    if ($tailscaleIP) {
        Write-Host "✅ Tailscale is running" -ForegroundColor Green
        Write-Host "🌐 Your Tailscale IP: $tailscaleIP" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Tailscale IP not found. Is Tailscale running?" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Tailscale is not running. Please start Tailscale first." -ForegroundColor Red
    Write-Host "💡 Install from: https://tailscale.com/download" -ForegroundColor Yellow
    exit 1
}

# Check if Docker container is running
try {
    $containerStatus = docker ps --filter "name=excel-processor" --format "table {{.Names}}\t{{.Status}}"
    if ($containerStatus -like "*excel-processor*") {
        Write-Host "✅ Docker container is running" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Docker container not found. Starting it..." -ForegroundColor Yellow
        docker compose up -d
        Start-Sleep -Seconds 5
    }
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Display access URLs
Write-Host "`n🌐 Remote Access URLs:" -ForegroundColor Yellow
Write-Host "   Main Application: http://$tailscaleIP:8000" -ForegroundColor Cyan
Write-Host "   API Documentation: http://$tailscaleIP:8000/docs" -ForegroundColor Cyan
Write-Host "   Health Check: http://$tailscaleIP:8000/health" -ForegroundColor Cyan

Write-Host "`n📱 Access from any device on your Tailscale network:" -ForegroundColor Green
Write-Host "   • Mobile phone" -ForegroundColor White
Write-Host "   • Tablet" -ForegroundColor White
Write-Host "   • Other computers" -ForegroundColor White
Write-Host "   • Any device with Tailscale installed" -ForegroundColor White

Write-Host "`n🔒 Security Notes:" -ForegroundColor Yellow
Write-Host "   • Only devices on your Tailscale network can access this" -ForegroundColor White
Write-Host "   • No need to open firewall ports" -ForegroundColor White
Write-Host "   • Traffic is encrypted end-to-end" -ForegroundColor White

Write-Host "`n🎉 Your Excel Processor is now accessible remotely!" -ForegroundColor Green
Write-Host "   Share this IP with your team: $tailscaleIP" -ForegroundColor Cyan 