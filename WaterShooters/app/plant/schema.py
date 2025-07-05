# schemas/role.py
from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime

class PlantSchema(BaseModel):
    plant_id: Optional[int] = None
    client_id: Optional[List[int]] = None
    operator_id: Optional[List[int]] = None
    plant_type_id: Optional[int] = None
    plant_name: Optional[str] = None
    address: Optional[str] = None
    plant_capacity: Optional[float] = None
    hotel_name: Optional[str] = None
    plant_description: Optional[str] = None
    operational_status: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    del_flag: Optional[bool] = None
    limit: Optional[int] = 100
    page: Optional[int] = 1

    class Config:
        from_attributes = True

class PlantTypeSchema(BaseModel):
    plant_type_id: Optional[int] = None
    plant_type_name: Optional[str] = None
    plant_type_description: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    del_flag: Optional[bool] = None

    class Config:
        from_attributes = True