from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.models.base import Plant, User, PlantType,PlantChemical, PlantEquipment, PlantFlowParameter,ClientPlant,OperatorPlant
from app.schemas.plant import PlantSchema
from fastapi import HTTPException



def get_client_operator_ids(db: Session, plant_id: int):
    client_ids = [cp.client_id for cp in db.query(ClientPlant).filter(ClientPlant.plant_id == plant_id).all()]
    operator_ids = [op.operator_id for op in db.query(OperatorPlant).filter(OperatorPlant.plant_id == plant_id).all()]
    return client_ids, operator_ids
# Create a new plant
def createPlant(db: Session, plant: PlantSchema):
    # Ensure client_id and operator_id are lists
    client_ids = plant.client_id if isinstance(plant.client_id, list) else [plant.client_id] if plant.client_id is not None else []
    operator_ids = plant.operator_id if isinstance(plant.operator_id, list) else [plant.operator_id] if plant.operator_id is not None else []

    # Check if all client users exist and have role 2
    for cid in client_ids:
        user = db.query(User).filter(User.user_id == cid, User.role_id == 2).first()
        if not user:
            raise HTTPException(status_code=400, detail=f"Client user with id {cid} and role 2 not found")

    # Check if all operator users exist and have role 3
    for oid in operator_ids:
        user = db.query(User).filter(User.user_id == oid, User.role_id == 3).first()
        if not user:
            raise HTTPException(status_code=400, detail=f"Operator user with id {oid} and role 3 not found")

    # Create the plant
    new_plant = Plant(
        plant_type_id=plant.plant_type_id,
        plant_name=plant.plant_name,
        address=plant.address,
        plant_capacity=plant.plant_capacity,
        hotel_name=plant.hotel_name if plant.hotel_name is not None else None,
        plant_description=plant.plant_description if plant.plant_description is not None else None,
        operational_status=plant.operational_status if plant.operational_status is not None else False
    )
    db.add(new_plant)
    db.commit()
    db.refresh(new_plant)

    # Create ClientPlant associations
    for cid in client_ids:
        client_plant = ClientPlant(client_id=cid, plant_id=new_plant.plant_id)
        db.add(client_plant)

    # Create OperatorPlant associations
    for oid in operator_ids:
        operator_plant = OperatorPlant(operator_id=oid, plant_id=new_plant.plant_id)
        db.add(operator_plant)

    db.commit()
    db.refresh(new_plant)
    client_ids, operator_ids = get_client_operator_ids(db, new_plant.plant_id)
    return PlantSchema(
                plant_id=new_plant.plant_id,
                plant_type_id=new_plant.plant_type_id,
                plant_name=new_plant.plant_name,
                address=new_plant.address,
                plant_capacity=new_plant.plant_capacity,
                hotel_name=new_plant.hotel_name,
                plant_description=new_plant.plant_description,
                operational_status=new_plant.operational_status,
                created_at=new_plant.created_at,
                updated_at=new_plant.updated_at,
                del_flag=new_plant.del_flag,
                client_id=client_ids,
                operator_id=operator_ids
            )



# Read a single plant by ID
def getPlantById(db: Session, plant_id: int):
    plant = db.query(Plant).filter(Plant.plant_id == plant_id, Plant.del_flag == False).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    if plant.plant_chemicals:
        plant.plant_chemicals = plant.plant_chemicals.split(",")
    if plant.plant_equipments:
        plant.plant_equiments = plant.plant_equiments.split(",")
    if plant.plant_flow_parameters:
        plant.plant_flow_parameters = plant.plant_flow_parameters.split(",")
    client_ids, operator_ids = get_client_operator_ids(db, plant.plant_id)

    return PlantSchema(
                plant_id=plant.plant_id,
                plant_type_id=plant.plant_type_id,
                plant_name=plant.plant_name,
                address=plant.address,
                plant_capacity=plant.plant_capacity,
                hotel_name=plant.hotel_name,
                plant_description=plant.plant_description,
                operational_status=plant.operational_status,
                created_at=plant.created_at,
                updated_at=plant.updated_at,
                del_flag=plant.del_flag,
                client_id=client_ids,
                operator_id=operator_ids
            )


def getPlantsByPlantTypeId(db: Session, plant_type_id: int, user: User):
    """This function retrieves plants based on the plant type ID and the user's role, supporting n-to-n client/operator relations."""
    plants = []
    if user.is_admin:
        print("Admin user fetching all plants")
        plants = db.query(Plant).filter(
            Plant.plant_type_id == plant_type_id,
            Plant.del_flag == False
        ).all()
    elif user.role_id == 2:  # Client
        print(f"Client user fetching owned plants plant type id : {plant_type_id} and user id : {user.user_id}")
        # Get all plant_ids for this client from ClientPlant
        client_plant_ids = db.query(ClientPlant.plant_id).filter(ClientPlant.client_id == user.user_id).subquery()
        plants = db.query(Plant).filter(
            Plant.plant_type_id == plant_type_id,
            Plant.del_flag == False,
            Plant.plant_id.in_(client_plant_ids)
        ).all()
        print(f"Plants fetched for client user : {len(plants)}")
    elif user.role_id == 3:  # Operator
        print("Operator user fetching operated plants")
        # Get all plant_ids for this operator from OperatorPlant
        operator_plant_ids = db.query(OperatorPlant.plant_id).filter(OperatorPlant.operator_id == user.user_id).subquery()
        plants = db.query(Plant).filter(
            Plant.plant_type_id == plant_type_id,
            Plant.del_flag == False,
            Plant.plant_id.in_(operator_plant_ids)
        ).all()

    if not plants:
        raise HTTPException(status_code=404, detail="Plants not found")
    for plant in plants:
        if plant.plant_chemicals:
            plant.plant_chemicals = plant.plant_chemicals.split(",")
        if plant.plant_equipments:
            plant.plant_equipments = plant.plant_equipments.split(",")
        if plant.plant_flow_parameters:
            plant.plant_flow_parameters = plant.plant_flow_parameters.split(",")
    result = []
    for plant in plants:
        client_ids, operator_ids = get_client_operator_ids(db, plant.plant_id)
        result.append(PlantSchema(
                plant_id=plant.plant_id,
                plant_type_id=plant.plant_type_id,
                plant_name=plant.plant_name,
                address=plant.address,
                plant_capacity=plant.plant_capacity,
                hotel_name=plant.hotel_name,
                plant_description=plant.plant_description,
                operational_status=plant.operational_status,
                created_at=plant.created_at,
                updated_at=plant.updated_at,
                del_flag=plant.del_flag,
                client_id=client_ids,
                operator_id=operator_ids
            ))
    return result


# Read all plants with optional filters
def getAllPlants(
    db: Session,
    plant: PlantSchema = None,
    current_user: User = None
):
    query = db.query(Plant).filter(Plant.del_flag == False)

    # Apply role-based filtering for n-to-n relations
    if current_user:
        if not current_user.is_admin:  # Non-admin users can only see their plants
            if current_user.role_id == 2:  # Client role
                client_plant_ids = db.query(ClientPlant.plant_id).filter(ClientPlant.client_id == current_user.user_id).subquery()
                query = query.filter(Plant.plant_id.in_(client_plant_ids))
            elif current_user.role_id == 3:  # Operator role
                operator_plant_ids = db.query(OperatorPlant.plant_id).filter(OperatorPlant.operator_id == current_user.user_id).subquery()
                query = query.filter(Plant.plant_id.in_(operator_plant_ids))

    # Apply additional filters if provided
    if plant:
        if plant.plant_name:
            query = query.filter(Plant.plant_name.ilike(f"%{plant.plant_name}%"))
        if plant.client_id:
            client_ids = plant.client_id if isinstance(plant.client_id, list) else [plant.client_id]
            client_plant_ids = db.query(ClientPlant.plant_id).filter(ClientPlant.client_id.in_(client_ids)).subquery()
            query = query.filter(Plant.plant_id.in_(client_plant_ids))
        if plant.plant_type_id:
            query = query.filter(Plant.plant_type_id == plant.plant_type_id)
        # Apply pagination only if plant parameter is provided
        plants = query.order_by(desc(Plant.created_at)).offset((plant.page-1)*plant.limit).limit(plant.limit).all()
        result = []
        for plant_obj in plants:
            client_ids, operator_ids = get_client_operator_ids(db, plant_obj.plant_id)
            result.append(PlantSchema(
                plant_id=plant_obj.plant_id,
                plant_type_id=plant_obj.plant_type_id,
                plant_name=plant_obj.plant_name,
                address=plant_obj.address,
                plant_capacity=plant_obj.plant_capacity,
                hotel_name=plant_obj.hotel_name,
                plant_description=plant_obj.plant_description,
                operational_status=plant_obj.operational_status,
                created_at=plant_obj.created_at,
                updated_at=plant_obj.updated_at,
                del_flag=plant_obj.del_flag,
                client_id=client_ids,
                operator_id=operator_ids
            ))
        return result

    # If no plant parameter, just return filtered results ordered by created_at
    plants = query.order_by(desc(Plant.created_at)).all()
    result = []
    for plant_obj in plants:
        client_ids, operator_ids = get_client_operator_ids(db, plant_obj.plant_id)
        result.append(PlantSchema(
                plant_id=plant_obj.plant_id,
                plant_type_id=plant_obj.plant_type_id,
                plant_name=plant_obj.plant_name,
                address=plant_obj.address,
                plant_capacity=plant_obj.plant_capacity,
                hotel_name=plant_obj.hotel_name,
                plant_description=plant_obj.plant_description,
                operational_status=plant_obj.operational_status,
                created_at=plant_obj.created_at,
                updated_at=plant_obj.updated_at,
                del_flag=plant_obj.del_flag,
                client_id=client_ids,
                operator_id=operator_ids
            ))
    return result
# Update a plant
def updatePlant(db: Session, plant_id: int, plant: PlantSchema):
    existing_plant = db.query(Plant).filter(Plant.plant_id == plant_id, Plant.del_flag == False).first()
    if not existing_plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    update_data = plant.model_dump(exclude_unset=True)

    # Remove client_id and operator_id from update_data to handle them separately
    client_ids = update_data.pop("client_id", None)
    operator_ids = update_data.pop("operator_id", None)
    update_data.pop("plant_id", None)
    update_data.pop("created_at", None)
    update_data.pop("updated_at", None)
    update_data.pop("del_flag", None)
    update_data.pop("limit", None)
    update_data.pop("page", None)
    # Update plant fields
    for key, value in update_data.items():
        setattr(existing_plant, key, value)

    # Update ClientPlant associations if client_ids provided
    if client_ids is not None:
        # Ensure it's a list
        client_ids = client_ids if isinstance(client_ids, list) else [client_ids]
        # Delete old associations
        db.query(ClientPlant).filter(ClientPlant.plant_id == plant_id).delete()
        # Add new associations
        for cid in client_ids:
            db.add(ClientPlant(client_id=cid, plant_id=plant_id))

    # Update OperatorPlant associations if operator_ids provided
    if operator_ids is not None:
        # Ensure it's a list
        operator_ids = operator_ids if isinstance(operator_ids, list) else [operator_ids]
        # Delete old associations
        db.query(OperatorPlant).filter(OperatorPlant.plant_id == plant_id).delete()
        # Add new associations
        for oid in operator_ids:
            db.add(OperatorPlant(operator_id=oid, plant_id=plant_id))

    db.commit()
    db.refresh(existing_plant)
    client_ids, operator_ids = get_client_operator_ids(db, plant_id)
    return_value = PlantSchema(
                plant_id=existing_plant.plant_id,
                plant_type_id=existing_plant.plant_type_id,
                plant_name=existing_plant.plant_name,
                address=existing_plant.address,
                plant_capacity=existing_plant.plant_capacity,
                hotel_name=existing_plant.hotel_name,
                plant_description=existing_plant.plant_description,
                operational_status=existing_plant.operational_status,
                created_at=existing_plant.created_at,
                updated_at=existing_plant.updated_at,
                del_flag=existing_plant.del_flag,
                client_id=client_ids,
                operator_id=operator_ids
            )
    print(return_value)
    return return_value

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