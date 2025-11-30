from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class LogisticsStatus(Enum):
    REQUESTED = "requested"          # Request submitted
    ASSIGNED = "assigned"            # Driver assigned
    PICKUP_SCHEDULED = "pickup_scheduled"  # Pickup scheduled
    PICKED_UP = "picked_up"          # Produce collected
    IN_TRANSIT = "in_transit"        # On the way
    DELIVERED = "delivered"          # Successfully delivered
    CANCELLED = "cancelled"          # Request cancelled
    FAILED = "failed"                # Delivery failed


class LogisticsRequestCreate(BaseModel):
    transaction_id: str
    pickup_address: str
    delivery_address: str
    pickup_datetime: Optional[datetime] = None
    special_instructions: Optional[str] = None
    vehicle_type: Optional[str] = "motorcycle"  # motorcycle, truck, etc.
    requester_id: Optional[str] = None  # Will be set by the system


class LogisticsRequestUpdate(BaseModel):
    pickup_address: Optional[str] = None
    delivery_address: Optional[str] = None
    pickup_datetime: Optional[datetime] = None
    special_instructions: Optional[str] = None
    vehicle_type: Optional[str] = None
    requester_id: Optional[str] = None
    status: Optional[LogisticsStatus] = None


class LogisticsRequest(BaseModel):
    transaction_id: str
    pickup_address: str
    delivery_address: str
    pickup_datetime: Optional[datetime] = None
    special_instructions: Optional[str] = None
    vehicle_type: Optional[str] = "motorcycle"  # motorcycle, truck, etc.
    requester_id: Optional[str] = None  # Will be set by the system


class LogisticsUpdate(BaseModel):
    status: Optional[LogisticsStatus] = None
    current_location: Optional[str] = None
    driver_notes: Optional[str] = None
    actual_pickup_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None


class LogisticsResponse(BaseModel):
    id: str
    transaction_id: str
    requester_id: str
    pickup_address: str
    delivery_address: str
    status: LogisticsStatus
    vehicle_type: str
    special_instructions: Optional[str] = None
    pickup_datetime: Optional[datetime] = None
    actual_pickup_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    driver_notes: Optional[str] = None
    current_location: Optional[str] = None
    created_at: datetime
    updated_at: datetime