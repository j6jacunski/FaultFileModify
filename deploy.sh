#!/bin/bash

# Excel Processor Deployment Script
# Usage: ./deploy.sh user@server:/path/to/deployment

set -e

# Configuration
REMOTE_PATH=${1:-"user@server:/opt/excel-processor"}
LOCAL_PATH="."
DOCKER_COMPOSE_FILE="docker-compose.yml"

echo "🚀 Starting deployment to: $REMOTE_PATH"

# Check if rsync is available
if ! command -v rsync &> /dev/null; then
    echo "❌ rsync is not installed. Please install it first."
    exit 1
fi

# Create remote directory structure
echo "📁 Creating remote directory structure..."
ssh ${REMOTE_PATH%:*} "mkdir -p ${REMOTE_PATH#*:}"

# Transfer files (excluding unnecessary files)
echo "📤 Transferring files..."
rsync -avz --progress \
    --exclude 'node_modules' \
    --exclude 'frontend/build' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.git' \
    --exclude 'uploads/*' \
    --exclude 'outputs/*' \
    --exclude 'history.json' \
    --exclude '.env*' \
    --exclude '*.log' \
    "$LOCAL_PATH/" "$REMOTE_PATH/"

# Create necessary directories on remote
echo "📂 Creating necessary directories..."
ssh ${REMOTE_PATH%:*} "mkdir -p ${REMOTE_PATH#*:}/uploads ${REMOTE_PATH#*:}/outputs"

# Check if Docker is available on remote
echo "🐳 Checking Docker availability..."
if ssh ${REMOTE_PATH%:*} "command -v docker &> /dev/null && command -v docker-compose &> /dev/null"; then
    echo "✅ Docker and Docker Compose found on remote server"
    
    # Build and run with Docker Compose
    echo "🔨 Building and starting application..."
    ssh ${REMOTE_PATH%:*} "cd ${REMOTE_PATH#*:} && docker-compose down || true"
    ssh ${REMOTE_PATH%:*} "cd ${REMOTE_PATH#*:} && docker-compose up -d --build"
    
    # Check if application is running
    echo "🔍 Checking application status..."
    sleep 10
    if ssh ${REMOTE_PATH%:*} "cd ${REMOTE_PATH#*:} && docker-compose ps | grep -q 'Up'"; then
        echo "✅ Application deployed successfully!"
        echo "🌐 Access your application at: http://$(echo ${REMOTE_PATH%:*} | cut -d@ -f2):8000"
    else
        echo "❌ Application failed to start. Check logs with:"
        echo "ssh ${REMOTE_PATH%:*} 'cd ${REMOTE_PATH#*:} && docker-compose logs'"
    fi
else
    echo "⚠️  Docker not found on remote server. Manual setup required."
    echo "📋 Manual setup instructions:"
    echo "1. SSH into the server: ssh ${REMOTE_PATH%:*}"
    echo "2. Navigate to: cd ${REMOTE_PATH#*:}"
    echo "3. Install Docker: https://docs.docker.com/engine/install/"
    echo "4. Run: docker-compose up -d --build"
fi

echo "🎉 Deployment script completed!" 