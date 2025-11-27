# app/crud/crud_logistics.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.logistics import LogisticsRequest
from app.schemas.logistics import LogisticsRequestCreate, LogisticsRequestUpdate


def create_logistics_request(db: Session, logistics_request: LogisticsRequestCreate, transaction_id: str) -> LogisticsRequest:
    """Create a new logistics request."""
    db_logistics_request = LogisticsRequest(
        transaction_id=transaction_id,
        pickup_location=logistics_request.pickup_location,
        pickup_description=logistics_request.pickup_description,
        dropoff_location=logistics_request.dropoff_location,
        dropoff_description=logistics_request.dropoff_description,
        scheduled_pickup=logistics_request.scheduled_pickup,
        estimated_delivery=logistics_request.estimated_delivery,
        transport_type=logistics_request.transport_type,
        estimated_cost=logistics_request.estimated_cost,
        status=logistics_request.status,
        contact_person=logistics_request.contact_person,
        contact_phone=logistics_request.contact_phone,
        vehicle_plate=logistics_request.vehicle_plate,
        notes=logistics_request.notes
    )
    db.add(db_logistics_request)
    db.commit()
    db.refresh(db_logistics_request)
    return db_logistics_request


def get_logistics_request(db: Session, logistics_request_id: str) -> Optional[LogisticsRequest]:
    """Get a logistics request by ID."""
    return db.query(LogisticsRequest).filter(LogisticsRequest.id == logistics_request_id).first()


def get_logistics_requests(db: Session, skip: int = 0, limit: int = 100, transaction_id: Optional[str] = None) -> List[LogisticsRequest]:
    """Get a list of logistics requests."""
    query = db.query(LogisticsRequest)
    if transaction_id:
        query = query.filter(LogisticsRequest.transaction_id == transaction_id)
    return query.offset(skip).limit(limit).all()


def update_logistics_request(db: Session, logistics_request_id: str, logistics_request_update: LogisticsRequestUpdate) -> Optional[LogisticsRequest]:
    """Update a logistics request."""
    db_logistics_request = get_logistics_request(db, logistics_request_id)
    if db_logistics_request:
        update_data = logistics_request_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_logistics_request, field, value)
        db.commit()
        db.refresh(db_logistics_request)
    return db_logistics_request


def delete_logistics_request(db: Session, logistics_request_id: str) -> bool:
    """Delete a logistics request."""
    db_logistics_request = get_logistics_request(db, logistics_request_id)
    if db_logistics_request:
        db.delete(db_logistics_request)
        db.commit()
        return True
    return False