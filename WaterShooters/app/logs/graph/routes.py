
from fastapi import APIRouter, Depends, HTTPException,UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.logs.graph import crud
from app.logs.graph.schema import (
    GraphDataRequest,
    GraphDataSeriesResponse
)
from app.database import get_db
from app.auth.jwt import get_current_user
from app.models.base import User
import base64
import io
from fastapi.responses import StreamingResponse
from datetime import date
from app.plant.report import generate_plant_report_pdf

graphLogRouter = APIRouter(prefix="/api/v1/logs", tags=["graphLog"])




@graphLogRouter.post("/graph-data", response_model=GraphDataSeriesResponse)
def get_graph_data(
    request: GraphDataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get time series data for graphs"""
    try:
        series = crud.get_graph_data(db, request)
        print(series)
        return GraphDataSeriesResponse(series=series)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@graphLogRouter.post("/graph-data/flow", response_model=GraphDataSeriesResponse)
def get_flow_graph_data(
    request: GraphDataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get flow data (inlet/outlet values) for graphs"""
    try:
        request.log_type = "flow"  # Override log type to ensure flow data
        series = crud.get_graph_data(db, request)
        print(series)
        return GraphDataSeriesResponse(series=series)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@graphLogRouter.post("/graph-data/equipment", response_model=GraphDataSeriesResponse)
def get_equipment_graph_data(
    request: GraphDataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get equipment status data for graphs"""
    try:
        request.log_type = "equipment"  # Override log type to ensure equipment data
        series = crud.get_graph_data(db, request)
        print(series)
        return GraphDataSeriesResponse(series=series)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@graphLogRouter.post("/graph-data/chemical/used", response_model=GraphDataSeriesResponse)
def get_chemical_usage_graph_data(
    request: GraphDataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chemical quantity used data for graphs"""
    try:
        request.log_type = "chemical-used"  # Override log type to ensure chemical data
        series = crud.get_graph_data(db, request)
        # Filter only the "Used" series
        print(series)
        # filtered_series = [s for s in series if "(Used)" in s.series_name]
        return GraphDataSeriesResponse(series=series)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@graphLogRouter.post("/graph-data/chemical/remaining", response_model=GraphDataSeriesResponse)
def get_chemical_remaining_graph_data(
    request: GraphDataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chemical quantity remaining data for graphs"""
    try:
        request.log_type = "chemical-left"  # Override log type to ensure chemical data
        series = crud.get_graph_data(db, request)
        # Filter only the "Quantity Left" series
        print(series)
        # filtered_series = [s for s in series if "(Quantity Left)" in s.series_name]
        return GraphDataSeriesResponse(series=series)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@graphLogRouter.post("/graph-data/parameters", response_model=GraphDataSeriesResponse)
def get_flow_parameters_graph_data(
    request: GraphDataRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get flow parameters data for graphs"""
    try:
        request.log_type = "flowparameter"  # Override log type to ensure flow parameter data
        series = crud.get_graph_data(db, request)
        print(series)
        return GraphDataSeriesResponse(series=series)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))