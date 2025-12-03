# app/models/produce.py
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, Boolean, Enum, JSON, Text
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.db.base_class import Base
from enum import Enum as PyEnum

from app.schemas.produce import CropType, ListingStatus, QualityGrade

# class CropType(PyEnum):
#     TOMATOES = "tomatoes"
#     ONIONS = "onions"
#     PEPPERS = "peppers"
#     YAMS = "yams"
#     MAIZE = "maize"
#     RICE = "rice"
#     # Add more as needed for MVP

# class QualityGrade(PyEnum):
#     premium = "premium"  # Firm, no blemishes, uniform size
#     good = "good"        # Minor blemishes, mostly firm
#     standard = "standard" # Some soft spots but usable
#     poor = "poor"        # Significant spoilage, urgent sale needed

# class ListingStatus(PyEnum):
#     AVAILABLE = "available"
#     MATCHED = "matched"
#     SOLD = "sold"
#     EXPIRED = "expired"
#     CANCELLED = "cancelled"

class ProduceListing(Base):
    __tablename__ = "produce_listings"

    id = Column(String, primary_key=True, index=True, default=lambda: f"prod_{uuid4().hex[:8]}")
    farmer_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Core produce details
    crop_type = Column(Text, nullable=False)
    # crop_type = Column(Enum(CropType, name="crop_type_enum"), nullable=False)
    quantity_kg = Column(Float, nullable=False)
    quality_grade = Column(Enum(QualityGrade, name="quality_grade_enum"), default=QualityGrade.GOOD)
    harvest_date = Column(DateTime, nullable=False)
    expected_price_per_kg = Column(Float, nullable=False)
    
    # Location & Storage
    location = Column(Geometry("POINT", srid=4326), nullable=False)
    storage_conditions = Column(String, nullable=True)  # "mud_silo", "plastic_bins", etc.
    shelf_life_days = Column(Integer, nullable=True)  # Estimated remaining shelf life
    
    # Status tracking
    status = Column(Enum(ListingStatus, name="produce_listng_status_enum"), default=ListingStatus.AVAILABLE)
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