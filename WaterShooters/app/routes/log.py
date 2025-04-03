from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.crud.log import *
from app.schemas.logs import FlowParameterLogSchema, EquipmentLogSchema, ChemicalLogSchema, DailyLogSchema
from app.database import get_db
from app.routes.jwt import get_current_user,getPriviledgeUser
from app.models.base import User

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
    log: EquipmentLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(getPriviledgeUser)
):
    try:
        return createEquipmentLog(db, log,current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@logRouter.post("/create/chemical")
def create_log(
    log: EquipmentLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(getPriviledgeUser)
):
    try:
        return createEquipmentLog(db, log,current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Fetch logs for a specific entity
@logRouter.get("/equipment", response_model=List[EquipmentLogSchema])
def get_equipment_logs(
    log: EquipmentLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return getEquipmentLogs(db, log, current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@logRouter.get("/flowparameter", response_model=List[FlowParameterLogSchema])
def get_flow_parameter_logs(
    log: FlowParameterLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return getFowParameterLogs(db, log, current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@logRouter.get("/chemical", response_model=List[ChemicalLogSchema])
def get_chemical_logs(
    log: ChemicalLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return getChemicalLogs(db, log, current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))