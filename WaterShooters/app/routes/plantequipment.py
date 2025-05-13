from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from app.database import get_db
from app.schemas.plant import PlantEquipmentSchema
from app.crud import plantequipment as crud_plantequipment
from app.routes.jwt import get_current_user

router = APIRouter(
    prefix="/plant-equipment",
    tags=["plant-equipment"]
)

@router.post("/create", response_model=PlantEquipmentSchema)
def create_plant_equipment(
    plant_equipment: PlantEquipmentSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new plant equipment"""
    return crud_plantequipment.create_plant_equipment(db=db, plant_equipment=plant_equipment)

@router.get("/{plant_equipment_id}", response_model=PlantEquipmentSchema)
def read_plant_equipment(
    plant_equipment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get plant equipment by ID"""
    db_plant_equipment = crud_plantequipment.get_plant_equipment(db, plant_equipment_id=plant_equipment_id)
    if db_plant_equipment is None:
        raise HTTPException(status_code=404, detail="Plant equipment not found")
    return db_plant_equipment

@router.get("/plant/{plant_id}", response_model=Dict[str, object])
def read_plant_equipments(
    plant_id: int,
    page: int = 1,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all equipment for a plant with pagination"""
    plant_equipments = crud_plantequipment.get_plant_equipments(
        db, plant_id=plant_id, page=page, limit=limit
    )
    return {
        "items": plant_equipments,
        "total": len(plant_equipments),
        "page": page,
        "limit": limit
    }

@router.put("/{plant_equipment_id}", response_model=PlantEquipmentSchema)
def update_plant_equipment(
    plant_equipment_id: int,
    plant_equipment: PlantEquipmentSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update plant equipment"""
    db_plant_equipment = crud_plantequipment.get_plant_equipment(db, plant_equipment_id=plant_equipment_id)
    if db_plant_equipment is None:
        raise HTTPException(status_code=404, detail="Plant equipment not found")
    return crud_plantequipment.update_plant_equipment(
        db=db, plant_equipment_id=plant_equipment_id, plant_equipment=plant_equipment
    )

@router.delete("/{plant_equipment_id}", response_model=Dict[str, str])
def delete_plant_equipment(
    plant_equipment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete plant equipment"""
    db_plant_equipment = crud_plantequipment.get_plant_equipment(db, plant_equipment_id=plant_equipment_id)
    if db_plant_equipment is None:
        raise HTTPException(status_code=404, detail="Plant equipment not found")
    crud_plantequipment.delete_plant_equipment(db=db, plant_equipment_id=plant_equipment_id)
    return {"detail": "Plant equipment deleted"}
