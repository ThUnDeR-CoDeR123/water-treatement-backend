
from fastapi import APIRouter, Depends, HTTPException,UploadFile
from sqlalchemy.orm import Session
from app.logs.flow import crud 
from app.logs.flow.schema import (
    FlowLogSchema
)
from app.database import get_db
from app.auth.jwt import get_current_user,getPriviledgeUser,getAdmin
from app.models.base import User
from app.logs.flow.images import upload_image
import base64
import io


flowLogRouter = APIRouter(prefix="/api/v1/logs", tags=["flowLog"])

@flowLogRouter.post("/create/flow")
async def create_flow_log(
    log: FlowLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(getPriviledgeUser)
):
    try:
        print(log)
        # Handle inlet image if provided
        if log.inlet_image:
            try:
                # Extract base64 data (remove data:image/jpeg;base64, if present)
                if ',' in log.inlet_image:
                    base64_data = log.inlet_image.split(',')[1]
                else:
                    base64_data = log.inlet_image
                
                # Decode base64 to binary
                image_data = base64.b64decode(base64_data)
                
                # Create file-like object
                image_file = io.BytesIO(image_data)
                
                # Create UploadFile instance with the correct parameters
                upload_file = UploadFile(
                    filename="inlet.jpg",
                    file=image_file
                )
                upload_file.headers = {"content-type": "image/jpeg"}
                
                # Upload using existing image upload function
                result = await upload_image(upload_file)
                log.inlet_image = "https://api.watershooters.in/images/"+result["image_id"]
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error processing inlet image: {str(e)}")

        # Handle outlet image if provided
        if log.outlet_image:
            try:
                # Extract base64 data
                if ',' in log.outlet_image:
                    base64_data = log.outlet_image.split(',')[1]
                else:
                    base64_data = log.outlet_image
                
                # Decode base64 to binary
                image_data = base64.b64decode(base64_data)
                
                # Create file-like object
                image_file = io.BytesIO(image_data)
                
                # Create UploadFile instance with the correct parameters
                upload_file = UploadFile(
                    filename="outlet.jpg",
                    file=image_file
                )
                upload_file.headers = {"content-type": "image/jpeg"}
                
                # Upload using existing image upload function
                result = await upload_image(upload_file)
                log.outlet_image = "https://api.watershooters.in/images/"+result["image_id"]
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error processing outlet image: {str(e)}")

        # Create the flow log with image references
        result = crud.create_flow_log(db=db, log=log, user_id=current_user.user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@flowLogRouter.post("/flow")
def get_flow_logs(
    log: FlowLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return crud.get_flow_logs(db, log)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@flowLogRouter.put("/update/flow", response_model=FlowLogSchema)
def update_flow_log(
    log: FlowLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(getPriviledgeUser)
):
    try:
        print(log)
        return crud.update_flow_log(db, log)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@flowLogRouter.delete("/delete/flow/{flow_log_id}")
def delete_flow_log(
    flow_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(getAdmin)
):
    try:
        crud.delete_flow_log(db, FlowLogSchema(flow_log_id=flow_log_id))
        return {"message": "Flow log deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

