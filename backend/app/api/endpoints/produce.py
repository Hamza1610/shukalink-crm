from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.db.session import SessionLocal
from app.schemas.produce import ProduceCreate, ProduceResponse, ProduceSearch, ProduceListingUpdate
from app.crud import create_produce_listing, get_produce_listing, delete_produce_listing, update_produce_listing, get_produce_listings, search_produce_listings
from app.crud import crud_produce
from app.api.deps import get_current_user
from app.models.user import User, UserType

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ProduceResponse)
def create_produce(
    produce_in: ProduceCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Create a new produce listing (Farmer only)
    """

    # Verify user is a farmer
    if current_user.user_type != UserType.FARMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only farmers can create produce listings"
        )
    
    # Add farmer_id to the produce data
    produce_data = produce_in.model_dump()

    produce_data["farmer_id"] = current_user.id
    


    # print("Produce", produce_data)
    # produce = create_produce_listing(db, produce_data)
    # return produce

    # produce_data = {
    #     **produce_in.model_dump(),
    #     farmer_id=current_user.id
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.db.session import SessionLocal
from app.schemas.produce import ProduceCreate, ProduceResponse, ProduceSearch, ProduceListingUpdate
from app.crud import create_produce_listing, get_produce_listing, delete_produce_listing, update_produce_listing, get_produce_listings, search_produce_listings
from app.crud import crud_produce
from app.api.deps import get_current_user
from app.models.user import User, UserType

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ProduceResponse)
def create_produce(
    produce_in: ProduceCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Create a new produce listing (Farmer only)
    """

    # Verify user is a farmer
    if current_user.user_type != UserType.FARMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only farmers can create produce listings"
        )
    
    # Add farmer_id to the produce data
    produce_data = produce_in.model_dump()

    produce_data["farmer_id"] = current_user.id
    


    # print("Produce", produce_data)
    # produce = create_produce_listing(db, produce_data)
    # return produce

    # produce_data = {
    #     **produce_in.model_dump(),
    #     farmer_id=current_user.id
    # }

    return create_produce_listing(db, produce_data)



@router.get("/all", response_model=List[ProduceResponse])
def get_all_produce(
    skip: int = 0,
    limit: int = 100,
    farmer_id: Optional[str] = None,
    db=Depends(get_db)
):
    """
    Search and list available produce
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Fetching all produce: skip={skip}, limit={limit}, farmer_id={farmer_id}")
    
    try:
        filters = {
            "skip": skip,
            "limit": limit
        }

        if farmer_id:
            filters["farmer_id"] = farmer_id

        produce_list = get_produce_listings(db, **filters)
        logger.info(f"Found {len(produce_list)} produce items")
        return produce_list
    except Exception as e:
        logger.error(f"Error fetching produce: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ProduceResponse])
def search_produce(
    crop_type: Optional[str] = None,
    min_quantity: Optional[int] = None,
    radius_km: Optional[int] = None,
    max_price: Optional[float] = None,
    farmer_id: Optional[str] = None,
    db=Depends(get_db)
):
    """
    Search and list available produce
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Searching produce: crop={crop_type}, min_qty={min_quantity}, max_price={max_price}, farmer={farmer_id}")

    try:
        filters = {}
        if crop_type:
            filters["crop_type"] = crop_type
        if min_quantity:
            filters["min_quantity"] = min_quantity
        if max_price:
            filters["max_price"] = max_price
        if radius_km:
            filters["radius_km"] = radius_km
        if farmer_id:
            filters["farmer_id"] = farmer_id
        
        produce_list = search_produce_listings(db, **filters)
        logger.info(f"Search found {len(produce_list)} items")
        return produce_list
    except Exception as e:
        logger.error(f"Error searching produce: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{produce_id}", response_model=ProduceResponse)
def get_produce_details(
    produce_id: str,
    db=Depends(get_db)
):
    """
    Get a specific produce listing by ID
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Fetching produce details: {produce_id}")

    try:
        produce = get_produce_listing(db, produce_id)
        if not produce:
            logger.warning(f"Produce not found: {produce_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produce listing not found"
            )
        return produce
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching produce details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{produce_id}", response_model=ProduceResponse)
def update_produce(
    produce_id: str,
    produce_in: ProduceListingUpdate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Update a produce listing (Farmer only)
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Updating produce {produce_id} by user {current_user.id}")

    try:
        # Get the existing produce
        existing_produce = get_produce_listing(db, produce_id)
        if not existing_produce:
            logger.warning(f"Produce not found for update: {produce_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produce listing not found"
            )
        
        # Verify that the current user is the owner
        if existing_produce.farmer_id != current_user.id:
            logger.warning(f"User {current_user.id} unauthorized to update produce {produce_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this produce listing"
            )
        
        # Update the produce
        updated_produce = update_produce_listing(db, existing_produce.id, produce_in.model_dump())
        logger.info(f"Produce updated successfully: {produce_id}")
        return updated_produce
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating produce: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{produce_id}")
def delete_produce(
    produce_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Delete a produce listing (Farmer only)
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Deleting produce {produce_id} by user {current_user.id}")

    try:
        # Get the existing produce
        existing_produce = get_produce_listing(db, produce_id)
        if not existing_produce:
            logger.warning(f"Produce not found for deletion: {produce_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produce listing not found"
            )
        
        # Verify that the current user is the owner
        if existing_produce.farmer_id != current_user.id:
            logger.warning(f"User {current_user.id} unauthorized to delete produce {produce_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this produce listing"
            )
        
        # Delete the produce
        delete_produce_listing(db, produce_id)
        logger.info(f"Produce deleted successfully: {produce_id}")
        return {"message": "Produce listing deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting produce: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))