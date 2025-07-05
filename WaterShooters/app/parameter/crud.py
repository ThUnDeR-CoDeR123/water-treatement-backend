from sqlalchemy.orm import Session
from app.models.base import PlantFlowParameter
from app.parameter.schema import PlantFlowParameterSchema
from datetime import datetime
from sqlalchemy import and_

def create_plant_flow_parameter(db: Session, plant_flow_parameter: PlantFlowParameterSchema):
    """Create a new plant flow parameter"""
    # Validate required fields
    if plant_flow_parameter.plant_id is None:
        raise ValueError("plant_id is required")
    if plant_flow_parameter.parameter_name is None:
        raise ValueError("parameter_name is required")
        
    db_plant_flow_parameter = PlantFlowParameter()
    
    # Set required fields
    db_plant_flow_parameter.plant_id = plant_flow_parameter.plant_id
    db_plant_flow_parameter.parameter_name = plant_flow_parameter.parameter_name
    db_plant_flow_parameter.created_at = datetime.now()
    db_plant_flow_parameter.updated_at = datetime.now()
    
    # Set optional fields if provided
    if plant_flow_parameter.parameter_unit is not None:
        db_plant_flow_parameter.parameter_unit = plant_flow_parameter.parameter_unit
    if plant_flow_parameter.target_value is not None:
        db_plant_flow_parameter.target_value = plant_flow_parameter.target_value
    if plant_flow_parameter.tolerance is not None:
        db_plant_flow_parameter.tolerance = plant_flow_parameter.tolerance
    
    db.add(db_plant_flow_parameter)
    db.commit()
    db.refresh(db_plant_flow_parameter)
    return db_plant_flow_parameter

def get_plant_flow_parameter(db: Session, plant_flow_parameter_id: int):
    """Get plant flow parameter by ID"""
    return db.query(PlantFlowParameter).filter(
        and_(
            PlantFlowParameter.plant_flow_parameter_id == plant_flow_parameter_id,
            PlantFlowParameter.del_flag == False
        )
    ).first()

def get_plant_flow_parameters(db: Session, plant_id: int, page: int = 1, limit: int = 100):
    """Get all flow parameters for a plant with pagination"""
    skip = (page - 1) * limit
    return db.query(PlantFlowParameter).filter(
        and_(
            PlantFlowParameter.plant_id == plant_id,
            PlantFlowParameter.del_flag == False
        )
    ).offset(skip).limit(limit).all()

def update_plant_flow_parameter(db: Session, plant_flow_parameter_id: int, plant_flow_parameter: PlantFlowParameterSchema):
    """Update plant flow parameter"""
    db_plant_flow_parameter = get_plant_flow_parameter(db, plant_flow_parameter_id)
    if db_plant_flow_parameter:
        if plant_flow_parameter.plant_id is not None:
            db_plant_flow_parameter.plant_id = plant_flow_parameter.plant_id
        if plant_flow_parameter.parameter_name is not None:
            db_plant_flow_parameter.parameter_name = plant_flow_parameter.parameter_name
        if plant_flow_parameter.parameter_unit is not None:
            db_plant_flow_parameter.parameter_unit = plant_flow_parameter.parameter_unit
        if plant_flow_parameter.target_value is not None:
            db_plant_flow_parameter.target_value = plant_flow_parameter.target_value
        if plant_flow_parameter.tolerance is not None:
            db_plant_flow_parameter.tolerance = plant_flow_parameter.tolerance
            
        db_plant_flow_parameter.updated_at = datetime.now()
        db.commit()
        db.refresh(db_plant_flow_parameter)
    return db_plant_flow_parameter

def delete_plant_flow_parameter(db: Session, plant_flow_parameter_id: int):
    """Soft delete plant flow parameter"""
    db_plant_flow_parameter = get_plant_flow_parameter(db, plant_flow_parameter_id)
    if db_plant_flow_parameter:
        db_plant_flow_parameter.del_flag = True
        db_plant_flow_parameter.updated_at = datetime.now()
        db.commit()
    return db_plant_flow_parameter
