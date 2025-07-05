# schemas/role.py
from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime

class PlantFlowParameterSchema(BaseModel):
    plant_flow_parameter_id: Optional[int] = None
    plant_id: Optional[int] = None
    parameter_name: Optional[str] = None
    parameter_unit: Optional[str] = None
    target_value: Optional[float] = None
    tolerance: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    del_flag: Optional[bool] = None
    limit: Optional[int] = 100
    page: Optional[int] = 1

    class Config:
        from_attributes = True