from sqlalchemy.orm import Session
from app.models.base import PlantEquipment
from app.equipment.schema import PlantEquipmentSchema
from datetime import datetime
from sqlalchemy import and_

def create_plant_equipment(db: Session, plant_equipment: PlantEquipmentSchema):
    """Create a new plant equipment"""
    # Validate required fields
    if plant_equipment.plant_id is None:
        raise ValueError("plant_id is required")
    if plant_equipment.equipment_name is None:
        raise ValueError("equipment_name is required")
        
    db_plant_equipment = PlantEquipment()
    
    # Set required fields
    db_plant_equipment.plant_id = plant_equipment.plant_id
    db_plant_equipment.equipment_name = plant_equipment.equipment_name
    db_plant_equipment.created_at = datetime.now()
    db_plant_equipment.updated_at = datetime.now()
    
    # Set optional fields if provided
    if plant_equipment.equipment_type is not None:
        db_plant_equipment.equipment_type = plant_equipment.equipment_type
    if plant_equipment.last_maintenance is not None:
        db_plant_equipment.last_maintenance = plant_equipment.last_maintenance
    if plant_equipment.status is not None:
        db_plant_equipment.status = plant_equipment.status
    
    db.add(db_plant_equipment)
    db.commit()
    db.refresh(db_plant_equipment)
    return db_plant_equipment

def get_plant_equipment(db: Session, plant_equipment_id: int):
    """Get plant equipment by ID"""
    return db.query(PlantEquipment).filter(
        and_(
            PlantEquipment.plant_equipment_id == plant_equipment_id,
            PlantEquipment.del_flag == False
        )
    ).first()

def get_plant_equipments(db: Session, plant_id: int, page: int = 1, limit: int = 100):
    """Get all equipment for a plant with pagination"""
    skip = (page - 1) * limit
    return db.query(PlantEquipment).filter(
        and_(
            PlantEquipment.plant_id == plant_id,
            PlantEquipment.del_flag == False
        )
    ).offset(skip).limit(limit).all()

def update_plant_equipment(db: Session, plant_equipment_id: int, plant_equipment: PlantEquipmentSchema):
    """Update plant equipment"""
    db_plant_equipment = get_plant_equipment(db, plant_equipment_id)
    if db_plant_equipment:
        if plant_equipment.plant_id is not None:
            db_plant_equipment.plant_id = plant_equipment.plant_id
        if plant_equipment.equipment_name is not None:
            db_plant_equipment.equipment_name = plant_equipment.equipment_name
        if plant_equipment.equipment_type is not None:
            db_plant_equipment.equipment_type = plant_equipment.equipment_type
        if plant_equipment.last_maintenance is not None:
            db_plant_equipment.last_maintenance = plant_equipment.last_maintenance
        if plant_equipment.status is not None:
            db_plant_equipment.status = plant_equipment.status
            
        db_plant_equipment.updated_at = datetime.now()
        db.commit()
        db.refresh(db_plant_equipment)
    return db_plant_equipment

def delete_plant_equipment(db: Session, plant_equipment_id: int):
    """Soft delete plant equipment"""
    db_plant_equipment = get_plant_equipment(db, plant_equipment_id)
    if db_plant_equipment:
        db_plant_equipment.del_flag = True
        db_plant_equipment.updated_at = datetime.now()
        db.commit()
    return db_plant_equipment