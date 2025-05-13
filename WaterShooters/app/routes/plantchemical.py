from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from app.database import get_db
from app.schemas.plant import (
    PlantChemicalSchema, PlantChemicalCreate, 
    PlantChemicalUpdate, PlantChemicalInDB
)
from app.crud import plantchemical as crud_plantchemical
from app.routes.jwt import get_current_user

router = APIRouter(
    prefix="/plant-chemical",
    tags=["plant-chemical"]
)

@router.post("/create")
def create_plant_chemical(
    plant_chemical: PlantChemicalCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new plant chemical"""
    try:
        return crud_plantchemical.create_plant_chemical(db=db, plant_chemical=plant_chemical)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{plant_chemical_id}")
def read_plant_chemical(
    plant_chemical_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get plant chemical by ID"""
    db_plant_chemical = crud_plantchemical.get_plant_chemical(db, plant_chemical_id=plant_chemical_id)
    if db_plant_chemical is None:
        raise HTTPException(status_code=404, detail="Plant chemical not found")
    return db_plant_chemical

@router.get("/plant/{plant_id}")
def read_plant_chemicals(
    plant_id: int,
    page: int = 1,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all chemicals for a plant with pagination"""
    plant_chemicals = crud_plantchemical.get_plant_chemicals(
        db, plant_id=plant_id, page=page, limit=limit
    )
    return plant_chemicals

@router.put("/update")
def update_plant_chemical(
    plant_chemical_id: int,
    plant_chemical: PlantChemicalSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update plant chemical"""
    db_plant_chemical = crud_plantchemical.get_plant_chemical(db, plant_chemical_id=plant_chemical.plant_chemical_id)
    if db_plant_chemical is None:
        raise HTTPException(status_code=404, detail="Plant chemical not found")
    return crud_plantchemical.update_plant_chemical(
        db=db, plant_chemical_id=plant_chemical_id, plant_chemical=plant_chemical
    )

@router.delete("/{plant_chemical_id}", response_model=Dict[str, str])
def delete_plant_chemical(
    plant_chemical_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete plant chemical"""
    db_plant_chemical = crud_plantchemical.get_plant_chemical(db, plant_chemical_id=plant_chemical_id)
    if db_plant_chemical is None:
        raise HTTPException(status_code=404, detail="Plant chemical not found")
    crud_plantchemical.delete_plant_chemical(db=db, plant_chemical_id=plant_chemical_id)
    return {"detail": "Plant chemical deleted"}
