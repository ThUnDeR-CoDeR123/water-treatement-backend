from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from typing import List, Dict, Union, Optional



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