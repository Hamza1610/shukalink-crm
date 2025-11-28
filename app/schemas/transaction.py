from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class TransactionStatus(Enum):
    PENDING = "pending"          # Matched but not paid
    PAYMENT_INITIATED = "payment_initiated"  # Payment link sent
    PAYMENT_CONFIRMED = "payment_confirmed"  # Payment received
    IN_LOGISTICS = "in_logistics" # Transport arranged
    DELIVERED = "delivered"       # Successfully delivered
    COMPLETED = "completed"       # Payment released to farmer
    DISPUTED = "disputed"         # Problem reported
    CANCELLED = "cancelled"       # Transaction cancelled


class TransactionCreate(BaseModel):
    produce_listing_id: str
    seller_id: str  # Farmer
    buyer_id: str
    agreed_price_per_kg: float
    quantity_kg: float
    total_amount: float  # Calculated: price * quantity
    status: Optional[TransactionStatus] = TransactionStatus.PENDING


class TransactionUpdate(BaseModel):
    produce_listing_id: Optional[str] = None
    seller_id: Optional[str] = None
    buyer_id: Optional[str] = None
    agreed_price_per_kg: Optional[float] = None
    quantity_kg: Optional[float] = None
    total_amount: Optional[float] = None
    status: Optional[TransactionStatus] = None


class TransactionResponse(BaseModel):
    id: str
    produce_listing_id: str
    seller_id: str
    buyer_id: str
    agreed_price_per_kg: float
    quantity_kg: float
    total_amount: float
    status: TransactionStatus
    matched_at: datetime
    payment_confirmed_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
# app/models/produce.py
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, Boolean, Enum, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.db.base_class import Base
from enum import Enum as PyEnum

class CropType(PyEnum):
    TOMATOES = "tomatoes"
    ONIONS = "onions"
    PEPPERS = "peppers"
    YAMS = "yams"
    MAIZE = "maize"
    RICE = "rice"
    # Add more as needed for MVP

class QualityGrade(PyEnum):
    PREMIUM = "premium"  # Firm, no blemishes, uniform size
    GOOD = "good"        # Minor blemishes, mostly firm
    STANDARD = "standard" # Some soft spots but usable
    POOR = "poor"        # Significant spoilage, urgent sale needed

class ListingStatus(PyEnum):
    AVAILABLE = "available"
    MATCHED = "matched"
    SOLD = "sold"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class ProduceListing(Base):
    __tablename__ = "produce_listings"

    id = Column(String, primary_key=True, index=True, default=lambda: f"prod_{uuid4().hex[:8]}")
    farmer_id = Column(String, ForeignKey("users.id"), nullable=False)

    # Core produce details
    crop_type = Column(Enum(CropType), nullable=False)
    quantity_kg = Column(Float, nullable=False)
    quality_grade = Column(Enum(QualityGrade), default=QualityGrade.GOOD)
    harvest_date = Column(DateTime, nullable=False)
    expected_price_per_kg = Column(Float, nullable=False)

    # Location & Storage
    location = Column(Geometry("POINT", srid=4326), nullable=False)
    storage_conditions = Column(String, nullable=True)  # "mud_silo", "plastic_bins", etc.
    shelf_life_days = Column(Integer, nullable=True)  # Estimated remaining shelf life

    # Status tracking
    status = Column(Enum(ListingStatus), default=ListingStatus.AVAILABLE)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # Auto-calculated based on crop type + shelf life

    # Voice context (for voice listings)
    voice_message_id = Column(String, ForeignKey("voice_messages.id"), nullable=True)
    transcription = Column(Text, nullable=True)  # Full text of voice listing

    # Relationships
    farmer = relationship("User", back_populates="produce_listings")
    voice_message = relationship("VoiceMessage")
    transactions = relationship("Transaction", back_populates="produce_listing")

    # Calculated field example (in property or service)
    @property
    def freshness_score(self):
        """Calculate freshness based on days since harvest and shelf life"""
        days_since_harvest = (datetime.utcnow() - self.harvest_date).days
        if not self.shelf_life_days or self.shelf_life_days == 0:
            return 0.0
        return max(0.0, 1.0 - (days_since_harvest / self.shelf_life_days))
