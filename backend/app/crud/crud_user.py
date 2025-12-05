# app/crud/crud_user.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User, FarmerProfile, BuyerProfile
from app.schemas.user import UserCreate, UserUpdate, FarmerProfileCreate, BuyerProfileCreate, FarmerProfileUpdate, BuyerProfileUpdate


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    db_user = User(
        phone_number=user["phone_number"],
        user_type=user["user_type"],
        # whatsapp_id=user["whatsapp_id"],
        # language_preference=user["language_preference"],
        # is_verified=user["is_verified"] ,
        # village=user["village"],
        # location=user["location"]
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: str) -> Optional[User]:
    """Get a user by ID."""

    return db.query(User).filter(User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get a list of users."""
    return db.query(User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: str, user_update: UserUpdate) -> Optional[User]:
    """Update a user."""
    db_user = get_user(db, user_id)
    if db_user:
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: str) -> bool:
    """Delete a user."""
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


def get_user_by_phone(db: Session, phone_number: str) -> Optional[User]:
    """Get a user by phone number."""
    return db.query(User).filter(User.phone_number == phone_number).first()


def create_farmer_profile(db: Session, farmer_profile: FarmerProfileCreate, user_id: str) -> FarmerProfile:
    """Create a farmer profile for a user."""
    db_farmer_profile = FarmerProfile(
        user_id=user_id,
        farm_size_hectares=farmer_profile.farm_size_hectares,
        primary_crops=farmer_profile.primary_crops,
        average_yield_kg=farmer_profile.average_yield_kg,
        storage_capacity_kg=farmer_profile.storage_capacity_kg,
        storage_type=farmer_profile.storage_type,
        typical_price_range=farmer_profile.typical_price_range
    )
    db.add(db_farmer_profile)
    db.commit()
    db.refresh(db_farmer_profile)
    return db_farmer_profile


def create_buyer_profile(db: Session, buyer_profile: BuyerProfileCreate, user_id: str) -> BuyerProfile:
    """Create a buyer profile for a user."""
    db_buyer_profile = BuyerProfile(
        user_id=user_id,
        business_name=buyer_profile.business_name,
        buyer_type=buyer_profile.buyer_type,
        typical_purchase_volume_kg=buyer_profile.typical_purchase_volume_kg,
        preferred_crops=buyer_profile.preferred_crops,
        service_radius_km=buyer_profile.service_radius_km
    )
    db.add(db_buyer_profile)
    db.commit()
    db.refresh(db_buyer_profile)
    return db_buyer_profile


def get_farmer_profile(db: Session, user_id: str) -> Optional[FarmerProfile]:
    """Get a farmer profile by user ID."""
    return db.query(FarmerProfile).filter(FarmerProfile.user_id == user_id).first()


def get_buyer_profile(db: Session, user_id: str) -> Optional[BuyerProfile]:
    """Get a buyer profile by user ID."""
    return db.query(BuyerProfile).filter(BuyerProfile.user_id == user_id).first()


def update_farmer_profile(db: Session, user_id: str, farmer_profile_update: FarmerProfileUpdate) -> Optional[FarmerProfile]:
    """Update a farmer profile."""
    db_farmer_profile = get_farmer_profile(db, user_id)
    if db_farmer_profile:
        update_data = farmer_profile_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_farmer_profile, field, value)
        db.commit()
        db.refresh(db_farmer_profile)
    return db_farmer_profile


def update_buyer_profile(db: Session, user_id: str, buyer_profile_update: BuyerProfileUpdate) -> Optional[BuyerProfile]:
    """Update a buyer profile."""
    db_buyer_profile = get_buyer_profile(db, user_id)
    if db_buyer_profile:
        update_data = buyer_profile_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_buyer_profile, field, value)
        db.commit()
        db.refresh(db_buyer_profile)
    return db_buyer_profile
