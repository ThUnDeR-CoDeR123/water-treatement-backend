from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.schemas.logs import EquipmentLogSchema, FlowParameterLogSchema, ChemicalLogSchema, FlowLogSchema
from app.models.base import DailyLog, EquipmentLog, FlowParameterLog, ChemicalLog, PlantEquipment, PlantFlowParameter, PlantChemical, FlowLog
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
        new_log = EquipmentLog(plant_id=plant_equipment.plant_id, 
                               shift=log.shift,
                               plant_equipment_id=log.plant_equipment_id,
                               equipment_status=log.equipment_status,
                               maintenance_done=log.maintenance_done,
                               daily_log_id=new_daily_log.log_id, 
                               created_by=user_id)
        print("after inserting new equipment log")
        plant_equipment.status = log.equipment_status
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return new_log
    else:
        print("inside non existing log")
        # Create a daily log entry
        new_daily_log = DailyLog(plant_id=plant_equipment.plant_id, shift=log.shift, created_by=user_id)
        print("after inserting new log daily log")
        db.add(new_daily_log)
        db.commit()

        # Creating a new equipment log entry
        new_log = EquipmentLog(plant_id=plant_equipment.plant_id, 
                               shift=log.shift,
                               plant_equipment_id=log.plant_equipment_id,
                               equipment_status=log.equipment_status,
                               maintenance_done=log.maintenance_done,
                               daily_log_id=new_daily_log.log_id, 
                               created_by=user_id)
        plant_equipment.status = log.equipment_status
        db.add(new_log)
        db.commit()
        return new_log


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
    query = query.filter(func.date(DailyLog.created_at) == func.date(func.now()))  # Compare only date, not time
    existing_log = query.first()
    print("3.2")

    if existing_log:
        # If a daily log exists, create a new flow parameter log entry
        print("4")
        new_log = FlowParameterLog(
                                    plant_flow_parameter_id =log.plant_flow_parameter_id, 
                                    plant_id=log.plant_id,
                                    shift=log.shift,
                                    value=log.value,
                                    daily_log_id=existing_log.log_id, 
                                    created_by=user_id)
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        print("5")
        return new_log
    else:
        # Create a daily log entry
        print("6")
        new_daily_log = DailyLog(plant_id=log.plant_id, shift=log.shift, created_by=user_id)
        db.add(new_daily_log)
        db.commit()

        print("7")
        # Creating a new flow parameter log entry
        new_log = FlowParameterLog(
                                    plant_flow_parameter_id =log.plant_flow_parameter_id, 
                                    plant_id=log.plant_id,
                                    shift=log.shift,
                                    value=log.value,
                                    daily_log_id=new_daily_log.log_id, 
                                    created_by=user_id)
        db.add(new_log)
        db.commit()
        print("8")
        return new_log


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
        new_log = ChemicalLog(
            plant_chemical_id =plant_chemical.plant_chemical_id, 
            plant_id= log.plant_id,
            shift=log.shift,
            quantity_left=log.quantity_left,
            quantity_consumed=log.quantity_used,
            sludge_discharge=log.sludge_discharge,
            daily_log_id=existing_log.log_id, 
            created_by=user_id)
        plant_chemical.quantity= log.quantity_left
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return new_log
    else:
        # Create a daily log entry
        new_daily_log = DailyLog(plant_id=plant_chemical.plant_id, shift=log.shift, created_by=user_id)
        db.add(new_daily_log)
        db.commit()

        # Creating a new chemical log entry
        new_log = ChemicalLog(
            plant_chemical_id =plant_chemical.plant_chemical_id, 
            plant_id= log.plant_id,
            shift=log.shift,
            quantity_left=log.quantity_left,
            quantity_consumed=log.quantity_used,
            sludge_discharge=log.sludge_discharge,
            daily_log_id=new_daily_log.log_id, 
            created_by=user_id)
        plant_chemical.quantity= log.quantity_left

        db.add(new_log)
        db.commit()
        return new_log

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

def create_flow_log(db: Session, log: FlowLogSchema, user_id: int):
    # First check for existing daily log
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
        # If a daily log exists, create a new flow log entry
        new_log = FlowLog(
            plant_id=log.plant_id,
            daily_log_id=existing_log.log_id,
            inlet_value=log.inlet_value,
            outlet_value=log.outlet_value,
            shift=log.shift,
            created_by=user_id
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
            created_by=user_id
        )
        db.add(new_daily_log)
        db.commit()

        # Then create the flow log entry
        new_log = FlowLog(
            plant_id=log.plant_id,
            daily_log_id=new_daily_log.log_id,
            inlet_value=log.inlet_value,
            outlet_value=log.outlet_value,
            shift=log.shift,
            created_by=user_id
        )
        db.add(new_log)
        db.commit()
        return new_log

def get_flow_logs(db: Session, log: FlowLogSchema) -> List[FlowLog]:
    query = db.query(FlowLog).filter(FlowLog.del_flag == False)
    if log.plant_id is not None:
        query = query.filter(FlowLog.plant_id == log.plant_id)
    if log.start_date is not None:
        query = query.filter(FlowLog.created_at >= log.start_date)
    if log.end_date is not None:
        query = query.filter(FlowLog.created_at <= log.end_date)
    if log.shift is not None:
        query = query.filter(FlowLog.shift == log.shift)
    flow_logs = query.all()
    if not flow_logs:
        raise HTTPException(status_code=404, detail="Flow logs not found")
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
    if log.shift is not None:
        flow_log.shift = log.shift
        
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
    db.commit()
    return True

def updateChemicalLogs(db: Session, log: ChemicalLogSchema, user_id: int) -> List[ChemicalLogSchema]:
    chemical_log = db.query(ChemicalLog).filter(ChemicalLog.del_flag == False, ChemicalLog.chemical_log_id==log.chemical_log_id).first()
    if not chemical_log:
        raise HTTPException(status_code=404, detail="Logs not found")

    if log.quantity_used is not None:
        chemical_log.quantity_used = log.quantity_used
    if log.quantity_left is not None:
        chemical_log.quantity_left = log.quantity_left
    if log.sludge_discharge is not None:
        chemical_log.sludge_discharge = log.sludge_discharge
    if log.shift is not None:
        chemical_log.shift = log.shift
    db.commit()
    db.refresh(chemical_log)

    return chemical_log

def updateEquipmentLogs(db: Session, log: EquipmentLogSchema, user_id: int) -> List[EquipmentLogSchema]:
    equipment_log = db.query(EquipmentLog).filter(EquipmentLog.del_flag == False, EquipmentLog.equipment_log_id==log.equipment_log_id).first()
    if not equipment_log:
        raise HTTPException(status_code=404, detail="Logs not found")

    if log.equipment_status is not None:
        equipment_log.equipment_status = log.equipment_status
    if log.maintenance_done is not None:
        equipment_log.maintenance_done = log.maintenance_done
    if log.shift is not None:
        equipment_log.shift = log.shift
    db.commit()
    db.refresh(equipment_log)

    return equipment_log

def updateFlowParameterLogs(db: Session, log: FlowParameterLogSchema, user_id: int) -> List[FlowParameterLogSchema]:
    flow_parameter_log = db.query(FlowParameterLog).filter(FlowParameterLog.del_flag == False, FlowParameterLog.flow_parameter_log_id==log.flow_parameter_log_id).first()
    if not flow_parameter_log:
        raise HTTPException(status_code=404, detail="Logs not found")

    if log.value is not None:
        flow_parameter_log.value = log.value
    if log.shift is not None:
        flow_parameter_log.shift = log.shift
    db.commit()
    db.refresh(flow_parameter_log)

    return flow_parameter_log

def deleteEquipmentLog(db: Session, log: EquipmentLogSchema) -> bool:
    equipment_log = db.query(EquipmentLog).filter(EquipmentLog.del_flag == False, EquipmentLog.equipment_log_id == log.equipment_log_id).first()
    if not equipment_log:
        raise HTTPException(status_code=404, detail="Logs not found")
    equipment_log.del_flag = True
    db.commit()
    return True

def deleteChemicalLog(db: Session, log: ChemicalLogSchema) -> bool:
    chemical_log = db.query(ChemicalLog).filter(ChemicalLog.del_flag == False, ChemicalLog.chemical_log_id == log.chemical_log_id).first()
    if not chemical_log:
        raise HTTPException(status_code=404, detail="Logs not found")
    chemical_log.del_flag = True
    db.commit()
    return True

def deleteFlowParameterLog(db: Session, log: FlowParameterLogSchema) -> bool:
    flow_parameter_log = db.query(FlowParameterLog).filter(FlowParameterLog.del_flag == False, FlowParameterLog.flow_parameter_log_id == log.flow_parameter_log_id).first()
    if not flow_parameter_log:
        raise HTTPException(status_code=404, detail="Logs not found")
    flow_parameter_log.del_flag = True
    db.commit()
    return True
