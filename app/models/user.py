# app/models/user.py
from typing import Optional, List
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Enum, DateTime, Text, Float, ForeignKey, Boolean, ARRAY, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from enum import Enum as PyEnum

from app.db.base_class import Base

class UserType(PyEnum):
    FARMER = "farmer"
    BUYER = "buyer"
    ADMIN = "admin"
    AGGREGATOR = "aggregator"

class LanguagePreference(PyEnum):
    ENGLISH = "english"
    HAUSA = "hausa"
    PIDGIN = "pidgin"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: f"usr_{uuid4().hex[:8]}")
    phone_number = Column(String, unique=True, index=True, nullable=False)
    user_type = Column(Enum(UserType), default=UserType.FARMER, nullable=False)
    
    # Authentication & Profile
    whatsapp_id = Column(String, unique=True, nullable=True)  # WhatsApp Business API identifier
    language_preference = Column(Enum(LanguagePreference), default=LanguagePreference.HAUSA)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Location Data (Minimal PII)
    village = Column(String, nullable=True)
    location = Column(Geometry("POINT", srid=4326), nullable=True)  # GPS coordinates
    
    # Relationships
    farmer_profile = relationship("FarmerProfile", uselist=False, back_populates="user")
    buyer_profile = relationship("BuyerProfile", uselist=False, back_populates="user")
    produce_listings = relationship("ProduceListing", back_populates="farmer")
    transactions_as_seller = relationship("Transaction", foreign_keys="[Transaction.seller_id]", back_populates="seller")
    transactions_as_buyer = relationship("Transaction", foreign_keys="[Transaction.buyer_id]", back_populates="buyer")
    voice_messages = relationship("VoiceMessage", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

# app/models/user.py (continued)

class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    id = Column(String, primary_key=True, default=lambda: f"fp_{uuid4().hex[:8]}")
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Farm Data
    farm_size_hectares = Column(Float, nullable=True)
    primary_crops = Column(ARRAY(String), default=list)
    average_yield_kg = Column(JSONB, nullable=True)  # Per crop type
    storage_capacity_kg = Column(Integer, nullable=True)
    storage_type = Column(String, nullable=True)  # "mud_silo", "plastic_bins", etc.
    
    # Economic Data
    typical_price_range = Column(JSONB, nullable=True)  # {"tomatoes": {"min": 500, "max": 1500}}
    
    # Relationships
    user = relationship("User", back_populates="farmer_profile")

class BuyerType(PyEnum):
    TRADER = "trader"
    AGGREGATOR = "aggregator"
    PROCESSOR = "processor"
    RETAILER = "retailer"

class BuyerProfile(Base):
    __tablename__ = "buyer_profiles"

    id = Column(String, primary_key=True, default=lambda: f"bp_{uuid4().hex[:8]}")
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Business Data
    business_name = Column(String, nullable=True)
    buyer_type = Column(Enum(BuyerType), default=BuyerType.TRADER)
    typical_purchase_volume_kg = Column(Integer, nullable=True)
    preferred_crops = Column(ARRAY(String), default=list)
    service_radius_km = Column(Integer, default=50)
    
    # Relationship metrics
    reliability_score = Column(Float, default=5.0)  # 1-5 scale
    payment_timeliness_score = Column(Float, default=5.0)  # 1-5 scale
    
    # Relationships
    user = relationship("User", back_populates="buyer_profile")