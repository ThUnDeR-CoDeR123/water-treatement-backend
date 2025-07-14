from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.logs.chemical.schema import (
    ChemicalLogSchema
)
from app.models.base import DailyLog, EquipmentLog, FlowParameterLog, ChemicalLog, PlantEquipment, PlantFlowParameter, PlantChemical, FlowLog
from fastapi import HTTPException
from typing import List
from datetime import datetime, timedelta, timezone


def get_IST():
    """Get current time in Indian Standard Time (IST)"""
    return datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)




def createChemicalLog(db: Session, log: ChemicalLogSchema, user_id: int):
    plant_chemical = db.query(PlantChemical).filter(
        PlantChemical.plant_chemical_id == log.plant_chemical_id,
        PlantChemical.del_flag == False
    ).first()
    if not plant_chemical:
        raise HTTPException(status_code=404, detail="Plant chemical not found")
    if plant_chemical.quantity < log.quantity_used:
        raise HTTPException(status_code=400, detail="Insufficient chemical quantity")
    query = db.query(DailyLog).filter(DailyLog.del_flag == False)
    if plant_chemical.plant_id is not None:
        query = query.filter(DailyLog.plant_id == plant_chemical.plant_id)
    if user_id is not None:
        query = query.filter(DailyLog.created_by == user_id)
    if log.shift is not None:
        query = query.filter(DailyLog.shift == log.shift)
    query = query.filter(func.date(DailyLog.created_at) == func.date(get_IST()))  # Compare only date, not time
    existing_log = query.first()
    # plant_chemical = db.query(PlantChemical).filter(PlantChemical.plant_chemical_id == log.plant_chemical_id).first()
    if existing_log:
        # If a daily log exists, create a new chemical log entry
        if log.incomming_quantity:
            plant_chemical.quantity+=log.incomming_quantity
        plant_chemical.quantity-=log.quantity_used
        new_log = ChemicalLog(
            plant_chemical_id =plant_chemical.plant_chemical_id, 
            plant_id= log.plant_id,
            shift=log.shift,
            quantity_left=plant_chemical.quantity,
            quantity_used=log.quantity_used,
            incomming_quantity=log.incomming_quantity if log.incomming_quantity else 0,
            chemical_name=plant_chemical.chemical_name,
            sludge_discharge=log.sludge_discharge,
            daily_log_id=existing_log.log_id, 
            created_by=user_id,
            created_at=get_IST()  # Use the IST function to set created_at
        )
        # plant_chemical.quantity= log.quantity_left
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return new_log
    else:
        # Create a daily log entry
        new_daily_log = DailyLog(plant_id=plant_chemical.plant_id, shift=log.shift, created_by=user_id, created_at=get_IST())  # Use the IST function to set created_at
        db.add(new_daily_log)
        db.commit()
        if log.incomming_quantity:
            plant_chemical.quantity+=log.incomming_quantity
        plant_chemical.quantity-=log.quantity_used
        # Creating a new chemical log entry
        new_log = ChemicalLog(
            plant_chemical_id =plant_chemical.plant_chemical_id, 
            plant_id= log.plant_id,
            shift=log.shift,
            quantity_left=plant_chemical.quantity,
            quantity_used=log.quantity_used,
            incomming_quantity=log.incomming_quantity if log.incomming_quantity else 0,
            chemical_name=plant_chemical.chemical_name,
            sludge_discharge=log.sludge_discharge,
            daily_log_id=new_daily_log.log_id, 
            created_by=user_id,
            created_at=get_IST()
        )

        db.add(new_log)
        db.commit()
        return new_log


def getChemicalLogs(db: Session, log: ChemicalLogSchema, user_id: int) -> List[ChemicalLogSchema]:
    query = db.query(ChemicalLog).filter(ChemicalLog.del_flag == False)
    if log.plant_id is not None:
        query = query.filter(ChemicalLog.plant_id == log.plant_id)
    if log.start_date is not None and log.end_date is not None:
        query = query.filter(func.date(EquipmentLog.created_at).between(log.start_date, log.end_date))
    elif log.start_date is not None:
        query = query.filter(func.date(EquipmentLog.created_at) >= log.start_date)
    elif log.end_date is not None:
        query = query.filter(func.date(EquipmentLog.created_at) <= log.end_date)
    if log.created_at is not None:
        query = query.filter(func.date(ChemicalLog.created_at) == func.date(log.created_at))
    chemicallogs = query.all()

    if not chemicallogs:
        return []
    return chemicallogs


def updateChemicalLogs(db: Session, log: ChemicalLogSchema, user_id: int) -> List[ChemicalLogSchema]:
    chemical_log = db.query(ChemicalLog).filter(ChemicalLog.del_flag == False, ChemicalLog.chemical_log_id==log.chemical_log_id).first()
    plant_chemical = db.query(PlantChemical).filter(PlantChemical.plant_chemical_id==chemical_log.plant_chemical_id).first()
    if not chemical_log:
        raise HTTPException(status_code=404, detail="Logs not found")
    if log.incomming_quantity:
            plant_chemical.quantity=plant_chemical.quantity+log.incomming_quantity-chemical_log.incomming_quantity
    plant_chemical.quantity=plant_chemical.quantity-log.quantity_used
    plant_chemical.quantity=plant_chemical.quantity+chemical_log.quantity_used
    old_quantity_used = chemical_log.quantity_used
    old_incomming_quantity = chemical_log.incomming_quantity
    if log.quantity_used is not None:
        chemical_log.quantity_used = log.quantity_used
    # if log.quantity_left is not None:
    #     chemical_log.quantity_left = plant_chemical.quantity
    if log.sludge_discharge is not None:
        chemical_log.sludge_discharge = log.sludge_discharge
    if log.shift is not None:
        chemical_log.shift = log.shift
    chemical_log.quantity_left=chemical_log.quantity_left + log.incomming_quantity - log.quantity_used + old_quantity_used - old_incomming_quantity
    chemical_log.updated_at = get_IST()  # Use the IST function to set updated_at
    db.commit()
    db.refresh(chemical_log)

    return chemical_log



def deleteChemicalLog(db: Session, log: ChemicalLogSchema) -> bool:
    chemical_log = db.query(ChemicalLog).filter(ChemicalLog.del_flag == False, ChemicalLog.chemical_log_id == log.chemical_log_id).first()
    if not chemical_log:
        raise HTTPException(status_code=404, detail="Logs not found")
    chemical_log.del_flag = True
    chemical_log.updated_at = get_IST()  # Use the IST function to set updated_at
    db.commit()
    return True
