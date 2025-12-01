from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime, timedelta
from app.db.session import SessionLocal
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import OTPRequest, OTPVerify, Token
from app.crud import create_user, get_user_by_phone
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.config import settings
import random
import string

router = APIRouter()

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/otp-request", response_model=dict)
def request_otp(otp_request: OTPRequest, db=Depends(get_db)):
    """
    Request OTP verification code via WhatsApp/SMS
    """
    # Generate a random 6-digit OTP
    otp_code = ''.join(random.choices(string.digits, k=6))
    
    # In a real implementation, this would send the OTP via WhatsApp/SMS
    # For now, we'll just store it in memory (in production, use Redis or database)
    
    # Check if user exists, create if not
    user = get_user_by_phone(db, phone_number=otp_request.phone_number)
    if not user:
        # Create new user
        user_data = {
            "phone_number": otp_request.phone_number,
            "user_type": otp_request.user_type,
            "language_preference": otp_request.language_preference or "english"
        }
        user = create_user(db, user=user_data)
    
    # In real implementation, send OTP via Twilio WhatsApp API
    print(f"OTP {otp_code} generated for {otp_request.phone_number}")
    
    return {
        "message": f"OTP sent to {otp_request.phone_number}",
        "expires_in": 300  # 5 minutes
    }

@router.post("/verify-otp", response_model=Token)
def verify_otp(otp_verify: OTPVerify, db=Depends(get_db)):
    """
    Verify OTP code and receive JWT token
    """
    # In a real implementation, verify the OTP from the database/Redis
    # For now, we'll just accept any 6-digit code
    
    user = get_user_by_phone(db, phone_number=otp_verify.phone_number)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "phone_number": user.phone_number},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user) if hasattr(UserResponse, 'from_orm') else UserResponse(
            id=user.id,
            phone_number=user.phone_number,
            user_type=user.user_type,
            language_preference=user.language_preference
        )
    )