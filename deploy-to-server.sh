#!/bin/bash

# Deploy Excel Processor to Remote Server
# Usage: ./deploy-to-server.sh [server_ip] [username]

set -e

# Configuration
SERVER_IP=${1:-"YOUR_SERVER_IP"}
USERNAME=${2:-"YOUR_USERNAME"}
PROJECT_NAME="FaultFileModify"
REMOTE_DIR="/home/$USERNAME/$PROJECT_NAME"

echo "🚀 Deploying Excel Processor to $SERVER_IP..."

# Check if server IP is provided
if [ "$SERVER_IP" = "YOUR_SERVER_IP" ]; then
    echo "❌ Please provide your server IP:"
    echo "   ./deploy-to-server.sh YOUR_SERVER_IP [username]"
    exit 1
fi

# Test server connectivity
echo "🔍 Testing server connectivity..."
if ! ping -c 1 $SERVER_IP > /dev/null 2>&1; then
    echo "❌ Cannot reach server $SERVER_IP"
    exit 1
fi

# Create remote directory
echo "📁 Creating remote directory..."
ssh $USERNAME@$SERVER_IP "mkdir -p $REMOTE_DIR"

# Copy project files (excluding unnecessary files)
echo "📤 Copying project files..."
rsync -avz --exclude='.git' \
    --exclude='node_modules' \
    --exclude='uploads/*' \
    --exclude='outputs/*' \
    --exclude='*.log' \
    --exclude='.env' \
    ./ $USERNAME@$SERVER_IP:$REMOTE_DIR/

# SSH into server and deploy
echo "🔧 Deploying on remote server..."
ssh $USERNAME@$SERVER_IP << EOF
    cd $REMOTE_DIR
    
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
    sleep 10
    
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
    echo ""
    echo "🔒 To open firewall ports, run:"
    echo "   sudo ufw allow 49490/tcp  # Ubuntu/Debian"
    echo "   sudo firewall-cmd --permanent --add-port=49490/tcp  # CentOS/RHEL"
EOF

echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Your application is now accessible at:"
echo "   http://$SERVER_IP:49490"
