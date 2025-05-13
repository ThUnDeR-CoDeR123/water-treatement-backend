from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from app.database import get_db
from app.schemas.plant import PlantFlowParameterSchema
from app.crud import plantflowparameter as crud_plantflowparameter
from app.routes.jwt import get_current_user

router = APIRouter(
    prefix="/plant-flow-parameter",
    tags=["plant-flow-parameter"]
)

@router.post("/create", response_model=PlantFlowParameterSchema)
def create_plant_flow_parameter(
    plant_flow_parameter: PlantFlowParameterSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new plant flow parameter"""
    return crud_plantflowparameter.create_plant_flow_parameter(db=db, plant_flow_parameter=plant_flow_parameter)

@router.get("/{plant_flow_parameter_id}")
def read_plant_flow_parameter(
    plant_flow_parameter_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get plant flow parameter by ID"""
    db_plant_flow_parameter = crud_plantflowparameter.get_plant_flow_parameter(
        db, plant_flow_parameter_id=plant_flow_parameter_id
    )
    if db_plant_flow_parameter is None:
        raise HTTPException(status_code=404, detail="Plant flow parameter not found")
    return db_plant_flow_parameter

@router.get("/plant/{plant_id}")
def read_plant_flow_parameters(
    plant_id: int,
    page: int = 1,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all flow parameters for a plant with pagination"""
    plant_flow_parameters = crud_plantflowparameter.get_plant_flow_parameters(
        db, plant_id=plant_id, page=page, limit=limit
    )
    return plant_flow_parameters

@router.put("/{plant_flow_parameter_id}")
def update_plant_flow_parameter(
    plant_flow_parameter_id: int,
    plant_flow_parameter: PlantFlowParameterSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update plant flow parameter"""
    db_plant_flow_parameter = crud_plantflowparameter.get_plant_flow_parameter(
        db, plant_flow_parameter_id=plant_flow_parameter_id
    )
    if db_plant_flow_parameter is None:
        raise HTTPException(status_code=404, detail="Plant flow parameter not found")
    return crud_plantflowparameter.update_plant_flow_parameter(
        db=db, 
        plant_flow_parameter_id=plant_flow_parameter_id, 
        plant_flow_parameter=plant_flow_parameter
    )

@router.delete("/{plant_flow_parameter_id}")
def delete_plant_flow_parameter(
    plant_flow_parameter_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete plant flow parameter"""
    db_plant_flow_parameter = crud_plantflowparameter.get_plant_flow_parameter(
        db, plant_flow_parameter_id=plant_flow_parameter_id
    )
    if db_plant_flow_parameter is None:
        raise HTTPException(status_code=404, detail="Plant flow parameter not found")
    crud_plantflowparameter.delete_plant_flow_parameter(
        db=db, plant_flow_parameter_id=plant_flow_parameter_id
    )
    return {"detail": "Plant flow parameter deleted"}
