# Excel Processor Docker Desktop Setup Script for Windows
# Run this script in PowerShell to clone and run your application
# Note: Uses 'docker compose' (newer Docker Desktop versions)

Write-Host "🐳 Setting up Excel Processor in Docker Desktop..." -ForegroundColor Green

# Check if Docker Desktop is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker Desktop is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Desktop is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Clone repository if not exists
if (-not (Test-Path "FaultFileModify")) {
    Write-Host "📥 Cloning repository..." -ForegroundColor Yellow
    git clone https://github.com/j6jacunski/FaultFileModify.git
}

# Navigate to the project directory
Set-Location FaultFileModify

# Build the Docker image
Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
docker build -t excel-processor .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker image built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}

# Stop and remove existing container if it exists
Write-Host "🔄 Stopping existing container..." -ForegroundColor Yellow
docker stop excel-processor 2>$null
docker rm excel-processor 2>$null

# Run the container
Write-Host "🚀 Starting container..." -ForegroundColor Yellow
docker run -d `
    --name excel-processor `
    -p 8000:8000 `
    -v "${PWD}\uploads:/app/uploads" `
    -v "${PWD}\outputs:/app/outputs" `
    --restart unless-stopped `
    excel-processor

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Excel Processor is running!" -ForegroundColor Green
    Write-Host "🌐 Access at: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "📊 Docker Desktop: Check the 'Containers' tab" -ForegroundColor Cyan
    Write-Host "📋 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to start container" -ForegroundColor Red
    exit 1
}

# Show container status
Write-Host "`n📊 Container Status:" -ForegroundColor Yellow
docker ps --filter "name=excel-processor"

Write-Host "`n🎉 Setup complete! Your Excel Processor is ready to use." -ForegroundColor Green 