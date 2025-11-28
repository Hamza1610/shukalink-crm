# app/models/logistics.py
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Enum, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.db.base_class import Base
from enum import Enum as PyEnum

class LogisticsStatus(PyEnum):
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    IN_TRANSIT = "in_transit"
    DELAYED = "delayed"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TransportType(PyEnum):
    TRUCK_SMALL = "truck_small"  # 1-3 tons
    TRUCK_MEDIUM = "truck_medium"  # 3-5 tons
    TRUCK_LARGE = "truck_large"  # 5+ tons
    VAN = "van"  # Smaller loads
    MOTORCYCLE = "motorcycle"  # Very small urgent deliveries

class LogisticsRequest(Base):
    __tablename__ = "logistics_requests"

    id = Column(String, primary_key=True, default=lambda: f"log_{uuid4().hex[:8]}")
    transaction_id = Column(String, ForeignKey("transactions.id"), unique=True, nullable=False)
    
    # Location details
    pickup_location = Column(Geometry("POINT", srid=4326), nullable=False)
    pickup_description = Column(String, nullable=False)  # "Mallam Ibrahim's farm, Gwarzo"
    dropoff_location = Column(Geometry("POINT", srid=4326), nullable=False)
    dropoff_description = Column(String, nullable=False)  # "Fatima's warehouse, Kano city"
    
    # Scheduling
    scheduled_pickup = Column(DateTime, nullable=False)
    estimated_delivery = Column(DateTime, nullable=True)
    actual_pickup = Column(DateTime, nullable=True)
    actual_delivery = Column(DateTime, nullable=True)
    
    # Transport details
    transport_type = Column(Enum(TransportType), default=TransportType.TRUCK_SMALL)
    estimated_cost = Column(Float, nullable=True)
    actual_cost = Column(Float, nullable=True)
    
    # Status tracking
    status = Column(Enum(LogisticsStatus), default=LogisticsStatus.REQUESTED)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Contact information
    contact_person = Column(String, nullable=True)  # "Driver Aliyu"
    contact_phone = Column(String, nullable=True)  # "+2348034567890"
    
    # Additional data
    vehicle_plate = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    transaction = relationship("Transaction", back_populates="logistics_request")