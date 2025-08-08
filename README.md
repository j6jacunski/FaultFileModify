# Excel Processor Web Application

A web-based application for processing Excel files with multiple CPU tabs, extracting fault data, and generating formatted output files.

## Features

- **File Upload**: Drag-and-drop or file picker for Excel files
- **CPU Selection**: Choose specific CPU tabs to process
- **Real-time Processing**: Progress tracking with detailed status updates
- **Data Preview**: View processed data with search functionality
- **Multiple Output Formats**: Individual files and ZIP archives
- **Usage Statistics**: Track fault bit usage and spare percentages

## Architecture

- **Frontend**: React with TypeScript and Material-UI
- **Backend**: FastAPI with Python
- **Containerization**: Docker with multi-stage builds
- **File Processing**: Pandas for Excel manipulation

## Quick Start with Docker

### Production Deployment

1. **Build and run the application:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development Environment

1. **Start development environment with hot-reloading:**
   ```bash
   docker-compose --profile dev up --build
   ```

2. **Access the application:**
   - Frontend (Development): http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Manual Setup (Without Docker)

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm

### Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the backend server:**
   ```bash
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Install Node.js dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm start
   ```

## Usage

### 1. Upload Excel File
- Drag and drop your Excel file or use the file picker
- Supported formats: `.xlsx`, `.xlsm`
- File structure should have CPU tabs (CPU01, CPU02, etc.)

### 2. Select CPU Tabs
- Choose which CPU tabs to process
- Use "Select All" to process all available CPUs
- Preview data for each CPU before processing

### 3. Process Files
- Click "Process Files" to start processing
- Monitor progress with real-time updates
- View detailed processing steps and completion status

### 4. Download Results
- Download individual CPU files
- Download ZIP archive containing all processed files
- Files contain three sheets: Faults, Manual Interventions, Warnings

## File Structure

```
FaultFileModify/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── excel_processor.py   # Excel processing logic
│   └── __init__.py
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   └── App.tsx         # Main application
│   ├── package.json
│   └── tsconfig.json
├── uploads/                 # Uploaded files (persistent)
├── outputs/                 # Processed files (persistent)
├── Dockerfile              # Production Docker image
├── Dockerfile.dev          # Development Docker image
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
└── README.md
```

## API Endpoints

- `POST /upload/` - Upload Excel file
- `GET /available-cpus/{filename}` - Get available CPU tabs
- `GET /preview/{filename}/{cpu}` - Preview CPU data
- `POST /process/` - Process selected CPUs
- `GET /progress/{job_id}` - Get processing progress
- `GET /download/{filename}` - Download processed file
- `GET /history/` - Get processing history

## Docker Commands

### Build Images
```bash
# Production image
docker build -t excel-processor .

# Development image
docker build -f Dockerfile.dev -t excel-processor-dev .
```

### Run Containers
```bash
# Production
docker run -p 8000:8000 -v $(pwd)/uploads:/app/uploads -v $(pwd)/outputs:/app/outputs excel-processor

# Development
docker run -p 8000:8000 -p 3000:3000 -v $(pwd):/app excel-processor-dev
```

### Docker Compose
```bash
# Production
docker-compose up --build

# Development
docker-compose --profile dev up --build

# Background mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Environment Variables

- `PYTHONPATH`: Python module path (default: `/app`)
- `PORT`: Backend port (default: `8000`)
- `NODE_ENV`: Node.js environment (default: `development`)

## Data Persistence

The application uses Docker volumes to persist:
- **Uploads**: Uploaded Excel files
- **Outputs**: Processed output files
- **History**: Processing history and job data

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Check what's using the port
   lsof -i :8000
   # Kill the process or change the port in docker-compose.yml
   ```

2. **Permission errors:**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER uploads/ outputs/
   ```

3. **Build failures:**
   ```bash
   # Clean Docker cache
   docker system prune -a
   # Rebuild without cache
   docker-compose build --no-cache
   ```

### Logs and Debugging

```bash
# View application logs
docker-compose logs -f excel-processor

# Access container shell
docker-compose exec excel-processor bash

# Check container health
docker-compose ps
```

## Development

### Adding New Features

1. **Backend changes:**
   - Modify files in `backend/`
   - Restart the container or use `--reload` flag

2. **Frontend changes:**
   - Modify files in `frontend/src/`
   - Changes auto-reload in development mode

3. **Dependencies:**
   - Backend: Update `requirements.txt`
   - Frontend: Update `frontend/package.json`

### Testing

```bash
# Run backend tests
cd backend && python -m pytest

# Run frontend tests
cd frontend && npm test

# Run in Docker
docker-compose exec excel-processor python -m pytest
```

## Production Deployment

### Docker Production

1. **Build optimized image:**
   ```bash
   docker build -t excel-processor:latest .
   ```

2. **Run with production settings:**
   ```bash
   docker run -d \
     --name excel-processor \
     -p 8000:8000 \
     -v /path/to/uploads:/app/uploads \
     -v /path/to/outputs:/app/outputs \
     --restart unless-stopped \
     excel-processor:latest
   ```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests.

## License

This project is proprietary software for internal use.

## Support

For issues and questions, contact the development team.