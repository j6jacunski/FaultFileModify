# Ubuntu Setup Commands

## Prerequisites
Make sure you have the following installed on your Ubuntu PC:
- Git
- Docker
- Docker Compose

## Step 1: Install Prerequisites (if not already installed)

### Install Git:
```bash
sudo apt update
sudo apt install git -y
```

### Install Docker:
```bash
# Remove old versions if any
sudo apt remove docker docker-engine docker.io containerd runc

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Log out and back in, or run this to apply group changes:
newgrp docker
```

### Install Docker Compose:
```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

## Step 2: Clone the Repository

```bash
# Navigate to your desired directory
cd ~

# Clone the repository
git clone https://github.com/j6jacunski/FaultFileModify.git

# Navigate into the project directory
cd FaultFileModify

# Verify the files are present
ls -la
```

## Step 3: Build and Run the Application

```bash
# Build and start the containers
docker-compose up -d --build

# Check if containers are running
docker-compose ps

# View logs to ensure everything started correctly
docker-compose logs --tail=20
```

## Step 4: Access the Application

Once the containers are running, you can access the application at:

- **Main Application:** http://localhost:49490
- **API Documentation:** http://localhost:49490/docs
- **Health Check:** http://localhost:49490/health

## Step 5: Test the Application

```bash
# Test health endpoint
curl http://localhost:49490/health

# Test main application
curl http://localhost:49490/
```

## Useful Commands

### View Container Status:
```bash
docker-compose ps
```

### View Logs:
```bash
# View all logs
docker-compose logs

# View last 20 lines
docker-compose logs --tail=20

# Follow logs in real-time
docker-compose logs -f
```

### Stop the Application:
```bash
docker-compose down
```

### Restart the Application:
```bash
docker-compose down
docker-compose up -d
```

### Rebuild and Restart:
```bash
docker-compose down
docker-compose up -d --build
```

### View Container Resources:
```bash
docker stats
```

## Troubleshooting

### If Docker permission errors occur:
```bash
# Log out and back in, or run:
newgrp docker
```

### If port 49490 is already in use:
```bash
# Check what's using the port
sudo netstat -tuln | grep 49490

# Kill the process if needed
sudo lsof -ti:49490 | xargs kill -9
```

### If containers fail to start:
```bash
# Check detailed logs
docker-compose logs

# Check Docker daemon status
sudo systemctl status docker
```

### Clean up if needed:
```bash
# Stop and remove containers
docker-compose down

# Remove all unused containers, networks, and images
docker system prune -a

# Remove specific images
docker rmi faultfilemodify-excel-processor
```

## Network Access (Optional)

If you want to access the application from other devices on your network:

```bash
# Get your Ubuntu PC's IP address
ip addr show | grep "inet " | grep -v 127.0.0.1

# Access from other devices using:
# http://YOUR_UBUNTU_IP:49490
```

## Firewall Configuration (if needed)

```bash
# Allow port 49490 through UFW firewall
sudo ufw allow 49490/tcp
sudo ufw reload

# Check firewall status
sudo ufw status
```

## Update the Application

To get the latest changes from the repository:

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

## Complete One-Liner Setup

If you want to run everything in one go (after installing Docker and Docker Compose):

```bash
cd ~ && \
git clone https://github.com/j6jacunski/FaultFileModify.git && \
cd FaultFileModify && \
docker-compose up -d --build && \
echo "Application is starting... Check http://localhost:49490 in a few moments"
```
