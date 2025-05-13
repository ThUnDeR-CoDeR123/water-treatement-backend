from sqlalchemy.orm import Session
from app.models.base import PlantChemical
from app.schemas.plant import PlantChemicalSchema
from datetime import datetime
from sqlalchemy import and_

def create_plant_chemical(db: Session, plant_chemical: PlantChemicalSchema):
    """Create a new plant chemical"""
    # Validate required fields
    if plant_chemical.plant_id is None:
        raise ValueError("plant_id is required")
    if plant_chemical.chemical_name is None:
        raise ValueError("chemical_name is required")
        
    db_plant_chemical = PlantChemical()
    
    # Set required fields
    db_plant_chemical.plant_id = plant_chemical.plant_id
    db_plant_chemical.chemical_name = plant_chemical.chemical_name
    db_plant_chemical.created_at = datetime.now()
    db_plant_chemical.updated_at = datetime.now()
    
    # Set optional fields if provided
    if plant_chemical.chemical_unit is not None:
        db_plant_chemical.chemical_unit = plant_chemical.chemical_unit
    if plant_chemical.quantity is not None:
        db_plant_chemical.quantity = plant_chemical.quantity
    
    db.add(db_plant_chemical)
    db.commit()
    db.refresh(db_plant_chemical)
    return db_plant_chemical

def get_plant_chemical(db: Session, plant_chemical_id: int):
    """Get plant chemical by ID"""
    return db.query(PlantChemical).filter(
        and_(
            PlantChemical.plant_chemical_id == plant_chemical_id,
            PlantChemical.del_flag == False
        )
    ).first()

def get_plant_chemicals(db: Session, plant_id: int, page: int = 1, limit: int = 100):
    """Get all chemicals for a plant with pagination"""
    skip = (page - 1) * limit
    return db.query(PlantChemical).filter(
        and_(
            PlantChemical.plant_id == plant_id,
            PlantChemical.del_flag == False
        )
    ).offset(skip).limit(limit).all()

def update_plant_chemical(db: Session, plant_chemical_id: int, plant_chemical: PlantChemicalSchema):
    """Update plant chemical"""
    db_plant_chemical = get_plant_chemical(db, plant_chemical_id)
    if db_plant_chemical:
        if plant_chemical.plant_id is not None:
            db_plant_chemical.plant_id = plant_chemical.plant_id
        if plant_chemical.chemical_name is not None:
            db_plant_chemical.chemical_name = plant_chemical.chemical_name
        if plant_chemical.chemical_unit is not None:
            db_plant_chemical.chemical_unit = plant_chemical.chemical_unit
        if plant_chemical.quantity is not None:
            db_plant_chemical.quantity = plant_chemical.quantity
            
        db_plant_chemical.updated_at = datetime.now()
        db.commit()
        db.refresh(db_plant_chemical)
    return db_plant_chemical

def delete_plant_chemical(db: Session, plant_chemical_id: int):
    """Soft delete plant chemical"""
    db_plant_chemical = get_plant_chemical(db, plant_chemical_id)
    if db_plant_chemical:
        db_plant_chemical.del_flag = True
        db_plant_chemical.updated_at = datetime.now()
        db.commit()
    return db_plant_chemical
