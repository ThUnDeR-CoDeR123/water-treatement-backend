from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from typing import  Optional

class EquipmentLogSchema(BaseModel):
    plant_id : Optional[int] = None
    equipment_log_id: Optional[int] =None
    daily_log_id: Optional[int] = None
    plant_equipment_id: Optional[int]= None
    equipment_status: Optional[int]= None
    maintenance_done: Optional[bool] = False
    equipment_remark : Optional[str] = None
    shift : Optional[int]=0 #0 for morning, 1 for evening, 2 for night
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True