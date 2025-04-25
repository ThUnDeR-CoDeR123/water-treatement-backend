from sqlalchemy.orm import Session
from sqlalchemy import desc,func,MetaData,text
from typing import List, Optional
from app.models.base import User
from app.schemas.user import UserSchema
from fastapi import Depends, HTTPException
from app.database import get_db

# Create a new user
def createUser(db: Session, user: UserSchema) -> User:
    new_user = User(**user.model_dump(exclude_unset=True))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Read a single user by ID
def getUserById( user_id: int,db: Session) -> Optional[User]:
    return db.query(User).filter(User.user_id == user_id, User.del_flag == False).first()
def getUserByEmail( email: str,db: Session) -> Optional[User]:
    return db.query(User).filter(User.email == email, User.del_flag == False).first()

# Read all users with filters and ordering
def getAllUsers(db: Session,filter: UserSchema = None,) -> List[User]:
    query = db.query(User).filter(User.del_flag == False)

    # Apply filters for all attributes
    if filter:
        if filter.user_id is not None:
            query = query.filter(User.user_id == filter.user_id)
        if filter.email:
            query = query.filter(User.email == filter.email)
        if filter.first_name:
            query = query.filter(User.first_name == filter.first_name)
        if filter.last_name:
            query = query.filter(User.last_name == filter.last_name)
        if filter.phone_no:
            query = query.filter(User.phone_no == filter.phone_no)
        if filter.address:
            query = query.filter(User.address == filter.address)
        if filter.qualification:
            query = query.filter(User.qualification == filter.qualification)
        if filter.DOB:
            query = query.filter(User.DOB == filter.DOB)
        if filter.is_verified is not None:
            query = query.filter(User.is_verified == filter.is_verified)
        if filter.last_login:
            query = query.filter(User.last_login == filter.last_login)
        if filter.is_admin is not None:
            query = query.filter(User.is_admin == filter.is_admin)

    # Order by created_at descending and apply pagination
    return query.order_by(desc(User.created_at)).offset(filter.page).limit(filter.limit).all()

# Update a user
def updateUser(db: Session, user_id: int, user: UserSchema) -> Optional[User]:
    existing_user = db.query(User).filter(User.user_id == user_id, User.del_flag == False).first()
    if not existing_user:
        return None

    for key, value in user.model_dump(exclude_unset=True).items():
        setattr(existing_user, key, value)

    db.commit()
    db.refresh(existing_user)
    return existing_user

# Soft delete a user
def deleteUser(db: Session, user_id: int) -> bool:
    existing_user = db.query(User).filter(User.user_id == user_id, User.del_flag == False).first()
    if not existing_user:
        return False

    existing_user.del_flag = True
    db.commit()
    return True



def updateLastLogin(user: User,db: Session):
    if not user:
        raise HTTPException(status_code=404, detail="User does not exists")
    user.last_login = func.now()
    db.commit()
    db.refresh(user)
    return user

def deleteAllTable(db: Session = Depends(get_db)):
    try:
        # Reflect the database schema to get all tables
        meta = MetaData()
        meta.reflect(bind=db.get_bind())  # Reflect the tables from the database

        # Drop all tables with cascade to handle dependencies
        for table in reversed(meta.sorted_tables):  # Drop in reverse dependency order
            # Quote the table name to handle reserved keywords
            db.execute(text(f'DROP TABLE IF EXISTS "{table.name}" CASCADE;'))

        db.commit()
        return {"message": "All tables dropped successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred while dropping the tables: {e}")