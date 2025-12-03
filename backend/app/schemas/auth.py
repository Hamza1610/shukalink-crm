from pydantic import BaseModel
from typing import Optional
from app.schemas.user import UserResponse, UserType


class OTPRequest(BaseModel):
    phone_number: str
    user_type: UserType
    language_preference: Optional[str] = "english"


class OTPVerify(BaseModel):
    phone_number: str
    otp_code: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    phone_number: Optional[str] = None