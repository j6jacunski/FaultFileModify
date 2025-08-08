# Docker Desktop Setup Guide

## 🐳 **Using Docker Desktop to Clone and Run Your Excel Processor**

### **Option 1: Clone and Build via Docker Desktop**

1. **Open Docker Desktop**
2. **Go to "Containers" tab**
3. **Click "New Container"**
4. **Use this configuration:**

```bash
# Base image (for cloning)
Image: alpine/git:latest

# Command to run:
git clone https://github.com/j6jacunski/FaultFileModify.git /app && \
cd /app && \
docker build -t excel-processor . && \
docker run -d -p 8000:8000 -v /app/uploads:/app/uploads -v /app/outputs:/app/outputs excel-processor
```

### **Option 2: Local Clone + Docker Desktop Build**

#### **Step 1: Clone Repository**
```bash
# Open terminal/command prompt
git clone https://github.com/j6jacunski/FaultFileModify.git
cd FaultFileModify
```

#### **Step 2: Build in Docker Desktop**
1. **Open Docker Desktop**
2. **Go to "Images" tab**
3. **Click "Build"**
4. **Set build context to your cloned directory**
5. **Dockerfile path: `./Dockerfile`**
6. **Image name: `excel-processor`**
7. **Click "Build"**

#### **Step 3: Run Container**
1. **Go to "Containers" tab**
2. **Click "Run" on your `excel-processor` image**
3. **Set port mapping: `8000:8000`**
4. **Add volumes:**
   - `./uploads:/app/uploads`
   - `./outputs:/app/outputs`
5. **Click "Run"**

### **Option 3: Using Docker Compose in Docker Desktop**

#### **Step 1: Clone and Setup**
```bash
git clone https://github.com/j6jacunski/FaultFileModify.git
cd FaultFileModify
```

#### **Step 2: Use Docker Compose**
1. **Open Docker Desktop**
2. **Go to "Containers" tab**
3. **Click "New Container"**
4. **Use this configuration:**

```bash
# Image: docker/compose:latest
# Command:
-f /app/docker-compose.yml up -d
```

5. **Mount your local directory as a volume:**
   - Source: `C:\Users\User\Documents\Automation\FaultFileListings\FaultFileModify`
   - Target: `/app`

### **Option 4: Quick Docker Desktop Script**

Create a file called `docker-desktop-run.sh`:

```bash
#!/bin/bash
echo "🐳 Setting up Excel Processor in Docker Desktop..."

# Clone repository if not exists
if [ ! -d "FaultFileModify" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/j6jacunski/FaultFileModify.git
fi

cd FaultFileModify

# Build the image
echo "🔨 Building Docker image..."
docker build -t excel-processor .

# Run the container
echo "🚀 Starting container..."
docker run -d \
    --name excel-processor \
    -p 8000:8000 \
    -v "$(pwd)/uploads:/app/uploads" \
    -v "$(pwd)/outputs:/app/outputs" \
    --restart unless-stopped \
    excel-processor

echo "✅ Excel Processor is running!"
echo "🌐 Access at: http://localhost:8000"
echo "📊 Docker Desktop: Check the 'Containers' tab"
```

### **Docker Desktop UI Steps**

1. **Open Docker Desktop**
2. **Navigate to "Containers"**
3. **Click "New Container"**
4. **Fill in the details:**
   - **Image**: `excel-processor` (after building)
   - **Container name**: `excel-processor`
   - **Ports**: `8000:8000`
   - **Volumes**: 
     - `./uploads:/app/uploads`
     - `./outputs:/app/outputs`
5. **Click "Run"**

### **Accessing Your Application**

Once running in Docker Desktop:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Container Logs**: Check Docker Desktop "Containers" tab

### **Troubleshooting**

#### **If build fails:**
1. Check Docker Desktop is running
2. Ensure you have enough disk space
3. Try building from terminal first

#### **If container won't start:**
1. Check the logs in Docker Desktop
2. Ensure port 8000 is not in use
3. Verify the image was built successfully

#### **If you can't access the app:**
1. Check if container is running in Docker Desktop
2. Verify port mapping is correct
3. Check firewall settings

### **Development with Docker Desktop**

For development with hot-reloading:

```bash
# Build development image
docker build -f Dockerfile.dev -t excel-processor-dev .

# Run development container
docker run -d \
    --name excel-processor-dev \
    -p 8000:8000 \
    -p 3000:3000 \
    -v "$(pwd)/frontend/src:/app/frontend/src" \
    -v "$(pwd)/backend:/app/backend" \
    -v "$(pwd)/uploads:/app/uploads" \
    -v "$(pwd)/outputs:/app/outputs" \
    excel-processor-dev
```

This will give you:
- **Backend**: http://localhost:8000
- **Frontend (Dev)**: http://localhost:3000
- **Hot-reloading** for both frontend and backend 