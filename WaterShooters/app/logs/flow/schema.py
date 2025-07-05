from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import  Optional

class FlowLogSchema(BaseModel):
    flow_log_id: Optional[int] = None
    daily_log_id: Optional[int] = None
    plant_id: Optional[int] = None
    inlet_value: Optional[float] = None
    outlet_value: Optional[float] = None
    inlet_image: Optional[str] = None
    outlet_image: Optional[str] = None
    created_by: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    shift: Optional[int] = None  #0 for morning, 1 for evening, 2 for night
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    del_flag: Optional[bool] = None

    class Config:
        from_attributes = True