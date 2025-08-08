# Proxmox Firewall Configuration for FaultFileModify

## Overview
When running Ubuntu on Proxmox, you need to configure the Proxmox firewall to allow traffic to reach your Ubuntu VM on port 49490.

## Step 1: Check Proxmox Firewall Status

First, check if the Proxmox firewall is enabled:

```bash
# SSH into your Proxmox host
ssh root@YOUR_PROXMOX_IP

# Check firewall status
pve-firewall status
```

## Step 2: Configure Proxmox Firewall

### Method 1: Using Proxmox Web Interface (Recommended)

1. **Access Proxmox Web Interface:**
   - Open browser and go to: `https://YOUR_PROXMOX_IP:8006`
   - Login with your credentials

2. **Navigate to Firewall Settings:**
   - Select your **Datacenter** in the left panel
   - Click on **Firewall** tab
   - Click **Options** → **Firewall** → **Enable**

3. **Add Firewall Rule:**
   - Click **Add** → **Security Group**
   - Name: `FaultFileModify`
   - Description: `Excel Processor Application`
   - Click **Create**

4. **Add Port Rule:**
   - Select the **FaultFileModify** security group
   - Click **Add** → **Rule**
   - **Action:** Accept
   - **Protocol:** TCP
   - **Source:** Any (or specific IP range)
   - **Destination Port:** 49490
   - **Comment:** `FaultFileModify Excel Processor`
   - Click **Add**

5. **Apply to VM:**
   - Go to your Ubuntu VM
   - Click **Firewall** tab
   - Click **Add** → **Security Group**
   - Select **FaultFileModify**
   - Click **Add**

### Method 2: Using Command Line

```bash
# SSH into Proxmox host
ssh root@YOUR_PROXMOX_IP

# Create security group
pve-firewall security-group create FaultFileModify

# Add rule to security group
pve-firewall security-group rule add FaultFileModify \
  --action accept \
  --protocol tcp \
  --dest-port 49490 \
  --comment "FaultFileModify Excel Processor"

# Apply security group to VM (replace VMID with your VM's ID)
pve-firewall security-group add FaultFileModify VMID
```

## Step 3: Configure VM Network Settings

### Check VM Network Configuration

1. **In Proxmox Web Interface:**
   - Select your Ubuntu VM
   - Click **Hardware** tab
   - Check the **Network Device** settings

2. **Verify Network Bridge:**
   - Make sure the VM is connected to the correct bridge (usually `vmbr0`)
   - Check that the bridge has access to your network

### Configure VM Network (if needed)

```bash
# Edit VM network configuration
nano /etc/pve/qemu-server/VMID.conf

# Add or modify network line:
# net0: virtio=XX:XX:XX:XX:XX:XX,bridge=vmbr0,firewall=1
```

## Step 4: Configure Ubuntu VM Firewall

Inside your Ubuntu VM, you still need to configure UFW:

```bash
# SSH into your Ubuntu VM
ssh username@YOUR_UBUNTU_VM_IP

# Open port 49490
sudo ufw allow 49490/tcp
sudo ufw reload

# Verify
sudo ufw status
```

## Step 5: Test Connectivity

### From Proxmox Host
```bash
# Test from Proxmox host to VM
curl http://YOUR_UBUNTU_VM_IP:49490/health
```

### From External Network
```bash
# Test from another machine on your network
curl http://YOUR_PROXMOX_IP:49490/health
```

## Step 6: Port Forwarding (if needed)

If you want to access the application using the Proxmox host IP instead of the VM IP:

### Using Proxmox Web Interface
1. Go to **Datacenter** → **Firewall**
2. Click **Add** → **Rule**
3. **Action:** Accept
4. **Protocol:** TCP
5. **Source:** Any
6. **Destination Port:** 49490
7. **Comment:** `FaultFileModify Port Forward`
8. Click **Add**

### Using Command Line
```bash
# Add port forwarding rule
pve-firewall rule add \
  --action accept \
  --protocol tcp \
  --dest-port 49490 \
  --comment "FaultFileModify Port Forward"
```

## Troubleshooting

### Check Proxmox Firewall Rules
```bash
# View all firewall rules
pve-firewall status

# View security groups
pve-firewall security-group list

# View rules for specific security group
pve-firewall security-group rule list FaultFileModify
```

### Check VM Network
```bash
# Check VM network configuration
cat /etc/pve/qemu-server/VMID.conf

# Check bridge status
ip link show vmbr0

# Check bridge firewall
pve-firewall status vmbr0
```

### Test Network Connectivity
```bash
# Test from Proxmox to VM
ping YOUR_UBUNTU_VM_IP

# Test port connectivity
telnet YOUR_UBUNTU_VM_IP 49490

# Check if port is listening on VM
ssh username@YOUR_UBUNTU_VM_IP "netstat -tuln | grep 49490"
```

### Common Issues

#### VM Not Accessible
```bash
# Check if VM firewall is enabled
pve-firewall status VMID

# Check VM network bridge
pve-firewall status vmbr0

# Restart VM network
qm reset VMID
```

#### Port Still Blocked
```bash
# Check Proxmox firewall logs
tail -f /var/log/pve-firewall.log

# Check if security group is applied
pve-firewall security-group list VMID
```

#### Application Not Responding
```bash
# Check if application is running in VM
ssh username@YOUR_UBUNTU_VM_IP "docker-compose ps"

# Check application logs
ssh username@YOUR_UBUNTU_VM_IP "docker-compose logs"
```

## Complete Setup Checklist

- [ ] Proxmox firewall enabled
- [ ] Security group created for FaultFileModify
- [ ] Port 49490 rule added to security group
- [ ] Security group applied to Ubuntu VM
- [ ] Ubuntu VM UFW configured (port 49490 open)
- [ ] Application running in Docker container
- [ ] Network connectivity tested

## Access URLs

Once configured, your application will be accessible at:
- **VM IP:** http://YOUR_UBUNTU_VM_IP:49490
- **Proxmox IP (if port forwarded):** http://YOUR_PROXMOX_IP:49490
- **API Docs:** http://YOUR_IP:49490/docs
- **Health Check:** http://YOUR_IP:49490/health

## Security Considerations

### Restrict Access (Recommended)
```bash
# Allow only from specific IP ranges
pve-firewall security-group rule add FaultFileModify \
  --action accept \
  --protocol tcp \
  --dest-port 49490 \
  --source 192.168.1.0/24 \
  --comment "FaultFileModify - Local Network Only"
```

### Monitor Traffic
```bash
# View firewall logs
tail -f /var/log/pve-firewall.log

# View VM firewall logs
ssh username@YOUR_UBUNTU_VM_IP "sudo tail -f /var/log/ufw.log"
```
