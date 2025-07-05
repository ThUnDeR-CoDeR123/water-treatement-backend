from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from app.user.schema import  UserSchema,LoginRequest,TokenData

from app.database import get_db
from app.models.base import User
from app.user.crud import updateUser,updateLastLogin,createUser,getAllUsers,deleteAllTable
from typing import Annotated,List
from app.auth.jwt import get_current_user,getAdmin,authenticate_user,create_access_token,get_password_hash
from starlette.responses import JSONResponse
import json
import traceback
from sqlalchemy import text
from app.config import settings
import httpx
import time


userRouter = APIRouter(prefix="/api/v1/user", tags=["user"])

#get user data
@userRouter.get("/me", response_model=UserSchema)
async def read_user(user : Annotated[TokenData,Depends(get_current_user)],db: Annotated[Session, Depends(get_db)]):
    
    return user

    
#get all user
@userRouter.post("/all", response_model=List[UserSchema])
async def read_user_all(user : Annotated[TokenData,Depends(getAdmin)],filter: UserSchema | None,db: Annotated[Session, Depends(get_db)]):

    users=getAllUsers(db,filter)
    return users



#Update user
@userRouter.put("/update", response_model=UserSchema)
async def update_user(user : Annotated[TokenData,Depends(get_current_user)],db: Annotated[Session, Depends(get_db)],updateUser: UserSchema):
    # token_data = await getTokenDataFromAuthService(token)
    updated_user = update_user( user,db,updateUser)  # Use the ID from the current user

    return updated_user




# HERE THE REQUEST BODY COMES AS {"email": "example@example.com","password":"somepassword"}
@userRouter.post("/login")
async def userLogin(
    form_data: LoginRequest, db : Annotated[Session , Depends(get_db) ]):

    #HERE THE REQUEST THAT IS BEING SENT TO AUTH IS IN {"username": "example@abc.com", "password": "somepassword"}

    user =  authenticate_user(form_data.email, form_data.password, db=db)
    if not user :
        return JSONResponse(status_code=401,content={"error":"Invalid Credentials!"})
    # if user.is_admin:
    #     return JSONResponse(status_code=401,content={"error":"Admin not found!"})
    if not user.is_verified:
        return JSONResponse(status_code=401,content={"error":"User not verified!"})
    
    try:
        json={            
                    "sub": user.user_id,
                    "email": user.email,
                    "role": user.role_id,
                    "is_admin" : user.is_admin
                }
        jwt = create_access_token(json,flag="LOGIN")
        
        print("token generated")
        # If the status code isn't 200 OK but no error was raised
        
        print("returning JSONResponse")
        updateLastLogin(user,db)

        # Successfully return the token or relevant response from auth service
        return JSONResponse(status_code=200, content={"token": jwt})

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"An unexpected error occurred: {str(e)}"}
        )

#Create User Account
@userRouter.post("/register")
async def create_user(user: UserSchema ,db: Annotated[Session, Depends(get_db)]):
    try:
            existing_user = db.query(User).filter(User.email == user.email).first()
            if existing_user:
                raise HTTPException(status_code=422, detail="Email already registered")
            existing_user = db.query(User).filter(User.phone_no == user.phone_no).first()
            if existing_user:
                raise HTTPException(status_code=422, detail="Phone number already registered")
            existing_user = db.query(User).filter(User.aadhar_no == user.aadhar_no).first()
            if existing_user:
                raise HTTPException(status_code=422, detail="Aadhar already registered")

            user.password = get_password_hash(user.password)

            user =createUser(db,user)

            json={            
                        "sub": user.user_id,
                        "email": user.email,
                        "role": user.role_id,
                        "is_admin" : user.is_admin
                    }
            jwt = create_access_token(json,flag="LOGIN")
            # otp=createOtp(forgetEmail(email=user.email),db)
            return JSONResponse(status_code=200, content={"token": jwt})  
    except Exception as e:
        db.rollback()
        print(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=503, detail=f"{str(e)}")
