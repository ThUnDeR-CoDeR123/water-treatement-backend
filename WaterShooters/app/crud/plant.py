from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.models.base import Plant, User, PlantType, PlantTypeToChemical, PlantTypeToEquipment, PlantTypeToFlowParameter, PlantChemical, PlantEquipment, PlantFlowParameter
from app.schemas.plant import PlantSchema
from fastapi import HTTPException

# Create a new plant
def createPlant(db: Session, plant: PlantSchema) -> Plant:
    # Create plant with explicit field definition
    # Required fields - no null checks needed
    new_plant = Plant(
        client_id=plant.client_id,
        operator_id=plant.operator_id,
        plant_type_id=plant.plant_type_id,
        plant_name=plant.plant_name,
        address=plant.address,
        plant_capacity=plant.plant_capacity,
        # Optional fields - apply null checks
        hotel_name=plant.hotel_name if plant.hotel_name is not None else None,
        plant_description=plant.plant_description if plant.plant_description is not None else None,
        operational_status=plant.operational_status if plant.operational_status is not None else False
    )
    db.add(new_plant)
    db.commit()
    db.refresh(new_plant)
    
    #fetching plant type chemicals, equipments and flow parameters
    chemicals = db.query(PlantTypeToChemical).filter(PlantTypeToChemical.plant_type_id == new_plant.plant_type_id).all()
    equipments = db.query(PlantTypeToEquipment).filter(PlantTypeToEquipment.plant_type_id == new_plant.plant_type_id).all()
    flow_parameters = db.query(PlantTypeToFlowParameter).filter(PlantTypeToFlowParameter.plant_type_id == new_plant.plant_type_id).all()
    
    #inserting values to plantchemicals, plantequipments and plantflowparameters
    for chemical in chemicals:
        plant_chemical = PlantChemical(plant_id=new_plant.plant_id, chemical_id=chemical.chemical_id, quantity=0)
        db.add(plant_chemical)
    for equipment in equipments:
        plant_equipment = PlantEquipment(plant_id=new_plant.plant_id, equipment_id=equipment.equipment_id)
        db.add(plant_equipment)
    for flow_parameter in flow_parameters:
        plant_flow_parameter = PlantFlowParameter(plant_id=new_plant.plant_id, flow_parameter_id=flow_parameter.flow_parameter_id, target_value=0, tolerance=0)
        db.add(plant_flow_parameter)
    
    db.commit()
    db.refresh(new_plant)
    return new_plant

# Read a single plant by ID
def getPlantById(db: Session, plant_id: int) -> Optional[Plant]:
    plant = db.query(Plant).filter(Plant.plant_id == plant_id, Plant.del_flag == False).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    if plant.plant_chemicals:
        plant.plant_chemicals = plant.plant_chemicals.split(",")
    if plant.plant_equipments:
        plant.plant_equiments = plant.plant_equiments.split(",")
    if plant.plant_flow_parameters:
        plant.plant_flow_parameters = plant.plant_flow_parameters.split(",")
    return plant
def getPlantsByPlantTypeId(db: Session, plant_type_id: int, user: User) -> Optional[Plant]:
    """This function retrieves plants based on the plant type ID and the user's role."""
    if user.is_admin:
        plants = db.query(Plant).filter(Plant.plant_type_id == plant_type_id, Plant.del_flag == False).all()
    if user.role_id==2 and user.owned_plants:
        plants = db.query(Plant).filter(
                    Plant.plant_type_id == plant_type_id,
                    Plant.del_flag == False,
                    Plant.client_id == user.user_id,
                ).all()
    if user.role_id==3 and user.operated_plants:
        plants = db.query(Plant).filter(
                    Plant.plant_type_id == plant_type_id,
                    Plant.del_flag == False,
                    Plant.operator_id == user.user_id,
                ).all()
        
    if not plants:
        raise HTTPException(status_code=404, detail="Plants not found")
    for plant in plants:
        if plant.plant_chemicals:
            plant.plant_chemicals = plant.plant_chemicals.split(",")
        if plant.plant_equipments:
            plant.plant_equiments = plant.plant_equiments.split(",")
        if plant.plant_flow_parameters:
            plant.plant_flow_parameters = plant.plant_flow_parameters.split(",")
    return plants

# Read all plants with optional filters
def getAllPlants(
    db: Session,
    plant:PlantSchema = None,
    current_user: User = None
) -> List[Plant]:
    query = db.query(Plant).filter(Plant.del_flag == False)
    # Apply filters
    if plant:
        if plant.plant_name:
            query = query.filter(Plant.plant_name.ilike(f"%{plant.name}%"))
        if plant.client_id:
            query = query.filter(Plant.client_id == plant.client_id)
        if plant.operator_id:
            query = query.filter(Plant.operator_id == plant.operator_id)
        if plant.plant_type_id:
            query = query.filter(Plant.plant_type_id == plant.plant_type_id)
        # Apply pagination only if plant parameter is provided
        return query.order_by(desc(Plant.created_at)).offset((plant.page-1)*plant.limit).limit(plant.limit).all()
    
    # If no plant parameter, just return all ordered by created_at
    return query.order_by(desc(Plant.created_at)).all()

# Update a plant
def updatePlant(db: Session, plant_id: int, plant: PlantSchema) -> Optional[Plant]:
    existing_plant = db.query(Plant).filter(Plant.plant_id == plant_id, Plant.del_flag == False).first()
    if not existing_plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    for key, value in plant.model_dump(exclude_unset=True).items():
        setattr(existing_plant, key, value)

    db.commit()
    db.refresh(existing_plant)
    return existing_plant

# Soft delete a plant
def deletePlant(db: Session, plant_id: int) -> bool:
    existing_plant = db.query(Plant).filter(Plant.plant_id == plant_id, Plant.del_flag == False).first()
    if not existing_plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    existing_plant.del_flag = True
    db.commit()
    return True

# Get all plant types
def getAllPlantTypes(db: Session) -> List["PlantType"]:
    """Get all non-deleted plant types"""
    return db.query(PlantType).filter(PlantType.del_flag == False).all()