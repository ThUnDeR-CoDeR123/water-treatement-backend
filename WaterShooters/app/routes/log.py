from fastapi import APIRouter, Depends, HTTPException,UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.crud import log as crud
from app.crud.log import *
from app.schemas.logs import (
    FlowParameterLogSchema, 
    EquipmentLogSchema, 
    ChemicalLogSchema, 
    DailyLogSchema,
    FlowLogSchema,
    GraphDataRequest,
    GraphDataSeriesResponse
)
from app.database import get_db
from app.routes.jwt import get_current_user,getPriviledgeUser,getAdmin
from app.models.base import User
from app.routes.images import upload_image
import base64
import io
from fastapi.responses import StreamingResponse
from datetime import date
from app.crud.report import generate_plant_report_pdf

logRouter = APIRouter(prefix="/api/v1/logs", tags=["Logs"])

# Create a log entry
@logRouter.post("/create/equipment")
def create_log(
    log: EquipmentLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(getPriviledgeUser)
):

        return createEquipmentLog(db, log,current_user.user_id)

    
    
@logRouter.post("/create/flowparameter")
def create_log(
    log: FlowParameterLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(getPriviledgeUser)
):
    try:
        return createFlowParameterLog(db, log,current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@logRouter.post("/create/chemical")
def create_log(
    log: ChemicalLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(getPriviledgeUser)
):
    try:
        return createChemicalLog(db, log,current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@logRouter.post("/create/flow")
async def create_flow_log(
    log: FlowLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(getPriviledgeUser)
):
    try:
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

# Fetch logs for a specific entity
@logRouter.post("/equipment")
def get_equipment_logs(
    log: EquipmentLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return getEquipmentLogs(db, log, current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@logRouter.post("/flowparameter")
def get_flow_parameter_logs(
    log: FlowParameterLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return getFowParameterLogs(db, log, current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@logRouter.post("/chemical")
def get_chemical_logs(
    log: ChemicalLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return getChemicalLogs(db, log, current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@logRouter.post("/flow")
def get_flow_logs(
    log: FlowLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return crud.get_flow_logs(db, log)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@logRouter.put("/update/chemical", response_model=ChemicalLogSchema)
def update_chemical_logs(
    log: ChemicalLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return updateChemicalLogs(db, log, current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@logRouter.put("/update/equipment", response_model=EquipmentLogSchema)
def update_equipment_logs(
    log: EquipmentLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return updateEquipmentLogs(db, log, current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@logRouter.put("/update/flowparameter", response_model=FlowParameterLogSchema)
def update_flow_parameter_logs(
    log: FlowParameterLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return updateFlowParameterLogs(db, log, current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@logRouter.put("/update/flow", response_model=FlowLogSchema)
def update_flow_log(
    log: FlowLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(getPriviledgeUser)
):
    try:
        return crud.update_flow_log(db, log)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@logRouter.delete("/delete/equipment")
def delete_equipment_logs(
    log: EquipmentLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(getAdmin)
):
    try:
        deleteEquipmentLog(db, log)
        return {"message": "Equipment log deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@logRouter.delete("/delete/flowparameter")
def delete_flow_parameter_logs(
    log: FlowParameterLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(getAdmin)
):
    try:
        deleteFlowParameterLog(db, log)
        return {"message": "Flow parameter log deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@logRouter.delete("/delete/chemical")
def delete_chemical_logs(
    log: ChemicalLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(getAdmin)
):
    try:
        deleteChemicalLog(db, log)
        return {"message": "Chemical log deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@logRouter.delete("/delete/flow")
def delete_flow_log(
    log: FlowLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(getAdmin)
):
    try:
        crud.delete_flow_log(db, log)
        return {"message": "Flow log deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@logRouter.post("/graph-data", response_model=GraphDataSeriesResponse)
def get_graph_data(
    request: GraphDataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get time series data for graphs"""
    try:
        series = crud.get_graph_data(db, request)
        print(series)
        return GraphDataSeriesResponse(series=series)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@logRouter.post("/graph-data/flow", response_model=GraphDataSeriesResponse)
def get_flow_graph_data(
    request: GraphDataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get flow data (inlet/outlet values) for graphs"""
    try:
        request.log_type = "flow"  # Override log type to ensure flow data
        series = crud.get_graph_data(db, request)
        print(series)
        return GraphDataSeriesResponse(series=series)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@logRouter.post("/graph-data/equipment", response_model=GraphDataSeriesResponse)
def get_equipment_graph_data(
    request: GraphDataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get equipment status data for graphs"""
    try:
        request.log_type = "equipment"  # Override log type to ensure equipment data
        series = crud.get_graph_data(db, request)
        print(series)
        return GraphDataSeriesResponse(series=series)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@logRouter.post("/graph-data/chemical/used", response_model=GraphDataSeriesResponse)
def get_chemical_usage_graph_data(
    request: GraphDataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chemical quantity used data for graphs"""
    try:
        request.log_type = "chemical-used"  # Override log type to ensure chemical data
        series = crud.get_graph_data(db, request)
        # Filter only the "Used" series
        print(series)
        # filtered_series = [s for s in series if "(Used)" in s.series_name]
        return GraphDataSeriesResponse(series=series)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@logRouter.post("/graph-data/chemical/remaining", response_model=GraphDataSeriesResponse)
def get_chemical_remaining_graph_data(
    request: GraphDataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chemical quantity remaining data for graphs"""
    try:
        request.log_type = "chemical-left"  # Override log type to ensure chemical data
        series = crud.get_graph_data(db, request)
        # Filter only the "Quantity Left" series
        print(series)
        # filtered_series = [s for s in series if "(Quantity Left)" in s.series_name]
        return GraphDataSeriesResponse(series=series)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@logRouter.post("/graph-data/parameters", response_model=GraphDataSeriesResponse)
def get_flow_parameters_graph_data(
    request: GraphDataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get flow parameters data for graphs"""
    try:
        request.log_type = "flowparameter"  # Override log type to ensure flow parameter data
        series = crud.get_graph_data(db, request)
        print(series)
        return GraphDataSeriesResponse(series=series)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@logRouter.get("/report/pdf")
def download_pdf_report(plant_id: int, start_date: date, end_date: date, db: Session = Depends(get_db)):
    pdf_data = generate_plant_report_pdf(db, plant_id, start_date, end_date)
    return StreamingResponse(io.BytesIO(pdf_data), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=plant_report.pdf"})

