from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import  UserSchema,LoginRequest
from app.schemas.utils import  TokenData

from app.database import get_db
from app.models.base import User
from app.crud.user import updateUser,updateLastLogin,createUser,getAllUsers,deleteAllTable
from typing import Annotated,List
from .jwt import get_current_user,getAdmin,authenticate_user,create_access_token,get_password_hash
from starlette.responses import JSONResponse
import json
import traceback
from sqlalchemy import text
from app.config import settings
import httpx
import time


tokenRouter = APIRouter(prefix="/api/v1/user")

#get user data
@tokenRouter.get("/me", response_model=UserSchema)
async def read_user(user : Annotated[TokenData,Depends(get_current_user)],db: Annotated[Session, Depends(get_db)]):
    
    return user

    
#get all user
@tokenRouter.post("/all", response_model=List[UserSchema])
async def read_user_all(user : Annotated[TokenData,Depends(getAdmin)],filter: UserSchema | None,db: Annotated[Session, Depends(get_db)]):

    users=getAllUsers(db,filter)
    return users



#Update user
@tokenRouter.put("/update", response_model=UserSchema)
async def update_user(user : Annotated[TokenData,Depends(get_current_user)],db: Annotated[Session, Depends(get_db)],updateUser: UserSchema):
    # token_data = await getTokenDataFromAuthService(token)
    updated_user = update_user( user,db,updateUser)  # Use the ID from the current user

    return updated_user




# HERE THE REQUEST BODY COMES AS {"email": "example@example.com","password":"somepassword"}
@tokenRouter.post("/login")
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
@tokenRouter.post("/register")
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
        raise HTTPException(status_code=503, detail=f"{str(e)}")



# @tokenRouter.post("/verify_user")
# async def verify_email(data : Token,db : Annotated[Session , Depends(get_db) ]):
#     # Fetch the user from the database
#     token_data = await getTokenDataFromAuthService(data.token)
#     print(token_data)
#     if token_data.flag != "SIGNUP":
#         return JSONResponse(
#         status_code=401,
#         content={
#             "error": "Invalid token",
#             "message": "The provided token is invalid or expired. Please request a new token."
#             }
#         )
    
#     updateVerified(token_data.id,db)
#     return {"message": "user verified successfully!"}



# @tokenRouter.post("/admin/login")
# async def adminLogin(
#     form_data: LoginRequest, db : Annotated[Session , Depends(get_db) ]):

#     #HERE THE REQUEST THAT IS BEING SENT TO AUTH IS IN {"username": "example@abc.com", "password": "somepassword"}

#     print(settings.auth_service_url)
#     user =  authenticate_user(form_data.email, form_data.password, db=db)

#     if not user :
#         return JSONResponse(status_code=401,content={"message":"Invalid Credentials!"})

#     if not user.is_admin:
#         return JSONResponse(status_code=401,content={"message":"Admin not found!"})
    
#     try:
#         response = await generateToken(id=user.id, username=form_data.email,flag="LOGIN",is_admin=user.is_admin)
        
        
#         # If the status code isn't 200 OK but no error was raised
#         if response.status_code != 200:
#             if response.status_code == 401:
#                 return JSONResponse(
#                     status_code=401,
#                     content={"message": "Unauthorized: The provided credentials are incorrect or expired."}
#                 )
#             return JSONResponse(
#                 status_code=response.status_code,
#                 content={"message": "Unexpected status code returned from auth service."}
#             )
#         updateLastLogin(user,db)

#         # Successfully return the token or relevant response from auth service
#         return response.json()

#     except Exception as e:
#         return JSONResponse(
#             status_code=500,
#             content={"error": f"An unexpected error occurred: {str(e)}",
#                      "message": "An unexpected error occurred. Please try again!"}
#         )




# # Delete user
# @tokenRouter.delete("/delete",response_model=DeleteUser)
# async def delete_user(token_data: TokenData | None,db: Annotated[Session, Depends(get_db)]):
#     # token_data = await getTokenDataFromAuthService(token)
#     if token_data is None :
#         return JSONResponse(status_code=401,content={"message": "missing Authorization header"})
#     if token_data.flag != "LOGIN":
#         return JSONResponse(status_code=401,content={"message":"Invalid Credentials!"})
#     deleted_user=deleteUser(token_data.id,db)
#     return DeleteUser(msg = "User deleted successfully", username=deleted_user.email)



# #truncate user table
# @tokenRouter.delete("/users/truncate")
# def drop_user(msg : Annotated[dict, Depends(truncateUsersTable)],msg1 : Annotated[dict, Depends(truncateUserTable)]):
#     return msg

@tokenRouter.delete("/tables/drop")
def drop_user(msg : Annotated[bool, Depends(deleteAllTable)]):
    if msg:
        return {'msg': "dropped all tables successfully!"}
    


# TABLE_NAMES = [
#     "users",
#     "entitlement",
#     "cryptowallet",
#     "referralwallet",
#     "referrals",
#     "transactions"
# ]
 


# @tokenRouter.get("/schemas")
# async def get_model_table_schemas(db: Session = Depends(get_db)):
#     """
#     Get schema information for hardcoded tables from the models and display it clustered by table.
#     """
#     try:
#         # SQL query to get column information for specified tables
#         query = text("""
#             SELECT 
#                 table_schema, 
#                 table_name, 
#                 column_name, 
#                 data_type, 
#                 is_nullable, 
#                 character_maximum_length
#             FROM information_schema.columns
#             WHERE table_name = ANY(:table_names)
#             ORDER BY table_name, ordinal_position;
#         """)

#         # Execute the query
#         result = db.execute(query, {"table_names": TABLE_NAMES}).mappings()
#         clustered_schemas = {}

#         # Process the query results to cluster by table name
#         for row in result:
#             table_name = row["table_name"]
#             column_info = {
#                 "column_name": row["column_name"],
#                 "data_type": row["data_type"],
#                 "is_nullable": row["is_nullable"],
#                 "character_max_length": row["character_maximum_length"]
#             }
#             if table_name not in clustered_schemas:
#                 clustered_schemas[table_name] = {
#                     "table_schema": row["table_schema"],
#                     "columns": []
#                 }
#             clustered_schemas[table_name]["columns"].append(column_info)

#         # Convert clustered schemas to a list for JSON response
#         formatted_response = [
#             {"table_name": table, "schema": schema}
#             for table, schema in clustered_schemas.items()
#         ]

#         # Return the clustered schemas as JSON
#         return JSONResponse(status_code=200, content={"schemas": formatted_response})

#     except Exception as e:
#         # Capture and return detailed exception
#         error_details = traceback.format_exc()
#         return JSONResponse(status_code=500, content={"error": str(e), "details": error_details})
