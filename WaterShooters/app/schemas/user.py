from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from .utils import TokenData

class RoleSchema(BaseModel):
    role_id: Optional[int]  = None
    label: Optional[str]  = None
    del_flag: Optional[bool]  = None

    class Config:
        orm_mode = True


class ComplaintSuggestionSchema(BaseModel):
    cs_id: Optional[int]  = None
    user_id: Optional[int]  = None
    plant_id: Optional[int]  = None
    message: Optional[str]  = None
    type: Optional[int]  = None  # e.g., 0=Complaint, 1=Suggestion
    is_addressed: Optional[bool]  = None
    created_at: Optional[datetime]  = None
    updated_at: Optional[datetime]  = None
    del_flag: Optional[bool]  = None

    class Config:
        orm_mode = True


class UserSchema(BaseModel):
    user_id: Optional[int] =None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    aadhar_no: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_no: Optional[int] = None
    address: Optional[str] = None
    qualification: Optional[str] = None
    DOB: Optional[datetime]  = None
    created_at: Optional[datetime]  = None
    updated_at: Optional[datetime]  = None
    is_verified: Optional[bool]  = None
    last_login: Optional[datetime]  = None
    otp: Optional[str]  = None
    is_admin: Optional[bool]  = None
    del_flag: Optional[bool]  = None
    role_id: Optional[int]  = None
    page: Optional[int]  = None
    limit: Optional[int]  = None
    class Config:
        orm_mode = True


class LoginRequest(BaseModel):
    email: str
    password: str


class passwordReset(BaseModel):
    token_data : Optional[TokenData] = None
    token: str
    new_password: str

class forgetEmail(BaseModel):
    email: str

class VerifyEmail(forgetEmail):
    otp : str