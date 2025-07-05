from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.logs.equipment.crud import *
from app.logs.equipment.schema import (
    EquipmentLogSchema
)
from app.database import get_db
from app.auth.jwt import get_current_user,getPriviledgeUser,getAdmin
from app.models.base import User

equipmentLogRouter = APIRouter(prefix="/api/v1/logs", tags=["equipmentLog"])
# Create a log entry
@equipmentLogRouter.post("/create/equipment")
def create_log(
    log: EquipmentLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(getPriviledgeUser)
):
        print(log)
        return createEquipmentLog(db, log,current_user.user_id)

    

# Fetch logs for a specific entity
@equipmentLogRouter.post("/equipment")
def get_equipment_logs(
    log: EquipmentLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return getEquipmentLogs(db, log, current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@equipmentLogRouter.put("/update/equipment", response_model=EquipmentLogSchema)
def update_equipment_logs(
    log: EquipmentLogSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        print(log)
        return updateEquipmentLogs(db, log, current_user.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@equipmentLogRouter.delete("/delete/equipment/{equipment_log_id}")
def delete_equipment_logs(
    equipment_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(getAdmin)
):
    try:
        deleteEquipmentLog(db, EquipmentLogSchema(equipment_log_id=equipment_log_id))
        return {"message": "Equipment log deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))