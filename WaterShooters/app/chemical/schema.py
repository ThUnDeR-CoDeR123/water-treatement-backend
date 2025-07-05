from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime


class PlantChemicalBase(BaseModel):
    plant_id: Optional[int] = None
    chemical_name: Optional[str] = None
    chemical_unit: Optional[str] = None
    quantity: Optional[float] = None

    class Config:
        from_attributes = True

class PlantChemicalCreate(PlantChemicalBase):
    plant_id: Optional[int] = None
    chemical_name: Optional[str] = None

class PlantChemicalUpdate(PlantChemicalBase):
    pass

class PlantChemicalInDB(PlantChemicalBase):
    plant_chemical_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    del_flag: Optional[bool] = False

class PlantChemicalSchema(PlantChemicalInDB):
    limit: Optional[int] = 100
    page: Optional[int] = 1

    class Config:
        from_attributes = True