
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from typing import List, Dict, Union, Optional


class ChemicalLogSchema(BaseModel):
    plant_id : Optional[int] = None
    chemical_log_id: Optional[int] = None
    daily_log_id: Optional[int] = None 
    plant_chemical_id: Optional[int]= None
    quantity_used: Optional[float]= None
    incomming_quantity: Optional[float]= None
    quantity_left: Optional[float]= None
    sludge_discharge: Optional[bool]  = False
    shift : Optional[int]=0 #0 for morning, 1 for evening, 2 for night
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True