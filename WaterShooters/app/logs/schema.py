from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from typing import List, Dict, Union, Optional


class getLogSchema(BaseModel):
    plant_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None