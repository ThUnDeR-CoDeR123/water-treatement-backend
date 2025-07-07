
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.logs.flow.schema import FlowLogSchema
from app.models.base import DailyLog, EquipmentLog, FlowLog
from fastapi import HTTPException
from typing import List
from datetime import datetime, timedelta, timezone


def get_IST():
    """Get current time in Indian Standard Time (IST)"""
    return datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)


def create_flow_log(db: Session, log: FlowLogSchema, user_id: int):
    # First check for existing daily log
    query = db.query(DailyLog).filter(DailyLog.del_flag == False)
    if log.plant_id is not None:
        query = query.filter(DailyLog.plant_id == log.plant_id)
    if user_id is not None:
        query = query.filter(DailyLog.created_by == user_id)
    if log.shift is not None:
        query = query.filter(DailyLog.shift == log.shift)
    else:
        log.shift = 0
    query = query.filter(func.date(DailyLog.created_at) == func.date(get_IST()))  # Compare only date, not time
    existing_log = query.first()
    
    if existing_log:
        # If a daily log exists, create a new flow log entry
        new_log = FlowLog(
            plant_id=log.plant_id,
            daily_log_id=existing_log.log_id,
            inlet_value=log.inlet_value,
            outlet_value=log.outlet_value,
            inlet_image=log.inlet_image,
            outlet_image=log.outlet_image,
            shift=log.shift,
            created_by=user_id,
            created_at=get_IST()  # Use the IST function to set created_at
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return new_log
    else:
        # Create a daily log entry first
        new_daily_log = DailyLog(
            plant_id=log.plant_id,
            shift=log.shift,
            created_by=user_id,
            created_at=get_IST()  # Use the IST function to set created_at
        )
        db.add(new_daily_log)
        db.commit()

        # Then create the flow log entry
        new_log = FlowLog(
            plant_id=log.plant_id,
            daily_log_id=new_daily_log.log_id,
            inlet_value=log.inlet_value,
            outlet_value=log.outlet_value,
            inlet_image=log.inlet_image,
            outlet_image=log.outlet_image,
            shift=log.shift,
            created_by=user_id,
            created_at=get_IST()
        )
        db.add(new_log)
        db.commit()
        return new_log

def get_flow_logs(db: Session, log: FlowLogSchema) -> List[FlowLog]:
    print("Debug - Input parameters:", {
        "plant_id": log.plant_id,
        "start_date": log.start_date,
        "end_date": log.end_date,
        "shift": log.shift
    })
    
    query = db.query(FlowLog).filter(FlowLog.del_flag == False)
    if log.plant_id is not None:
        query = query.filter(FlowLog.plant_id == log.plant_id)
    if log.start_date is not None and log.end_date is not None:
        query = query.filter(func.date(EquipmentLog.created_at).between(log.start_date, log.end_date))
    elif log.start_date is not None:
        query = query.filter(func.date(EquipmentLog.created_at) >= log.start_date)
    elif log.end_date is not None:
        query = query.filter(func.date(EquipmentLog.created_at) <= log.end_date)
    if log.created_at is not None:
        query = query.filter(func.date(FlowLog.created_at) == func.date(log.created_at))
    if log.shift is not None:
        query = query.filter(FlowLog.shift == log.shift)
        
    # Print the SQL query being generated
    print("Debug - SQL Query:", str(query))
    
    flow_logs = query.all()
    print("Debug - Number of results:", len(flow_logs))
    if flow_logs:
        print("Debug - First result:", flow_logs[0].__dict__)

    return flow_logs

def update_flow_log(db: Session, log: FlowLogSchema) -> FlowLog:
    flow_log = db.query(FlowLog).filter(
        FlowLog.flow_log_id == log.flow_log_id,
        FlowLog.del_flag == False
    ).first()
    if not flow_log:
        raise HTTPException(status_code=404, detail="Flow log not found")

    if log.inlet_value is not None:
        flow_log.inlet_value = log.inlet_value
    if log.outlet_value is not None:
        flow_log.outlet_value = log.outlet_value
    if log.inlet_image is not None:
        flow_log.inlet_image = log.inlet_image
    if log.outlet_image is not None:
        flow_log.outlet_image = log.outlet_image
    if log.shift is not None:
        flow_log.shift = log.shift
    
    flow_log.updated_at = get_IST()  # Use the IST function to set updated_at
    db.commit()
    db.refresh(flow_log)
    return flow_log

def delete_flow_log(db: Session, log: FlowLogSchema) -> bool:
    flow_log = db.query(FlowLog).filter(
        FlowLog.flow_log_id == log.flow_log_id,
        FlowLog.del_flag == False
    ).first()
    if not flow_log:
        raise HTTPException(status_code=404, detail="Flow log not found")
    flow_log.del_flag = True
    flow_log.updated_at = get_IST()  # Use the IST function to set updated_at
    db.commit()
    return True
