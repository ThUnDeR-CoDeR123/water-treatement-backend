from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.schemas.logs import (
    FlowParameterLogSchema, 
    EquipmentLogSchema, 
    ChemicalLogSchema, 
    DailyLogSchema,
    FlowLogSchema,
    GraphDataRequest,
    GraphDataResponse,
    GraphDataPoint
)
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
                               daily_log_id=existing_log.log_id, 
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
                                    inlet_value=log.value,
                                    outlet_value=log.outlet_value,
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
                                    inlet_value=log.value,
                                    outlet_value=log.outlet_value,
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
        if log.incomming_quantity:
            plant_chemical.quantity+=log.incomming_quantity
        plant_chemical.quantity-=log.quantity_used
        new_log = ChemicalLog(
            plant_chemical_id =plant_chemical.plant_chemical_id, 
            plant_id= log.plant_id,
            shift=log.shift,
            quantity_left=plant_chemical.quantity,
            quantity_used=log.quantity_used,
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
            sludge_discharge=log.sludge_discharge,
            daily_log_id=new_daily_log.log_id, 
            created_by=user_id)
        

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
        return []
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
        return []
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
        return []
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
    else:
        log.shift = 0
    query = query.filter(func.date(DailyLog.created_at) == func.date(func.now()))  # Compare only date, not time
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
            inlet_image=log.inlet_image,
            outlet_image=log.outlet_image,
            shift=log.shift,
            created_by=user_id
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
    if log.start_date is not None:
        query = query.filter(FlowLog.created_at >= log.start_date)
    if log.end_date is not None:
        query = query.filter(FlowLog.created_at <= log.end_date)
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
    plant_chemical = db.query(PlantChemical).filter(PlantChemical.plant_chemical_id==chemical_log.plant_chemical_id).first()
    if not chemical_log:
        raise HTTPException(status_code=404, detail="Logs not found")
    if log.incomming_quantity:
            plant_chemical.quantity+=log.incomming_quantity
    plant_chemical.quantity-=log.quantity_used
    plant_chemical.quantity+=chemical_log.quantity_used
    if log.quantity_used is not None:
        chemical_log.quantity_used = log.quantity_used
    if log.quantity_left is not None:
        chemical_log.quantity_left = plant_chemical.quantity
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
        flow_parameter_log.inlet_value = log.value
    if log.outlet_value is not None:
        flow_parameter_log.outlet_value = log.outlet_value
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

def get_graph_data(db: Session, request: GraphDataRequest) -> List[GraphDataResponse]:
    """Fetch log data for graphing based on time range and log type"""
    series = []

    if request.log_type == "flowparameter":
        parameters = (db.query(PlantFlowParameter)
                    .filter(PlantFlowParameter.plant_id == request.plant_id,
                           PlantFlowParameter.del_flag == False)
                    .all())
        
        for param in parameters:
            param_name = param.parameter_name
            data_points = []
            logs = (db.query(FlowParameterLog)
                   .filter(FlowParameterLog.plant_id == request.plant_id,
                          FlowParameterLog.plant_flow_parameter_id == param.plant_flow_parameter_id,
                          func.date(FlowParameterLog.created_at).between(request.start_date, request.end_date),
                          FlowParameterLog.del_flag == False)
                   .order_by(FlowParameterLog.created_at)
                   .all())
            
            for log in logs:                
                data_points.append(GraphDataPoint(
                    timestamp=log.created_at.date(),
                    value=log.value,
                    parameter_name=param_name
                ))
            
            if data_points:
                series.append(GraphDataResponse(
                    series_name=f"Flow Parameter: {param_name}",
                    data=data_points
                ))

    elif request.log_type == "chemical-used":
        chemicals = (db.query(PlantChemical)
                   .filter(PlantChemical.plant_id == request.plant_id,
                          PlantChemical.del_flag == False)
                   .all())
        
        for chem in chemicals:
            chem_name = chem.chemical_name
            data_points = []
            logs = (db.query(ChemicalLog)
                   .filter(ChemicalLog.plant_id == request.plant_id,
                          ChemicalLog.plant_chemical_id == chem.plant_chemical_id,
                          func.date(ChemicalLog.created_at).between(request.start_date, request.end_date),
                          ChemicalLog.del_flag == False)
                   .order_by(ChemicalLog.created_at)
                   .all())
            
            for log in logs:
                # Add quantity left data point
                # if log.quantity_left is not None:
                #     data_points.append(GraphDataPoint(
                #         timestamp=log.created_at,
                #         value=log.quantity_left,
                #         parameter_name=f"{chem_name} (Quantity Left)"
                #     ))
                # Add quantity used data point
                if log.quantity_used is not None:                    
                    data_points.append(GraphDataPoint(
                        timestamp=log.created_at.date(),
                        value=log.quantity_used,
                        parameter_name=f"{chem_name} (Used)"
                    ))
            
            if data_points:
                series.append(GraphDataResponse(
                    series_name=f"Chemical: {chem_name}",
                    data=data_points
                ))
    elif request.log_type == "chemical-left":
        chemicals = (db.query(PlantChemical)
                   .filter(PlantChemical.plant_id == request.plant_id,
                          PlantChemical.del_flag == False)
                   .all())
        
        for chem in chemicals:
            chem_name = chem.chemical_name
            data_points = []
            logs = (db.query(ChemicalLog)
                   .filter(ChemicalLog.plant_id == request.plant_id,
                          ChemicalLog.plant_chemical_id == chem.plant_chemical_id,
                          func.date(ChemicalLog.created_at).between(request.start_date, request.end_date),
                          ChemicalLog.del_flag == False)
                   .order_by(ChemicalLog.created_at)
                   .all())
            
            for log in logs:
                # Add quantity left data point
                if log.quantity_left is not None:                    
                    data_points.append(GraphDataPoint(
                        timestamp=log.created_at.date(),
                        value=log.quantity_left,
                        parameter_name=f"{chem_name} (Quantity Left)"
                    ))
                # Add quantity used data point
                # if log.quantity_used is not None:
                #     data_points.append(GraphDataPoint(
                #         timestamp=log.created_at,
                #         value=log.quantity_used,
                #         parameter_name=f"{chem_name} (Used)"
                #     ))
            
            if data_points:
                series.append(GraphDataResponse(
                    series_name=f"Chemical: {chem_name}",
                    data=data_points
                ))

    elif request.log_type == "equipment":
        equipments = (db.query(PlantEquipment)
                    .filter(PlantEquipment.plant_id == request.plant_id,
                           PlantEquipment.del_flag == False)
                    .all())
        
        for equip in equipments:
            equip_name = equip.equipment_name
            data_points = []
            logs = (db.query(EquipmentLog)
                   .filter(EquipmentLog.plant_id == request.plant_id,
                          EquipmentLog.plant_equipment_id == equip.plant_equipment_id,
                          func.date(EquipmentLog.created_at).between(request.start_date, request.end_date),
                          EquipmentLog.del_flag == False)
                   .order_by(EquipmentLog.created_at)
                   .all())
            
            for log in logs:                
                data_points.append(GraphDataPoint(
                    timestamp=log.created_at.date(),
                    value=log.equipment_status,
                    parameter_name=equip_name
                ))
            
            if data_points:
                series.append(GraphDataResponse(
                    series_name=f"Equipment Status: {equip_name}",
                    data=data_points
                ))

    elif request.log_type == "flow":
        # For flow logs, we'll create two series: inlet and outlet values
        inlet_points = []
        outlet_points = []
        
        logs = (db.query(FlowLog)
               .filter(FlowLog.plant_id == request.plant_id,                      func.date(FlowLog.created_at).between(request.start_date, request.end_date),
                      FlowLog.del_flag == False)
               .order_by(FlowLog.created_at)
               .all())
        
        for log in logs:
            if log.inlet_value is not None:                
                inlet_points.append(GraphDataPoint(
                    timestamp=log.created_at.date(),
                    value=log.inlet_value,
                    parameter_name="Inlet Value"
                ))
            if log.outlet_value is not None:                
                outlet_points.append(GraphDataPoint(
                    timestamp=log.created_at.date(),
                    value=log.outlet_value,
                    parameter_name="Outlet Value"
                ))
        
        if inlet_points:
            series.append(GraphDataResponse(
                series_name="Inlet Value",
                data=inlet_points
            ))
        if outlet_points:
            series.append(GraphDataResponse(
                series_name="Outlet Value",
                data=outlet_points
            ))

    return series
