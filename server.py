from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
import os
import shutil
import subprocess
import time
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
# Allow frontend requests from http://localhost:3000

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Change this if your frontend URL is different
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


UPLOAD_DIR = "d:/vechicle-master/backend/uploads"
OUTPUT_DIR = "d:/vechicle-master/backend/outputs"
VIDEO_PATH = os.path.join(OUTPUT_DIR, "output.mp4")


os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

processing = False  # Global flag to track processing status


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    global processing
    processing = True  # Set processing flag

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print(f"📥 Received file: {file.filename} -> {file_path}")

    # Process the video using traffic2.py
    output_file_path = os.path.join(OUTPUT_DIR, "output.mp4")
    
    process = subprocess.run(["python", "d:/vechicle-master/count+plate_detection/main.py", file_path, output_file_path], 
                             capture_output=True, text=True)
    
    if process.returncode == 0:
        print("✅ Processing completed successfully.")
        processing = False  # Set processing to False once video is ready
        return {"status": "completed", "output_file": "output.mp4"}
    else:
        print(f"❌ Error in processing: {process.stderr}")
        processing = False  # Reset flag in case of failure
        return {"error": "Processing failed", "details": process.stderr}


@app.get("/status/")
async def check_status():
    """Check if the processed video is available"""
    if processing:
        return {"status": "processing"}  # Still processing

    if os.path.exists(VIDEO_PATH) and os.path.getsize(VIDEO_PATH) > 5000:
        return {"status": "completed"}  # Video is ready

    return {"status": "processing"}  # Still processing


@app.get("/output/")
async def get_output_video():
    """Serves the processed video when it's ready"""
    if processing:
        return JSONResponse(status_code=202, content={"message": "Processing video, please wait..."})

    if os.path.exists(VIDEO_PATH) and os.path.getsize(VIDEO_PATH) > 5000:
        print("📂 Sending processed video...")
        return FileResponse(VIDEO_PATH, media_type="video/mp4", filename="output.mp4")

    return JSONResponse(status_code=404, content={"error": "Processed video not found"})


@app.get("/download/")
async def download_file():
    """Allows the frontend to download the processed video."""
    if processing:
        print("Processing")
        return JSONResponse(status_code=202, content={"message": "Processing video, please wait..."})

    if not os.path.exists(VIDEO_PATH) or os.path.getsize(VIDEO_PATH) == 0:
        print("File not found")
        return JSONResponse(status_code=404, content={"error": "File not found or still processing"})
    print(f"Serving file from: {VIDEO_PATH}")
    return FileResponse(VIDEO_PATH, media_type="video/mp4", filename="output.mp4",)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
