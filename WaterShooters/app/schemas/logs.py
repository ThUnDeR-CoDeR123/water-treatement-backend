from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from typing import List, Dict, Union, Optional

class DailyLogSchema(BaseModel):
    log_id: Optional[int]
    plant_id: Optional[int]
    created_by: Optional[int]
    shift: Optional[int]
    created_at: Optional[datetime]
    del_flag: Optional[bool]

    class Config:
        from_attributes = True

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
    class Config:
        from_attributes = True

class getLogSchema(BaseModel):
    plant_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

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

    class Config:
        from_attributes = True

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

class GraphDataRequest(BaseModel):
    start_date: date
    end_date: date
    plant_id: int
    log_type: str  # 'flow', 'chemical', 'flowparameter', 'equipment'

class GraphDataPoint(BaseModel):
    timestamp: date
    value: Union[float, int, str]
    parameter_name: Optional[str] = None

class GraphDataResponse(BaseModel):
    series_name: str
    data: List[GraphDataPoint]

class GraphDataSeriesResponse(BaseModel):
    series: List[GraphDataResponse]

