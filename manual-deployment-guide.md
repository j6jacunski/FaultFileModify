# Manual Deployment Guide

## Prerequisites

1. **SSH access** to your remote server
2. **Docker** installed on the server
3. **Docker Compose** installed on the server

## Step 1: Connect to Your Server

```bash
ssh username@your-server-ip
```

## Step 2: Install Docker (if not installed)

### Ubuntu/Debian:
```bash
# Update package list
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker
```

### CentOS/RHEL:
```bash
# Install Docker
sudo yum install -y docker

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
```

## Step 3: Install Docker Compose

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

## Step 4: Clone Your Repository

```bash
# Create project directory
mkdir -p ~/FaultFileModify
cd ~/FaultFileModify

# Clone from git
git clone https://github.com/j6jacunski/FaultFileModify.git .
```

## Step 5: Deploy the Application

```bash
# Build and start containers
docker-compose up -d --build

# Check container status
docker-compose ps

# View logs
docker-compose logs -f
```

## Step 6: Configure Firewall

### Ubuntu/Debian (UFW):
```bash
sudo ufw allow 49490/tcp
sudo ufw reload
```

### CentOS/RHEL (firewalld):
```bash
sudo firewall-cmd --permanent --add-port=49490/tcp
sudo firewall-cmd --reload
```

### iptables:
```bash
sudo iptables -A INPUT -p tcp --dport 49490 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

## Step 7: Test the Deployment

```bash
# Test locally on server
curl http://localhost:49490/health

# Test from your local machine
curl http://your-server-ip:49490/health
```

## Step 8: Access Your Application

- **Main App:** http://your-server-ip:49490
- **API Docs:** http://your-server-ip:49490/docs
- **Health Check:** http://your-server-ip:49490/health

## Troubleshooting

### Check Container Status:
```bash
docker-compose ps
docker-compose logs
```

### Restart Containers:
```bash
docker-compose down
docker-compose up -d
```

### Check Port Binding:
```bash
netstat -tuln | grep 49490
```

### Check Firewall:
```bash
# UFW
sudo ufw status

# firewalld
sudo firewall-cmd --list-ports

# iptables
sudo iptables -L -n
```

## Updating the Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

## Security Considerations

1. **Use HTTPS** in production (nginx + Let's Encrypt)
2. **Set up a reverse proxy** (nginx/Apache)
3. **Configure proper firewall rules**
4. **Use environment variables** for sensitive data
5. **Regular security updates**

## Performance Optimization

1. **Use a reverse proxy** (nginx) for better performance
2. **Enable gzip compression**
3. **Set up caching headers**
4. **Monitor resource usage**
5. **Use Docker volumes** for persistent data
