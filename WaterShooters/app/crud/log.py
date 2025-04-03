from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.schemas.logs import EquipmentLogSchema, FlowParameterLogSchema, ChemicalLogSchema
from app.models.base import DailyLog, EquipmentLog, FlowParameterLog, ChemicalLog, PlantEquipment, PlantFlowParameter, PlantChemical
from fastapi import HTTPException
from typing import List

# Create a log entry

def createEquipmentLog(db: Session, log: EquipmentLogSchema, user_id: int):
    # Check if there is any log for the same date and same shift
    print("inside createEquipmentLog")
    plant_equipment = db.query(PlantEquipment).filter(
        PlantEquipment.plant_equipment_id == log.plant_equipment_id,
        PlantEquipment.del_flag == False
    ).first()
    print("after query")
    if not plant_equipment:
        raise HTTPException(status_code=404, detail="Plant equipment not found")

    query = db.query(DailyLog).filter(DailyLog.del_flag == False)
    if plant_equipment.plant_id is not None:
        query = query.filter(DailyLog.plant_id == plant_equipment.plant_id)
    if user_id is not None:
        query = query.filter(DailyLog.created_by == user_id)
    if log.shift is not None:
        query = query.filter(DailyLog.shift == log.shift)
    query = query.filter(func.date(DailyLog.created_at) == func.date(func.now()))  # Compare only date, not time
    existing_log = query.first()
    print("after querrying daily log")
    if existing_log:
        # If a daily log exists, create a new equipment log entry
        print("inside existing log")
        new_log = EquipmentLog(**log.model_dump(exclude_unset=True), daily_log_id=existing_log.log_id, created_by=user_id)
        print("after inserting new equipment log")
        plant_equipment.status = log.equipment_status
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
    else:
        print("inside non existing log")
        # Create a daily log entry
        new_daily_log = DailyLog(plant_id=plant_equipment.plant_id, shift=log.shift, created_by=user_id)
        print("after inserting new log daily log")
        db.add(new_daily_log)
        db.commit()

        # Creating a new equipment log entry
        new_log = EquipmentLog(**log.model_dump(exclude_unset=True), daily_log_id=new_daily_log.log_id, created_by=user_id)
        plant_equipment.status = log.equipment_status
        db.add(new_log)
        db.commit()


def createFlowParameterLog(db: Session, log: FlowParameterLogSchema, user_id: int):
    plant_flow_parameter = db.query(PlantFlowParameter).filter(
        PlantFlowParameter.plant_flow_parameter_id == log.plant_flow_parameter_id,
        PlantFlowParameter.del_flag == False
    ).first()
    if not plant_flow_parameter:
        raise HTTPException(status_code=404, detail="Plant flow parameter not found")

    query = db.query(DailyLog).filter(DailyLog.del_flag == False)
    if log.plant_id is not None:
        query = query.filter(DailyLog.plant_id == log.plant_id)
    if user_id is not None:
        query = query.filter(DailyLog.created_by == user_id)
    if log.shift is not None:
        query = query.filter(DailyLog.shift == log.shift)
    query = query.filter(func.date(DailyLog.created_at) == func.date(func.now()))  # Compare only date, not time
    existing_log = query.first()

    if existing_log:
        # If a daily log exists, create a new flow parameter log entry
        new_log = FlowParameterLog(**log.model_dump(exclude_unset=True), daily_log_id=existing_log.log_id, created_by=user_id)
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
    else:
        # Create a daily log entry
        new_daily_log = DailyLog(plant_id=log.plant_id, shift=log.shift, created_by=user_id)
        db.add(new_daily_log)
        db.commit()

        # Creating a new flow parameter log entry
        new_log = FlowParameterLog(**log.model_dump(exclude_unset=True), daily_log_id=new_daily_log.log_id, created_by=user_id)
        db.add(new_log)
        db.commit()


def createChemicalLog(db: Session, log: ChemicalLogSchema, user_id: int):
    plant_chemical = db.query(PlantChemical).filter(
        PlantChemical.plant_chemical_id == log.plant_chemical_id,
        PlantChemical.del_flag == False
    ).first()
    if not plant_chemical:
        raise HTTPException(status_code=404, detail="Plant chemical not found")

    query = db.query(DailyLog).filter(DailyLog.del_flag == False)
    if plant_chemical.plant_id is not None:
        query = query.filter(DailyLog.plant_id == plant_chemical.plant_id)
    if user_id is not None:
        query = query.filter(DailyLog.created_by == user_id)
    if log.shift is not None:
        query = query.filter(DailyLog.shift == log.shift)
    query = query.filter(func.date(DailyLog.created_at) == func.date(func.now()))  # Compare only date, not time
    existing_log = query.first()

    if existing_log:
        # If a daily log exists, create a new chemical log entry
        new_log = ChemicalLog(**log.model_dump(exclude_unset=True), daily_log_id=existing_log.log_id, created_by=user_id)
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
    else:
        # Create a daily log entry
        new_daily_log = DailyLog(plant_id=plant_chemical.plant_id, shift=log.shift, created_by=user_id)
        db.add(new_daily_log)
        db.commit()

        # Creating a new chemical log entry
        new_log = ChemicalLog(**log.model_dump(exclude_unset=True), daily_log_id=new_daily_log.log_id, created_by=user_id)
        db.add(new_log)
        db.commit()

# Fetch logs by entity type and entity ID

def getEquipmentLogs(db: Session, log: EquipmentLogSchema, user_id: int) -> List[EquipmentLog]:
    query = db.query(EquipmentLog).filter(EquipmentLog.del_flag == False)
    if log.plant_id is not None:
        query = query.filter(EquipmentLog.plant_id == log.plant_id)
    if log.start_date is not None:
        query = query.filter(EquipmentLog.created_at >= log.start_date)
    if log.end_date is not None:
        query = query.filter(EquipmentLog.created_at <= log.end_date)
    equipmentlogs = query.all()

    if not equipmentlogs:
        raise HTTPException(status_code=404, detail="Logs not found")
    return equipmentlogs

def getChemicalLogs(db: Session, log: ChemicalLogSchema, user_id: int) -> List[ChemicalLogSchema]:
    query = db.query(ChemicalLog).filter(ChemicalLog.del_flag == False)
    if log.plant_id is not None:
        query = query.filter(ChemicalLog.plant_id == log.plant_id)
    if log.start_date is not None:
        query = query.filter(ChemicalLog.created_at >= log.start_date)
    if log.end_date is not None:
        query = query.filter(ChemicalLog.created_at <= log.end_date)
    chemicallogs = query.all()

    if not chemicallogs:
        raise HTTPException(status_code=404, detail="Logs not found")
    return chemicallogs

def getFowParameterLogs(db: Session, log: FlowParameterLogSchema, user_id: int) -> List[FlowParameterLogSchema]:
    query = db.query(FlowParameterLog).filter(FlowParameterLog.del_flag == False)
    if log.plant_id is not None:
        query = query.filter(FlowParameterLog.plant_id == log.plant_id)
    if log.start_date is not None:
        query = query.filter(FlowParameterLog.created_at >= log.start_date)
    if log.end_date is not None:
        query = query.filter(FlowParameterLog.created_at <= log.end_date)
    flowparameterlogs = query.all()

    if not flowparameterlogs:
        raise HTTPException(status_code=404, detail="Logs not found")
    return flowparameterlogs