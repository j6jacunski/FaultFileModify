from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import pandas as pd
import os
from datetime import datetime
import json
from pathlib import Path
from backend.excel_processor import ExcelProcessor
import zipfile
import asyncio
import time

app = FastAPI(title="Excel Processor")

# Configure CORS to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:49490", "*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
HISTORY_FILE = Path("history.json")

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize history file if it doesn't exist
if not HISTORY_FILE.exists():
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

# Progress tracking
processing_status = {}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        return {"filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/available-cpus/{filename}")
async def get_available_cpus(filename: str):
    try:
        file_path = UPLOAD_DIR / filename
        processor = ExcelProcessor(file_path)
        cpu_sheets = processor.get_available_cpus()
        return {"cpus": cpu_sheets}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/preview/{filename}/{cpu}")
async def preview_cpu(filename: str, cpu: str):
    try:
        file_path = UPLOAD_DIR / filename
        processor = ExcelProcessor(file_path)
        preview_data = processor.preview_cpu_tab(cpu)
        return preview_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/data/{filename}/{cpu}")
async def get_cpu_data(filename: str, cpu: str, section: str, page: int = 0, page_size: int = 1000):
    """Get paginated data for a specific CPU and section."""
    try:
        file_path = UPLOAD_DIR / filename
        processor = ExcelProcessor(file_path)
        data = processor.get_section_data(cpu, section, page, page_size)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from pydantic import BaseModel

class ProcessRequest(BaseModel):
    filename: str
    selected_cpus: List[str]

@app.post("/process/")
async def process_file(request: ProcessRequest):
    try:
        # Generate a unique job ID
        job_id = f"job_{int(time.time())}"
        
        # Initialize progress tracking
        processing_status[job_id] = {
            "status": "starting",
            "current_step": "Initializing processor...",
            "progress": 0,
            "total_steps": len(request.selected_cpus) + 2,  # +2 for initialization and zip creation
            "current_cpu": None,
            "completed_cpus": [],
            "error": None
        }
        
        input_file = UPLOAD_DIR / request.filename
        processor = ExcelProcessor(input_file)
        
        # Update progress
        processing_status[job_id]["status"] = "processing"
        processing_status[job_id]["current_step"] = "Processing CPU files..."
        processing_status[job_id]["progress"] = 1
        
        # Process each CPU with progress tracking
        output_files = {}
        total_cpus = len(request.selected_cpus)
        
        for i, cpu in enumerate(request.selected_cpus, 1):
            # Update progress for current CPU
            processing_status[job_id]["current_cpu"] = cpu
            processing_status[job_id]["current_step"] = f"Processing {cpu}... ({i}/{total_cpus})"
            processing_status[job_id]["progress"] = i
            
            # Process individual CPU
            output_files[cpu] = processor.process_cpu_tab_to_file(cpu, OUTPUT_DIR)
            processing_status[job_id]["completed_cpus"].append(cpu)
            
            # Small delay to allow progress updates
            await asyncio.sleep(0.1)
        
        # Update progress for zip creation
        processing_status[job_id]["current_step"] = "Creating ZIP file..."
        processing_status[job_id]["progress"] = total_cpus + 1
        
        # Create zip file
        zip_filename = f"{request.filename}_processed.zip"
        zip_path = OUTPUT_DIR / zip_filename
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for cpu, file_path in output_files.items():
                zipf.write(file_path, file_path.name)
        
        # Mark as completed
        processing_status[job_id]["status"] = "completed"
        processing_status[job_id]["current_step"] = "Processing completed!"
        processing_status[job_id]["progress"] = total_cpus + 2
        
        # Return individual files and zip file
        individual_files = {cpu: file_path.name for cpu, file_path in output_files.items()}
        return {
            "job_id": job_id,
            "individual_files": individual_files,
            "zip_file": zip_filename
        }
    except Exception as e:
        if job_id in processing_status:
            processing_status[job_id]["status"] = "error"
            processing_status[job_id]["error"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/progress/{job_id}")
async def get_progress(job_id: str):
    """Get the current progress of a processing job."""
    if job_id not in processing_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Clean up old completed jobs (older than 1 hour)
    current_time = time.time()
    jobs_to_remove = []
    for job_id_old, job_data in processing_status.items():
        if job_data["status"] in ["completed", "error"] and current_time - float(job_id_old.split("_")[1]) > 3600:
            jobs_to_remove.append(job_id_old)
    
    for job_id_old in jobs_to_remove:
        del processing_status[job_id_old]
    
    return processing_status[job_id]

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@app.get("/history/")
async def get_history():
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
    return {"history": history[-10:]}  # Return last 10 entries

# Mount static files for React frontend (in production) - mount AFTER all API routes
try:
    # Mount static assets first
    if os.path.exists("frontend/build/static"):
        app.mount("/static", StaticFiles(directory="frontend/build/static", html=False), name="static")
    
    # Mount the main frontend files
    if os.path.exists("frontend/build"):
        app.mount("/", StaticFiles(directory="frontend/build", html=True), name="frontend")
        print("Static files mounted successfully")
    else:
        print("frontend/build directory not found - static files not mounted")
except Exception as e:
    # In development, frontend/build might not exist
    print(f"Could not mount static files: {e}")
    pass

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)