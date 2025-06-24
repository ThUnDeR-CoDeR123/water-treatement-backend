from datetime import datetime
import json
from sqlalchemy.orm import DeclarativeBase
from typing import List, Optional
from sqlalchemy import (
    String, Integer, Boolean, DateTime, ForeignKey, func, Text,Float
)
from sqlalchemy.orm import ( Mapped, mapped_column, relationship)
# -----------------------------------------------
# Base with to_dict and to_json
# -----------------------------------------------
class Base(DeclarativeBase):
    def to_dict(self, seen=None):
        if seen is None:
            seen = set()
        if id(self) in seen:
            return {}
        seen.add(id(self))

        data = {}
        for column in self.__table__.columns:
            val = getattr(self, column.name)
            if isinstance(val, datetime):
                data[column.name] = val.isoformat()
            else:
                data[column.name] = val

        for rel_name in self.__mapper__.relationships.keys():
            related_obj = getattr(self, rel_name)
            if related_obj is not None:
                if isinstance(related_obj, list):
                    data[rel_name] = [item.to_dict(seen=seen) for item in related_obj]
                else:
                    data[rel_name] = related_obj.to_dict(seen=seen)

        return data

    def to_json(self):
        return json.dumps(self.to_dict(), default=str)














# -----------------------------------------------
# Role Table
# -----------------------------------------------
class Role(Base):
    __tablename__ = "role"

    role_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[str] = mapped_column(String(30), nullable=False)
    del_flag: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    users: Mapped[List["User"]] = relationship("User", back_populates="role", cascade="all, delete-orphan")

# -----------------------------------------------
# User Table
# -----------------------------------------------
class User(Base):
    __tablename__ = "user"

    # Primary key
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Required fields
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    aadhar_no: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    phone_no: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)

    # Optional fields
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    qualification: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    DOB: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    otp: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Required fields with defaults
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    del_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    # Foreign key
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("role.role_id"), nullable=False)
    role: Mapped["Role"] = relationship("Role", back_populates="users")

    # Relationships 
    owned_plants: Mapped[List["Plant"]] = relationship(
        "Plant",
        foreign_keys="Plant.client_id",
        back_populates="client"
    )
    operated_plants: Mapped[List["Plant"]] = relationship(
        "Plant",
        foreign_keys="Plant.operator_id",
        back_populates="operator"
    )
    daily_logs: Mapped[List["DailyLog"]] = relationship("DailyLog", back_populates="operator", foreign_keys="DailyLog.created_by")
    complaints: Mapped[List["ComplaintSuggestion"]] = relationship("ComplaintSuggestion", back_populates="user", foreign_keys="ComplaintSuggestion.user_id")



class ClientPlant(Base):
    __tablename__ = "clientplant"
    client_plant_id: Mapped[int] = mapped_column(Integer,primary_key=True)
    client_id: Mapped[int] = mapped_column(Integer,ForeignKey("user.user_id"),nullable=False)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plant.plant_id"), nullable=False)


class OperatorPlant(Base):
    __tablename__ = "operatorplant"
    operator_plant_id: Mapped[int] = mapped_column(Integer,primary_key=True)
    operator_id: Mapped[int] = mapped_column(Integer,ForeignKey("user.user_id"),nullable=False)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plant.plant_id"), nullable=False)


# -----------------------------------------------
# COMPLAINT / SUGGESTION
# -----------------------------------------------
class ComplaintSuggestion(Base):
    __tablename__ = "complaintsuggestion"

    cs_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer,ForeignKey("user.user_id"),nullable=False)
    plant_id: Mapped[int] = mapped_column(Integer,ForeignKey("plant.plant_id"),nullable=False)

    message: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[int] = mapped_column(Integer, nullable=False)  # e.g., 0=Complaint, 1=Suggestion
    is_addressed: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column( DateTime, default=func.now(), onupdate=func.now())
    del_flag: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="complaints")
    plant: Mapped["Plant"] = relationship("Plant", back_populates="complaints")

    def __repr__(self) -> str:
        return f"<ComplaintSuggestion(cs_id={self.cs_id}, user_id={self.user_id}, plant_id={self.plant_id})>"

















#plant type table
class PlantType(Base):
    __tablename__ = "planttype"

    plant_type_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plant_type_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    plant_type_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.user_id"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
    del_flag: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    
# PLANT

class Plant(Base):
    __tablename__ = "plant"

    #primary key
    plant_id: Mapped[int] = mapped_column(Integer, primary_key=True)



    #Foreign keys
    # A single user can be the "client" (owner)
    client_id: Mapped[int] = mapped_column(Integer,ForeignKey("user.user_id"),nullable=False)
    # A single user can be the "operator"
    operator_id: Mapped[int] = mapped_column(Integer,ForeignKey("user.user_id"),nullable=False)

    plant_type_id: Mapped[int] = mapped_column(Integer,ForeignKey("planttype.plant_type_id"),nullable=False)


    #atributes that are needed for object creation
    plant_name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    plant_capacity: Mapped[float] = mapped_column(Float, nullable=False)


    #optional attributes
    hotel_name: Mapped[str] = mapped_column(String, nullable=True)
    plant_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    #operational attributes
    operational_status: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    del_flag: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # Relationships
    # - to complaints
    complaints: Mapped[List["ComplaintSuggestion"]] = relationship("ComplaintSuggestion",back_populates="plant",cascade="all, delete-orphan")

    # - to daily logs
    daily_logs: Mapped[List["DailyLog"]] = relationship("DailyLog",back_populates="plant",cascade="all, delete-orphan",foreign_keys="DailyLog.plant_id")

    #relationships
    plant_chemicals: Mapped[List["PlantChemical"]] = relationship("PlantChemical", back_populates="plant", cascade="all, delete-orphan")
    plant_equipments: Mapped[List["PlantEquipment"]] = relationship("PlantEquipment", back_populates="plant", cascade="all, delete-orphan")
    plant_flow_parameters: Mapped[List["PlantFlowParameter"]] = relationship("PlantFlowParameter", back_populates="plant", cascade="all, delete-orphan")
    client: Mapped[Optional["User"]] = relationship("User", foreign_keys=[client_id], back_populates="owned_plants", uselist=False)
    operator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[operator_id], back_populates="operated_plants", uselist=False)

    def __repr__(self) -> str:
        return (
            f"<Plant(plant_id={self.plant_id}, name={self.plant_name}, "
            f"type={self.plant_type}, capacity={self.plant_capacity})>"
        )


# Table: PlantChemical
class PlantChemical(Base):
    __tablename__ = "plantchemical"

    plant_chemical_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plant.plant_id"), nullable=False)
    
    # Moved from Chemical class
    chemical_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    chemical_unit: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    quantity: Mapped[Optional[float]] = mapped_column(Float, nullable=True) 
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    del_flag: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # Relationships
    plant: Mapped["Plant"] = relationship("Plant", back_populates="plant_chemicals")
    plant_chemical_logs: Mapped[List["ChemicalLog"]] = relationship("ChemicalLog", back_populates="plant_chemical", cascade="all, delete-orphan")

# Table: PlantEquipment
class PlantEquipment(Base):
    __tablename__ = "plantequipment"

    plant_equipment_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plant.plant_id"), nullable=False)
    
    # Moved from Equipment class
    equipment_name: Mapped[str] = mapped_column(String, nullable=False)
    equipment_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    last_maintenance: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")  # 0 for okay, 1 for critical, 2 for down
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    del_flag: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    
    # Relationships
    plant: Mapped["Plant"] = relationship("Plant", back_populates="plant_equipments")
    plant_equipment_logs: Mapped[List["EquipmentLog"]] = relationship("EquipmentLog", back_populates="plant_equipment", cascade="all, delete-orphan")

# Table: PlantFlowParameter
class PlantFlowParameter(Base):
    __tablename__ = "plantflowparameter"

    plant_flow_parameter_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plant.plant_id"), nullable=False)
    
    # Moved from FlowParameter class
    parameter_name: Mapped[str] = mapped_column(String, nullable=False)
    parameter_unit: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    target_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tolerance: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    del_flag: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # Relationships
    plant: Mapped["Plant"] = relationship("Plant", back_populates="plant_flow_parameters")
    flow_parameter_logs: Mapped[List["FlowParameterLog"]] = relationship("FlowParameterLog", back_populates="plant_flow_parameter", cascade="all, delete-orphan")














class DailyLog(Base):
    __tablename__ = "dailylog"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plant_id: Mapped[int] = mapped_column(Integer,ForeignKey("plant.plant_id"),nullable=False)
    created_by: Mapped[int] = mapped_column(Integer,ForeignKey("user.user_id"),nullable=False)
    shift: Mapped[int] = mapped_column(Integer, nullable=False)#0 for morning, 1 for evening, 2 for night
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    del_flag: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # Relationships
    plant: Mapped["Plant"] = relationship("Plant",back_populates="daily_logs")
    operator: Mapped["User"] = relationship("User",back_populates="daily_logs")

    # Each DailyLog can have multiple flow parameters, equipment checks, chemicals
    flow_parameter_logs: Mapped[List["FlowParameterLog"]] = relationship("FlowParameterLog",back_populates="daily_log",cascade="all, delete-orphan")
    equipment_logs: Mapped[List["EquipmentLog"]] = relationship("EquipmentLog",back_populates="daily_log",cascade="all, delete-orphan")
    plant_chemical_logs: Mapped[List["ChemicalLog"]] = relationship("ChemicalLog",back_populates="daily_log",cascade="all, delete-orphan")
    flow_logs: Mapped[List["FlowLog"]] = relationship("FlowLog", back_populates="daily_log", cascade="all, delete-orphan")


    def __repr__(self) -> str:
        return (
            f"<DailyLog(log_id={self.log_id}, plant_id={self.plant_id}, shift={self.shift})>"
        )

class FlowLog(Base):
    __tablename__ = "flow_log"

    flow_log_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    daily_log_id: Mapped[int] = mapped_column(Integer, ForeignKey("dailylog.log_id"), nullable=False)
    plant_id: Mapped[int] = mapped_column(Integer, ForeignKey("plant.plant_id"), nullable=False)
    inlet_value: Mapped[float] = mapped_column(Float, nullable=False)
    outlet_value: Mapped[float] = mapped_column(Float, nullable=False)
    inlet_image: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    outlet_image: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("user.user_id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    del_flag: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    shift: Mapped[int] = mapped_column(Integer, nullable=False)  # 0 for morning, 1 for evening, 2 for night
    # Relationships
    daily_log: Mapped["DailyLog"] = relationship("DailyLog", back_populates="flow_logs")
    plant: Mapped["Plant"] = relationship("Plant")

# FLOW PARAMETER LOG
class FlowParameterLog(Base):
    __tablename__ = "flowparameterlog"

    plant_id: Mapped[int] = mapped_column(Integer,ForeignKey("plant.plant_id"),nullable=False)
    flow_parameter_log_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    daily_log_id: Mapped[int] = mapped_column(Integer,ForeignKey("dailylog.log_id"),nullable=False)
    plant_flow_parameter_id: Mapped[int] = mapped_column(Integer,ForeignKey("plantflowparameter.plant_flow_parameter_id"),nullable=False)
    created_by: Mapped[int] = mapped_column(Integer,ForeignKey("user.user_id"),nullable=False)
    
    shift: Mapped[int] = mapped_column(Integer, nullable=False)#0 for morning, 1 for evening, 2 for night
    inlet_value: Mapped[float] = mapped_column(Float, nullable=False)
    outlet_value: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    del_flag: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # Relationships
    daily_log: Mapped["DailyLog"] = relationship("DailyLog",back_populates="flow_parameter_logs")
    plant_flow_parameter: Mapped["PlantFlowParameter"] = relationship("PlantFlowParameter",back_populates="flow_parameter_logs")

    def __repr__(self) -> str:
        return (
            f"<FlowParameterLog(flow_parameter_log_id={self.flow_parameter_log_id}, "
            f"value={self.value})>"
        )


# CHEMICAL LOG
class ChemicalLog(Base):
    __tablename__ = "chemicallog"

    plant_id: Mapped[int] = mapped_column(Integer,ForeignKey("plant.plant_id"),nullable=False)
    chemical_log_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    daily_log_id: Mapped[int] = mapped_column(Integer,ForeignKey("dailylog.log_id"),nullable=False)
    plant_chemical_id: Mapped[int] = mapped_column(Integer,ForeignKey("plantchemical.plant_chemical_id"),nullable=False)
    created_by: Mapped[int] = mapped_column(Integer,ForeignKey("user.user_id"),nullable=False)

    shift: Mapped[int] = mapped_column(Integer, nullable=False)#0 for morning, 1 for evening, 2 for night
    quantity_left: Mapped[float] = mapped_column(Float, nullable=False)
    quantity_used: Mapped[float] = mapped_column(Float, nullable=False)
    sludge_discharge: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    del_flag: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # Relationships
    daily_log: Mapped["DailyLog"] = relationship("DailyLog",back_populates="plant_chemical_logs")
    plant_chemical: Mapped["PlantChemical"] = relationship("PlantChemical",back_populates="plant_chemical_logs")

    def __repr__(self) -> str:
        return (
            f"<ChemicalLog(chemical_log_id={self.chemical_log_id}, "
            f"qty_left={self.quantity_left}, qty_consumed={self.quantity_consumed})>"
        )


# EQUIPMENT LOG
class EquipmentLog(Base):
    __tablename__ = "equipmentlog"

    equipment_log_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    daily_log_id: Mapped[int] = mapped_column(Integer,ForeignKey("dailylog.log_id"),nullable=False)
    plant_equipment_id: Mapped[int] = mapped_column(Integer,ForeignKey("plantequipment.plant_equipment_id"),nullable=False)
    plant_id: Mapped[int] = mapped_column(Integer,ForeignKey("plant.plant_id"),nullable=False)
    created_by: Mapped[int] = mapped_column(Integer,ForeignKey("user.user_id"),nullable=False)

    shift: Mapped[int] = mapped_column(Integer, nullable=False)#0 for morning, 1 for evening, 2 for night
    equipment_status: Mapped[int] = mapped_column(Integer, default=0)# 0 for okay, 1 for critical, 2 for down
    equipment_remark: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    maintenance_done: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    del_flag: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    # Relationships
    daily_log: Mapped["DailyLog"] = relationship("DailyLog",back_populates="equipment_logs")
    plant_equipment: Mapped["PlantEquipment"] = relationship("PlantEquipment",back_populates="plant_equipment_logs")

    def __repr__(self) -> str:
        return (
            f"<EquipmentLog(equipment_log_id={self.equipment_log_id}, "
            f"status={self.equipment_status}, remark={self.equipment_remark})>"
        )


