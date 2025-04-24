import os
import uuid
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
from typing import Optional

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