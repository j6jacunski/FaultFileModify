#!/bin/bash

# Git-based deployment for Excel Processor
# This script pulls from git and deploys on the remote server

set -e

# Configuration
SERVER_IP=${1:-"YOUR_SERVER_IP"}
USERNAME=${2:-"YOUR_USERNAME"}
GIT_REPO="https://github.com/j6jacunski/FaultFileModify.git"
REMOTE_DIR="/home/$USERNAME/FaultFileModify"

echo "🚀 Deploying via Git to $SERVER_IP..."

# Check if server IP is provided
if [ "$SERVER_IP" = "YOUR_SERVER_IP" ]; then
    echo "❌ Please provide your server IP:"
    echo "   ./deploy-via-git.sh YOUR_SERVER_IP [username]"
    exit 1
fi

# SSH into server and deploy
echo "🔧 Deploying on remote server..."
ssh $USERNAME@$SERVER_IP << EOF
    # Create directory if it doesn't exist
    mkdir -p $REMOTE_DIR
    cd $REMOTE_DIR
    
    # Clone or pull from git
    if [ -d ".git" ]; then
        echo "📥 Pulling latest changes..."
        git pull origin main
    else
        echo "📥 Cloning repository..."
        git clone $GIT_REPO .
    fi
    
    # Install Docker if not present
    if ! command -v docker &> /dev/null; then
        echo "🐳 Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker \$USER
        echo "✅ Docker installed. Please log out and back in to use Docker without sudo."
    fi
    
    # Install Docker Compose if not present
    if ! command -v docker-compose &> /dev/null; then
        echo "📦 Installing Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
    
    # Stop existing containers
    echo "🛑 Stopping existing containers..."
    docker-compose down 2>/dev/null || true
    
    # Build and start containers
    echo "🔨 Building and starting containers..."
    docker-compose up -d --build
    
    # Wait for containers to be ready
    echo "⏳ Waiting for containers to be ready..."
    sleep 15
    
    # Check container status
    echo "📊 Container status:"
    docker-compose ps
    
    # Show access information
    echo ""
    echo "🎉 Deployment complete!"
    echo "📋 Access URLs:"
    echo "   Local: http://localhost:49490"
    echo "   Network: http://$SERVER_IP:49490"
    echo "   API Docs: http://$SERVER_IP:49490/docs"
EOF

echo "✅ Git-based deployment completed successfully!"
echo ""
echo "🌐 Your application is now accessible at:"
echo "   http://$SERVER_IP:49490"
echo ""
echo "💡 For future updates, just push to git and run this script again!"
