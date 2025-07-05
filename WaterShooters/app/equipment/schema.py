# schemas/role.py
from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime

class PlantEquipmentSchema(BaseModel):
    plant_equipment_id: Optional[int] = None
    plant_id: Optional[int] = None
    equipment_name: Optional[str] = None
    equipment_type: Optional[str] = None
    last_maintenance: Optional[datetime] = None
    status: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    del_flag: Optional[bool] = None
    limit: Optional[int] = 100
    page: Optional[int] = 1

    class Config:
        from_attributes = True