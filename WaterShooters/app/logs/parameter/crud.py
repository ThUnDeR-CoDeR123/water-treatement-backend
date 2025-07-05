from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.logs.parameter.schema import FlowParameterLogSchema
from app.models.base import DailyLog, EquipmentLog, FlowParameterLog, ChemicalLog, PlantEquipment, PlantFlowParameter, PlantChemical, FlowLog
from fastapi import HTTPException
from typing import List
from datetime import datetime, timedelta, timezone


def get_IST():
    """Get current time in Indian Standard Time (IST)"""
    return datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)

def createFlowParameterLog(db: Session, log: FlowParameterLogSchema, user_id: int):
    print("1")
    plant_flow_parameter = db.query(PlantFlowParameter).filter(
        PlantFlowParameter.plant_flow_parameter_id == log.plant_flow_parameter_id,
        PlantFlowParameter.del_flag == False
    ).first()
    if not plant_flow_parameter:
        raise HTTPException(status_code=404, detail="Plant flow parameter not found")

    query = db.query(DailyLog).filter(DailyLog.del_flag == False)
    if log.plant_id is not None:
        print("2")
        query = query.filter(DailyLog.plant_id == log.plant_id)
    if user_id is not None:
        print("3")
        query = query.filter(DailyLog.created_by == user_id)
    if log.shift is not None:
        print("3.1")
        query = query.filter(DailyLog.shift == log.shift)
    query = query.filter(func.date(DailyLog.created_at) == func.date(get_IST()))  # Compare only date, not time
    existing_log = query.first()
    print("3.2")
    # flow_parameter = db.query(PlantFlowParameter).filter(PlantFlowParameter.plant_flow_parameter_id == log.plant_flow_parameter_id).first()
    if existing_log:
        # If a daily log exists, create a new flow parameter log entry
        print("4")
        new_log = FlowParameterLog(
                                    plant_flow_parameter_id =log.plant_flow_parameter_id, 
                                    plant_id=log.plant_id,
                                    shift=log.shift,
                                    inlet_value=log.value,
                                    outlet_value=log.outlet_value,
                                    daily_log_id=existing_log.log_id,
                                    parameter_name=plant_flow_parameter.parameter_name, 
                                    created_by=user_id,
                                    created_at=get_IST()  # Use the IST function to set created_at
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        print("5")
        return new_log
    else:
        # Create a daily log entry
        print("6")
        new_daily_log = DailyLog(plant_id=log.plant_id, shift=log.shift, created_by=user_id, created_at=get_IST())  # Use the IST function to set created_at
        db.add(new_daily_log)
        db.commit()

        print("7")
        # Creating a new flow parameter log entry
        new_log = FlowParameterLog(
                                    plant_flow_parameter_id =log.plant_flow_parameter_id, 
                                    plant_id=log.plant_id,
                                    shift=log.shift,
                                    inlet_value=log.value,
                                    outlet_value=log.outlet_value,
                                    parameter_name=plant_flow_parameter.parameter_name,
                                    daily_log_id=new_daily_log.log_id, 
                                    created_by=user_id,
                                    created_at=get_IST()  # Use the IST function to set created_at
        )
        db.add(new_log)
        db.commit()
        print("8")
        return new_log



def getFowParameterLogs(db: Session, log: FlowParameterLogSchema, user_id: int) -> List[FlowParameterLogSchema]:
    query = db.query(FlowParameterLog).filter(FlowParameterLog.del_flag == False)
    if log.plant_id is not None:
        query = query.filter(FlowParameterLog.plant_id == log.plant_id)
    if log.start_date is not None and log.end_date is not None:
        query = query.filter(func.date(EquipmentLog.created_at).between(log.start_date, log.end_date))
    elif log.start_date is not None:
        query = query.filter(func.date(EquipmentLog.created_at) >= log.start_date)
    elif log.end_date is not None:
        query = query.filter(func.date(EquipmentLog.created_at) <= log.end_date)
    flowparameterlogs = query.all()

    if not flowparameterlogs:
        return []
    return flowparameterlogs



def updateFlowParameterLogs(db: Session, log: FlowParameterLogSchema, user_id: int) -> List[FlowParameterLogSchema]:
    flow_parameter_log = db.query(FlowParameterLog).filter(FlowParameterLog.del_flag == False, FlowParameterLog.flow_parameter_log_id==log.flow_parameter_log_id).first()
    if not flow_parameter_log:
        raise HTTPException(status_code=404, detail="Logs not found")

    if log.value is not None:
        flow_parameter_log.inlet_value = log.value
    if log.outlet_value is not None:
        flow_parameter_log.outlet_value = log.outlet_value
    if log.shift is not None:
        flow_parameter_log.shift = log.shift
    flow_parameter_log.updated_at = get_IST()  # Use the IST function to set updated_at
    db.commit()
    db.refresh(flow_parameter_log)

    return flow_parameter_log

def deleteFlowParameterLog(db: Session, log: FlowParameterLogSchema) -> bool:
    flow_parameter_log = db.query(FlowParameterLog).filter(FlowParameterLog.del_flag == False, FlowParameterLog.flow_parameter_log_id == log.flow_parameter_log_id).first()
    if not flow_parameter_log:
        raise HTTPException(status_code=404, detail="Logs not found")
    flow_parameter_log.del_flag = True
    flow_parameter_log.updated_at = get_IST()  # Use the IST function to set updated_at
    db.commit()
    return True