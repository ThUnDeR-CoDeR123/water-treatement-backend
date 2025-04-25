from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.crud import log as crud
from app.crud.log import *
from app.schemas.logs import FlowParameterLogSchema, EquipmentLogSchema, ChemicalLogSchema, DailyLogSchema, FlowLog, FlowLogCreate, FlowLogUpdate
from app.database import get_db
from app.routes.jwt import get_current_user,getPriviledgeUser,getAdmin
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
def create_flow_log(
    log: schemas.FlowLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(getPriviledgeUser)
):
    try:
        return crud.create_flow_log(db, log, current_user.user_id)
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
    
@logRouter.get("/flow")
def get_flow_logs(
    log: schemas.FlowLogSchema,
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

@logRouter.put("/update/flow", response_model=schemas.FlowLogSchema)
def update_flow_log(
    log: schemas.FlowLogSchema,
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
    log: schemas.FlowLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(getAdmin)
):
    try:
        crud.delete_flow_log(db, log)
        return {"message": "Flow log deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
