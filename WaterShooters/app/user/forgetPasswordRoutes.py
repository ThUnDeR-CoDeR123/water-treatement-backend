from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.user.crud import getUserByEmail, send_mail,hash_password
import random
from typing import Optional

class ForgetPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str

forgetRouter = APIRouter(prefix="/auth", tags=["forgetPassword"])

@forgetRouter.post("/forget-password")
async def forget_password(request: ForgetPasswordRequest, db: Session = Depends(get_db)):
    """Send OTP to user's email for password reset"""
    user = getUserByEmail(request.email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )
    
    # Generate 6-digit OTP
    otp = ''.join(random.choices('0123456789', k=6))
    
    # Save OTP to user model
    user.otp = otp
    db.commit()
    
    # Send OTP via email
    html_content = f"""
        <h2>Password Reset Request</h2>
        <p>Your OTP for password reset is: <strong>{otp}</strong></p>
        <p>This OTP will expire in 10 minutes.</p>
        <p>If you did not request this password reset, please ignore this email.</p>
    """
    
    await send_mail(
        email=request.email,
        subject="Password Reset OTP",
        htmlbody=html_content
    )
    
    return {"message": "OTP has been sent to your email", "otp": otp}

@forgetRouter.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using OTP"""
    user = getUserByEmail(request.email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )
    
    if not user.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OTP was generated for this user"
        )
    
    if user.otp != request.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
      # Update password and clear OTP
    
    user.password = hash_password(request.new_password)
    user.otp = None
    db.commit()
    
    await send_mail(
        email=request.email,
        subject="Password Reset Successful",
        htmlbody="<h2>Password Reset Successful</h2><p>Your password has been successfully reset.</p>"
    )
    
    return {"message": "Password has been reset successfully"}

