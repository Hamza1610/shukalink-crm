from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum


class CropType(Enum):
    TOMATOES = "tomatoes"
    ONIONS = "onions"
    PEPPERS = "peppers"
    YAMS = "yams"
    MAIZE = "maize"
    RICE = "rice"
    # Add more as needed for MVP


class QualityGrade(Enum):
    PREMIUM = "PREMIUM"  # Firm, no blemishes, uniform size
    GOOD = "GOOD"        # Minor blemishes, mostly firm
    STANDARD = "STANDARD" # Some soft spots but usable
    POOR = "POOR"        # Significant spoilage, urgent sale needed


class ListingStatus(Enum):
    AVAILABLE = "AVAILABLE"
    MATCHED = "MATCHED"
    SOLD = "SOLD"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class ProduceListingCreate(BaseModel):
    crop_type: CropType # I removed the ENUM TYPE to allow different croptype
    quantity_kg: float
    quality_grade: Optional[QualityGrade] = QualityGrade.GOOD
    harvest_date: datetime
    expected_price_per_kg: float
    location: str  # Will be handled as coordinates in the service layer
    storage_conditions: Optional[str] = None
    shelf_life_days: Optional[int] = None
    expires_at: datetime
    voice_message_id: Optional[str] = None
    transcription: Optional[str] = None


class ProduceListingUpdate(BaseModel):
    crop_type: Optional[CropType] = None
    quantity_kg: Optional[float] = None
    quality_grade: Optional[QualityGrade] = None
    harvest_date: Optional[datetime] = None
    expected_price_per_kg: Optional[float] = None
    location: Optional[str] = None  # Will be handled as coordinates in the service layer
    storage_conditions: Optional[str] = None
    shelf_life_days: Optional[int] = None
    expires_at: Optional[datetime] = None
    voice_message_id: Optional[str] = None
    transcription: Optional[str] = None
    status: Optional[ListingStatus] = None


class ProduceListingResponse(BaseModel):
    id: str
    farmer_id: str
    crop_type: CropType
    quantity_kg: float
    quality_grade: QualityGrade
    harvest_date: datetime
    expected_price_per_kg: float
    storage_conditions: Optional[str] = None
    shelf_life_days: Optional[int] = None
    status: ListingStatus
    created_at: datetime
    expires_at: datetime
    voice_message_id: Optional[str] = None
    transcription: Optional[str] = None


class ProduceSearch(BaseModel):
    crop_type: Optional[str] = None
    min_quantity: Optional[float] = None
    max_price: Optional[float] = None
    location: Optional[str] = None
    radius_km: Optional[int] = 25
    quality_grade: Optional[QualityGrade] = None


# Aliases for backward compatibility with endpoints
ProduceCreate = ProduceListingCreate
ProduceResponse = ProduceListingResponse
ProduceUpdate = ProduceListingUpdate