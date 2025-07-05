from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from typing import List, Dict, Union, Optional


class FlowParameterLogSchema(BaseModel):
    flow_parameter_log_id: Optional[int]= None
    daily_log_id: Optional[int]= None
    plant_flow_parameter_id: Optional[int]= None
    value: Optional[float]= None
    outlet_value: Optional[float]= None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    shift : Optional[int]=0 #0 for morning, 1 for evening, 2 for night
    plant_id : Optional[int] = None


    class Config:
        from_attributes = True
