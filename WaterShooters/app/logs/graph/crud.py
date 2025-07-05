
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.logs.graph.schema import (
    GraphDataRequest,
    GraphDataResponse,
    GraphDataPoint
)
from app.models.base import DailyLog, EquipmentLog, FlowParameterLog, ChemicalLog, PlantEquipment, PlantFlowParameter, PlantChemical, FlowLog
from fastapi import HTTPException
from typing import List




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
                    value=log.inlet_value,
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
