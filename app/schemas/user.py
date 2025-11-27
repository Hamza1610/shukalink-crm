# app/schemas/user.py
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.models.user import UserType, LanguagePreference, BuyerType


class UserBase(BaseModel):
    phone_number: str
    user_type: UserType
    whatsapp_id: Optional[str] = None
    language_preference: Optional[LanguagePreference] = None
    is_verified: Optional[bool] = False
    village: Optional[str] = None
    location: Optional[str] = None  # This would be a geometry type in practice


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    phone_number: Optional[str] = None
    user_type: Optional[UserType] = None
    whatsapp_id: Optional[str] = None
    language_preference: Optional[LanguagePreference] = None
    is_verified: Optional[bool] = None
    village: Optional[str] = None
    location: Optional[str] = None


class User(UserBase):
    id: str
    created_at: datetime
    last_active: datetime

    class Config:
        from_attributes = True


class FarmerProfileBase(BaseModel):
    farm_size_hectares: Optional[float] = None
    primary_crops: Optional[List[str]] = None
    average_yield_kg: Optional[dict] = None  # JSONB field
    storage_capacity_kg: Optional[int] = None
    storage_type: Optional[str] = None
    typical_price_range: Optional[dict] = None  # JSONB field


class FarmerProfileCreate(FarmerProfileBase):
    pass


class FarmerProfileUpdate(BaseModel):
    farm_size_hectares: Optional[float] = None
    primary_crops: Optional[List[str]] = None
    average_yield_kg: Optional[dict] = None
    storage_capacity_kg: Optional[int] = None
    storage_type: Optional[str] = None
    typical_price_range: Optional[dict] = None


class FarmerProfile(FarmerProfileBase):
    id: str
    user_id: str

    class Config:
        from_attributes = True


class BuyerProfileBase(BaseModel):
    business_name: Optional[str] = None
    buyer_type: Optional[BuyerType] = None
    typical_purchase_volume_kg: Optional[int] = None
    preferred_crops: Optional[List[str]] = None
    service_radius_km: Optional[int] = 50
    reliability_score: Optional[float] = 5.0
    payment_timeliness_score: Optional[float] = 5.0


class BuyerProfileCreate(BuyerProfileBase):
    pass


class BuyerProfileUpdate(BaseModel):
    business_name: Optional[str] = None
    buyer_type: Optional[BuyerType] = None
    typical_purchase_volume_kg: Optional[int] = None
    preferred_crops: Optional[List[str]] = None
    service_radius_km: Optional[int] = None
    reliability_score: Optional[float] = None
    payment_timeliness_score: Optional[float] = None


class BuyerProfile(BuyerProfileBase):
    id: str
    user_id: str

    class Config:
        from_attributes = True