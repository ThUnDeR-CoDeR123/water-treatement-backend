
from app.logs.schema import getLogSchema
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.logs.parameter.crud import getFowParameterLogs
from app.logs.chemical.crud import getChemicalLogs
from app.logs.chemical.schema import ChemicalLogSchema
from app.logs.equipment.crud import getEquipmentLogs
from app.logs.equipment.schema import EquipmentLogSchema
from app.logs.flow.schema import FlowLogSchema
from app.logs.flow.crud import get_flow_logs
from app.logs.parameter.schema import FlowParameterLogSchema
from app.database import get_db
from app.auth.jwt import get_current_user
from app.models.base import User

logRouter = APIRouter(prefix="/api/v1/logs", tags=["Logs"])


@logRouter.post("/all")
def get_all_logs(log: getLogSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Fetch all logs for a plant within a date range.
    """
    try:
        if not log.plant_id:
            raise HTTPException(status_code=400, detail="plant_id is required")
        if not log.start_date or not log.end_date:
            raise HTTPException(status_code=400, detail="start_date and end_date are required")
        if not log.start_date <= log.end_date:
            raise HTTPException(status_code=400, detail="start_date must be before end_date")
        chemicalLog = getChemicalLogs(db, ChemicalLogSchema(plant_id=log.plant_id, start_date=log.start_date, end_date=log.end_date), current_user.user_id)
        equipmentLog = getEquipmentLogs(db, EquipmentLogSchema(plant_id=log.plant_id, start_date=log.start_date, end_date=log.end_date), current_user.user_id)
        flowParameterLog = getFowParameterLogs(db, FlowParameterLogSchema(plant_id=log.plant_id, start_date=log.start_date, end_date=log.end_date), current_user.user_id)
        flowLog = get_flow_logs(db, FlowLogSchema(plant_id=log.plant_id, start_date=log.start_date, end_date=log.end_date))
        return {
            "chemical_logs": chemicalLog,
            "equipment_logs": equipmentLog,
            "flow_parameter_logs": flowParameterLog,
            "flow_logs": flowLog
        }
    except Exception as e:

        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))