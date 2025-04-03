from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DailyLogSchema(BaseModel):
    log_id: Optional[int]
    plant_id: Optional[int]
    created_by: Optional[int]
    shift: Optional[int]
    created_at: Optional[datetime]
    del_flag: Optional[bool]

    class Config:
        orm_mode = True

class FlowParameterLogSchema(BaseModel):
    flow_parameter_log_id: Optional[int]= None
    daily_log_id: Optional[int]= None
    plant_flow_parameter_id: Optional[int]
    inlet_value: Optional[float]
    outlet_value: Optional[float]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    shift : Optional[int]=0 #0 for morning, 1 for evening, 2 for night
    plant_id : Optional[int] = None


    class Config:
        orm_mode = True



class EquipmentLogSchema(BaseModel):
    plant_id : Optional[int] = None
    equipment_log_id: Optional[int] =None
    daily_log_id: Optional[int] = None
    plant_equipment_id: Optional[int]
    equipment_status: Optional[int]
    maintenance_done: Optional[bool] = False
    equipment_remark : Optional[str] = None
    shift : Optional[int]=0 #0 for morning, 1 for evening, 2 for night
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    class Config:
        orm_mode = True

class ChemicalLogSchema(BaseModel):
    plant_id : Optional[int] = None
    chemical_log_id: Optional[int] = None
    daily_log_id: Optional[int] = None 
    plant_chemical_id: Optional[int]
    quantity_used: Optional[float]
    quantity_left: Optional[float]
    sludge_discharge: Optional[bool]  = False
    shift : Optional[int]=0 #0 for morning, 1 for evening, 2 for night
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    class Config:
        orm_mode = True

