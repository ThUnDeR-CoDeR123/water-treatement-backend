import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
from typing import Optional
from datetime import datetime

imageRouter = APIRouter(prefix="/images", tags=["images"])

UPLOAD_DIR = "/app/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@imageRouter.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save the file
    with open(file_path, "wb+") as file_object:
        file_object.write(await file.read())
    
    return {"image_id": unique_filename}

@imageRouter.get("/{image_id}")
async def get_image(image_id: str):
    file_path = os.path.join(UPLOAD_DIR, image_id)
    if not os.path.exists(file_path):
        return {"error": "Image not found"}, 404
    
    return FileResponse(file_path)

@imageRouter.get("/download/all")
async def download_all_images():
    # Create a timestamp for unique zip file name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"images_{timestamp}.zip"
    zip_filepath = os.path.join(UPLOAD_DIR, zip_filename)
    zip_base = os.path.join(UPLOAD_DIR, f"images_{timestamp}")
    
    try:
        # Create a zip file containing all images
        shutil.make_archive(
            base_name=zip_base,
            format='zip',
            root_dir=UPLOAD_DIR
        )
        
        # Return the zip file
        response = FileResponse(
            zip_filepath,
            media_type='application/zip',
            filename=zip_filename
        )
        
        return response
    except Exception as e:
        return {"error": f"Failed to create zip file: {str(e)}"}, 500