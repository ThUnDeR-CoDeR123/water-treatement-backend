from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from app.database import get_db
from app.parameter.schema import PlantFlowParameterSchema
from app.parameter import  crud
from app.auth.jwt import get_current_user

flowParameterRouter = APIRouter(
    prefix="/plant-flow-parameter",
    tags=["plant-flow-parameter"]
)

@flowParameterRouter.post("/create", response_model=PlantFlowParameterSchema)
def create_plant_flow_parameter(
    plant_flow_parameter: PlantFlowParameterSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new plant flow parameter"""
    return crud.create_plant_flow_parameter(db=db, plant_flow_parameter=plant_flow_parameter)

@flowParameterRouter.get("/{plant_flow_parameter_id}")
def read_plant_flow_parameter(
    plant_flow_parameter_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get plant flow parameter by ID"""
    db_plant_flow_parameter = crud.get_plant_flow_parameter(
        db, plant_flow_parameter_id=plant_flow_parameter_id
    )
    if db_plant_flow_parameter is None:
        raise HTTPException(status_code=404, detail="Plant flow parameter not found")
    return db_plant_flow_parameter

@flowParameterRouter.get("/plant/{plant_id}")
def read_plant_flow_parameters(
    plant_id: int,
    page: int = 1,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all flow parameters for a plant with pagination"""
    plant_flow_parameters = crud.get_plant_flow_parameters(
        db, plant_id=plant_id, page=page, limit=limit
    )
    return plant_flow_parameters

@flowParameterRouter.put("/update")
def update_plant_flow_parameter(
    plant_flow_parameter: PlantFlowParameterSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update plant flow parameter"""
    plant_flow_parameter_id = plant_flow_parameter.plant_flow_parameter_id
    if plant_flow_parameter_id is None:
        raise HTTPException(status_code=400, detail="plant_flow_parameter_id is required")
    db_plant_flow_parameter = crud.get_plant_flow_parameter(
        db, plant_flow_parameter_id=plant_flow_parameter_id
    )
    if db_plant_flow_parameter is None:
        raise HTTPException(status_code=404, detail="Plant flow parameter not found")
    return crud.update_plant_flow_parameter(
        db=db, 
        plant_flow_parameter_id=plant_flow_parameter_id, 
        plant_flow_parameter=plant_flow_parameter
    )

@flowParameterRouter.delete("/{plant_flow_parameter_id}")
def delete_plant_flow_parameter(
    plant_flow_parameter_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete plant flow parameter"""
    db_plant_flow_parameter =   crud.get_plant_flow_parameter(
        db, plant_flow_parameter_id=plant_flow_parameter_id
    )
    if db_plant_flow_parameter is None:
        raise HTTPException(status_code=404, detail="Plant flow parameter not found")
    crud.delete_plant_flow_parameter(
        db=db, plant_flow_parameter_id=plant_flow_parameter_id
    )
    return {"detail": "Plant flow parameter deleted"}
