#!/bin/bash

# Ubuntu Quick Setup Script for FaultFileModify
# Run this script to quickly set up the application on Ubuntu

set -e

echo "🚀 Setting up FaultFileModify on Ubuntu..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root. Run as a regular user."
    exit 1
fi

# Step 1: Check and install prerequisites
print_status "Checking prerequisites..."

# Check if Git is installed
if ! command -v git &> /dev/null; then
    print_status "Installing Git..."
    sudo apt update
    sudo apt install git -y
    print_success "Git installed successfully"
else
    print_success "Git is already installed"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    sudo systemctl start docker
    sudo systemctl enable docker
    print_success "Docker installed successfully"
    print_warning "You may need to log out and back in for Docker permissions to take effect"
else
    print_success "Docker is already installed"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_status "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose installed successfully"
else
    print_success "Docker Compose is already installed"
fi

# Step 2: Clone repository
print_status "Cloning repository..."
if [ -d "FaultFileModify" ]; then
    print_warning "FaultFileModify directory already exists. Updating..."
    cd FaultFileModify
    git pull origin main
else
    git clone https://github.com/j6jacunski/FaultFileModify.git
    cd FaultFileModify
fi
print_success "Repository cloned/updated successfully"

# Step 3: Check if Docker daemon is running
print_status "Checking Docker daemon..."
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running. Please start Docker and try again."
    print_status "You can start Docker with: sudo systemctl start docker"
    exit 1
fi
print_success "Docker daemon is running"

# Step 4: Build and start application
print_status "Building and starting application..."
docker-compose up -d --build

# Step 5: Wait for containers to be ready
print_status "Waiting for containers to be ready..."
sleep 10

# Step 6: Check container status
print_status "Checking container status..."
if docker-compose ps | grep -q "Up"; then
    print_success "Containers are running successfully"
else
    print_error "Containers failed to start. Check logs with: docker-compose logs"
    exit 1
fi

# Step 7: Test application
print_status "Testing application..."
if curl -s http://localhost:49490/health > /dev/null; then
    print_success "Application is accessible"
else
    print_warning "Application may still be starting up. Please wait a moment and try again."
fi

# Step 8: Display access information
echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Access URLs:"
echo "   Main Application: http://localhost:49490"
echo "   API Documentation: http://localhost:49490/docs"
echo "   Health Check: http://localhost:49490/health"
echo ""
echo "🔧 Useful Commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop app: docker-compose down"
echo "   Restart app: docker-compose up -d"
echo "   Update app: git pull origin main && docker-compose up -d --build"
echo ""
echo "🌐 Network Access:"
echo "   To access from other devices, use: http://$(hostname -I | awk '{print $1}'):49490"
echo ""

print_success "Setup completed! Open http://localhost:49490 in your browser."
