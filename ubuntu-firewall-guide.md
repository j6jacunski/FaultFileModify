# Ubuntu Firewall Port Configuration Guide

## Overview
Ubuntu uses **UFW (Uncomplicated Firewall)** as the default firewall. This guide shows you how to open ports for your FaultFileModify application.

## Check Firewall Status

First, check if UFW is installed and enabled:

```bash
# Check UFW status
sudo ufw status

# If UFW is not installed, install it
sudo apt update
sudo apt install ufw -y
```

## Method 1: Open Port 49490 for FaultFileModify

### Basic Port Opening
```bash
# Allow port 49490 (TCP)
sudo ufw allow 49490/tcp

# Reload firewall to apply changes
sudo ufw reload

# Verify the rule was added
sudo ufw status numbered
```

### More Specific Rules (Recommended)
```bash
# Allow port 49490 from any IP (for network access)
sudo ufw allow from any to any port 49490 proto tcp

# Or allow from specific network (e.g., local network)
sudo ufw allow from 192.168.1.0/24 to any port 49490 proto tcp
```

## Method 2: Using UFW with Application Profiles

### Create Application Profile
```bash
# Create a profile for your application
sudo nano /etc/ufw/applications.d/faultfilemodify
```

Add this content to the file:
```
[FaultFileModify]
title=FaultFileModify Excel Processor
description=Excel file processing application
ports=49490/tcp
```

### Enable the Application Profile
```bash
# Reload UFW to recognize new profile
sudo ufw app update

# Allow the application
sudo ufw allow FaultFileModify

# Reload firewall
sudo ufw reload
```

## Method 3: Using iptables Directly

If you prefer to use iptables directly:

```bash
# Allow incoming connections on port 49490
sudo iptables -A INPUT -p tcp --dport 49490 -j ACCEPT

# Save the rules (Ubuntu 20.04+)
sudo netfilter-persistent save

# Or for older versions
sudo iptables-save > /etc/iptables/rules.v4
```

## Verify Port is Open

### Check UFW Status
```bash
# View all UFW rules
sudo ufw status verbose

# View numbered rules
sudo ufw status numbered
```

### Test Port Connectivity
```bash
# Test locally
netstat -tuln | grep 49490

# Test from another machine
telnet YOUR_UBUNTU_IP 49490

# Or use nmap
nmap -p 49490 YOUR_UBUNTU_IP
```

### Test Application Access
```bash
# Test health endpoint
curl http://localhost:49490/health

# Test from another machine
curl http://YOUR_UBUNTU_IP:49490/health
```

## Common UFW Commands

### Basic UFW Management
```bash
# Enable UFW
sudo ufw enable

# Disable UFW
sudo ufw disable

# Reset UFW to defaults
sudo ufw reset

# Reload UFW rules
sudo ufw reload
```

### View and Manage Rules
```bash
# View all rules
sudo ufw status

# View rules with numbers
sudo ufw status numbered

# Delete a rule by number
sudo ufw delete 1

# Delete a specific rule
sudo ufw delete allow 49490/tcp
```

### Allow/Deny Rules
```bash
# Allow specific port
sudo ufw allow 49490

# Allow port with protocol
sudo ufw allow 49490/tcp

# Allow from specific IP
sudo ufw allow from 192.168.1.100

# Allow from specific IP to specific port
sudo ufw allow from 192.168.1.100 to any port 49490

# Deny specific port
sudo ufw deny 49490
```

## Troubleshooting

### Check if Port is Actually Open
```bash
# Check listening ports
sudo netstat -tuln | grep 49490

# Check with ss command
sudo ss -tuln | grep 49490

# Check with lsof
sudo lsof -i :49490
```

### Common Issues

#### UFW Not Running
```bash
# Start UFW service
sudo systemctl start ufw
sudo systemctl enable ufw

# Check service status
sudo systemctl status ufw
```

#### Port Still Blocked
```bash
# Check if Docker is binding to the right interface
docker-compose ps

# Check Docker port mappings
docker port faultfilemodify-excel-processor-1
```

#### Application Not Accessible
```bash
# Check if application is running
docker-compose logs

# Check if port is bound correctly
curl http://localhost:49490/health
```

## Security Considerations

### Restrict Access (Recommended)
```bash
# Allow only from local network
sudo ufw allow from 192.168.1.0/24 to any port 49490

# Allow only from specific IPs
sudo ufw allow from 192.168.1.100 to any port 49490
sudo ufw allow from 192.168.1.101 to any port 49490
```

### Monitor Connections
```bash
# View active connections
sudo netstat -tuln | grep 49490

# Monitor UFW logs
sudo tail -f /var/log/ufw.log
```

## Complete Setup for FaultFileModify

Here's the complete sequence to open port 49490 for your application:

```bash
# 1. Check UFW status
sudo ufw status

# 2. Enable UFW if not enabled
sudo ufw enable

# 3. Allow port 49490
sudo ufw allow 49490/tcp

# 4. Reload firewall
sudo ufw reload

# 5. Verify the rule
sudo ufw status

# 6. Test the application
curl http://localhost:49490/health
```

## Quick Commands Reference

```bash
# Open port 49490
sudo ufw allow 49490/tcp && sudo ufw reload

# Check if port is open
sudo ufw status | grep 49490

# Test application
curl http://localhost:49490/health

# Get your IP address
ip addr show | grep "inet " | grep -v 127.0.0.1
```

## Network Access URLs

Once the port is open, your application will be accessible at:
- **Local:** http://localhost:49490
- **Network:** http://YOUR_UBUNTU_IP:49490
- **API Docs:** http://YOUR_UBUNTU_IP:49490/docs
- **Health Check:** http://YOUR_UBUNTU_IP:49490/health
