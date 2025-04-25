from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Annotated
from app.crud.plant import (
    createPlant,
    getPlantById,
    getAllPlants,
    updatePlant,
    deletePlant,
    getPlantsByPlantTypeId,
    getAllPlantTypes
)
from app.schemas.plant import PlantSchema, PlantTypeSchema
from app.database import get_db
from app.models.base import User, PlantType
from app.routes.jwt import get_current_user,getAdmin

plantrouter = APIRouter(prefix="/api/v1/plant", tags=["Plant"])

# Create a new plant
@plantrouter.post("/createplant", response_model=PlantSchema)
def create_plant(
    plant: PlantSchema,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(getAdmin)]
):
    # Only admins can create plants

    return createPlant(db, plant)

# Get a single plant by ID
@plantrouter.get("/getplant/{plant_id}", response_model=PlantSchema)
def get_plant_by_id(
    plant_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    "Since it is been accessed by id no need to chk for the user who is aksing for it"
    return getPlantById(db, plant_id)


@plantrouter.get("/getplant/plantype/{plant_type_id}", response_model=List[PlantSchema])
def get_plant_by_type(
    plant_type_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return getPlantsByPlantTypeId(db, plant_type_id,current_user)

# Get all plants with optional filters
@plantrouter.get("/getallplants", response_model=List[PlantSchema])
def get_all_plants(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    plant: Optional[PlantSchema] = None
):
    # Ensure correct arguments are passed to getAllPlants
    return getAllPlants(
        db=db,
        plant=plant,
        current_user =current_user
    )

# Update a plant
@plantrouter.put("/updateplant/{plant_id}", response_model=PlantSchema)
def update_plant(
    plant_id: int,
    plant: PlantSchema,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    # Only admins can update plants
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")
    return updatePlant(db, plant_id, plant)

# Soft delete a plant
@plantrouter.delete("/deleteplant/{plant_id}")
def delete_plant(
    plant_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    # Only admins can delete plants
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")
    deletePlant(db, plant_id)
    return {"message": "Plant deleted successfully"}

@plantrouter.get("/types", response_model=List[PlantTypeSchema])
def get_plant_types(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get all plant types"""
    return getAllPlantTypes(db)