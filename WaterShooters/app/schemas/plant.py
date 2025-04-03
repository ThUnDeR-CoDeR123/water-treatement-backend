# schemas/role.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PlantSchema(BaseModel):
    plant_id: Optional[int] = None
    client_id: Optional[int] = None
    operator_id: Optional[int] = None
    plant_type_id: Optional[int] = None
    plant_name: Optional[str] = None
    address: Optional[str] = None
    plant_capacity: Optional[float] = None
    hotel_name: Optional[str] = None
    plant_description: Optional[str] = None
    operational_status: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    del_flag: Optional[bool] = None
    limit: Optional[int] = 10
    page: Optional[int] = 1

    class Config:
        orm_mode = True

class PlantTypeSchema(BaseModel):
    plant_type_id: Optional[int] = None
    plant_type_name: Optional[str] = None
    plant_type_description: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    del_flag: Optional[bool] = None

    class Config:
        orm_mode = True

class PlantFlowParameterSchema(BaseModel):
    plant_flow_parameter_id: Optional[int] = None
    plant_id: Optional[int] = None
    flow_parameter_id: Optional[int] = None
    target_value: Optional[float] = None
    tolerance: Optional[float] = None

    class Config:
        orm_mode = True

class PlantChemicalSchema(BaseModel):
    plant_chemical_id: Optional[int] = None
    plant_id: Optional[int] = None
    chemical_id: Optional[int] = None
    quantity: Optional[float] = None
    created_at: Optional[datetime] = None
    del_flag: Optional[bool] = None

    class Config:
        orm_mode = True


class PlantEquipmentSchema(BaseModel):
    plant_equipment_id: Optional[int] = None
    plant_id: Optional[int] = None
    equipment_id: Optional[int] = None
    last_maintenance: Optional[datetime] = None
    status: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    del_flag: Optional[bool] = None

    class Config:
        orm_mode = True

class FlowParameterSchema(BaseModel):
    flow_parameter_id: Optional[int] = None
    created_by: Optional[int] = None
    parameter_name: Optional[str] = None
    parameter_unit: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    del_flag: Optional[bool] = None

    class Config:
        orm_mode = True

class EquipmentSchema(BaseModel):
    equipment_id: Optional[int] = None
    plant_id: Optional[int] = None
    created_by: Optional[int] = None
    equipment_name: Optional[str] = None
    equipment_type: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    del_flag: Optional[bool] = None

    class Config:
        orm_mode = True

class ChemicalSchema(BaseModel):
    chemical_id: Optional[int] = None
    created_by: Optional[int] = None
    chemical_name: Optional[str] = None
    chemical_unit: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    del_flag: Optional[bool] = None

    class Config:
        orm_mode = True