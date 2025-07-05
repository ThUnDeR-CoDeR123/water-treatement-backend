from fastapi import APIRouter, Depends, HTTPException,UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.logs.parameter.crud import *
from app.logs.parameter.schema import FlowParameterLogSchema
from app.database import get_db
from app.auth.jwt import get_current_user,getPriviledgeUser,getAdmin
from app.models.base import User
import base64
import io
from fastapi.responses import StreamingResponse
from datetime import date
from app.plant.report import generate_plant_report_pdf

flowParameterLogRouter = APIRouter(prefix="/api/v1/logs", tags=["ParameterLog"])




    
@flowParameterLogRouter.post("/create/flowparameter")
def create_log(
    log: FlowParameterLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(getPriviledgeUser)
):
    try:
        print(log)
        return createFlowParameterLog(db, log,current_user.user_id)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))


@flowParameterLogRouter.post("/flowparameter")
def get_flow_parameter_logs(
    log: FlowParameterLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return getFowParameterLogs(db, log, current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@flowParameterLogRouter.put("/update/flowparameter", response_model=FlowParameterLogSchema)
def update_flow_parameter_logs(
    log: FlowParameterLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        print(log)
        return updateFlowParameterLogs(db, log, current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@flowParameterLogRouter.delete("/delete/flowparameter/{flow_parameter_log_id}")
def delete_flow_parameter_logs(
    flow_parameter_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(getAdmin)
):
    try:
        deleteFlowParameterLog(db, FlowParameterLogSchema(flow_parameter_log_id=flow_parameter_log_id))
        return {"message": "Flow parameter log deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))