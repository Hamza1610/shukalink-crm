from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.produce import ProduceListing
from app.schemas.produce import ProduceListingCreate, ProduceListingUpdate


def create_produce_listing(db: Session, produce_listing: ProduceListingCreate) -> ProduceListing:
    """Create a new produce listing."""
    print("TEST: ", produce_listing)
    db_produce_listing = ProduceListing(
        farmer_id=produce_listing["farmer_id"],
        crop_type=produce_listing["crop_type"].value,
        quantity_kg=produce_listing["quantity_kg"],
        quality_grade=produce_listing["quality_grade"].value,
        harvest_date=produce_listing["harvest_date"],
        expected_price_per_kg=produce_listing["expected_price_per_kg"],
        location=produce_listing["location"],
        storage_conditions=produce_listing["storage_conditions"],
        shelf_life_days=produce_listing["shelf_life_days"],
        expires_at=produce_listing["expires_at"],
        voice_message_id=produce_listing["voice_message_id"],
        transcription=produce_listing["transcription"]
    )


    # db_produce_listing = ProduceListing(**produce_listing)
    db.add(db_produce_listing)
    db.commit()
    db.refresh(db_produce_listing)
    return db_produce_listing


def get_produce_listing(db: Session, produce_listing_id: str) -> Optional[ProduceListing]:
    """Get a produce listing by ID."""
    return db.query(ProduceListing).filter(ProduceListing.id == produce_listing_id).first()


def get_produce_listings(db: Session, skip: int = 0, limit: int = 100, farmer_id: Optional[str] = None) -> List[ProduceListing]:
    """Get a list of produce listings all or from a farmer"""
    query = db.query(ProduceListing)
    if farmer_id:
        query = query.filter(ProduceListing.farmer_id == farmer_id)
    return query.offset(skip).limit(limit).all()

def search_produce_listings( 
    db: Session,
    crop_type: Optional[str] = None,
    min_quantity: Optional[int] = None,
    max_price: Optional[float] = None,
    radius_km: Optional[float] = None,
    farmer_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """Get a list of produce listings.base on criteria"""
    query = db.query(ProduceListing)

    if crop_type:
        query = query.filter(ProduceListing.crop_type == crop_type)

    if min_quantity:
        query = query.filter(ProduceListing.quantity_kg >= min_quantity)

    if max_price:
        query = query.filter(ProduceListing.expected_price_per_kg <= max_price)

    # if radius_km:
    #     query = query.filter(ProduceListing.location <= radius_km)

    if farmer_id:
        query = query.filter(ProduceListing.farmer_id == farmer_id)

    return query.offset(skip).limit(limit).all()


# def update_produce_listing(db: Session, produce_listing_id: str, produce_listing_update: ProduceListingUpdate) -> Optional[ProduceListing]:
#     """Update a produce listing."""
#     db_produce_listing = get_produce_listing(db, produce_listing_id)
#     if db_produce_listing:
#         update_data = produce_listing_update
#         for field, value in update_data.items():
#             setattr(db_produce_listing, field, value)
#         db.commit()
#         db.refresh(db_produce_listing)
#     return db_produce_listing


from enum import Enum

def update_produce_listing(db: Session, produce_listing_id: str, produce_listing_update: ProduceListingUpdate):
    db_produce_listing = get_produce_listing(db, produce_listing_id)
    if not db_produce_listing:
        return None

    update_dict = produce_listing_update

    for field, value in update_dict.items():

         # 🚫 Never overwrite NOT NULL fields with None
        if value is None:
            continue
        # Convert Python Enum -> string
        if isinstance(value, Enum):
            value = value.value

        # Convert location WKT to EWKT
        if field == "location":
            value = f"SRID=4326;{value}"

        setattr(db_produce_listing, field, value)

    db.commit()
    db.refresh(db_produce_listing)
    return db_produce_listing



def delete_produce_listing(db: Session, produce_listing_id: str) -> bool:
    """Delete a produce listing."""
    db_produce_listing = get_produce_listing(db, produce_listing_id)
    if db_produce_listing:
        db.delete(db_produce_listing)
        db.commit()
        return True
    return False