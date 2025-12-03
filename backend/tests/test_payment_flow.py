"""
Test script for Payment Flow
Verifies initialization and webhook processing with database tracking
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from sqlalchemy.types import TypeDecorator, String

# Mock Geometry for SQLite tests
class MockGeometry(TypeDecorator):
    impl = String
    def __init__(self, *args, **kwargs):
        super().__init__()
        
    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(String)

# Mock ARRAY for SQLite tests
class MockArray(TypeDecorator):
    impl = String
    def __init__(self, *args, **kwargs):
        super().__init__()

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(String)

import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Patch Geometry and ARRAY before importing models
import geoalchemy2
import sqlalchemy
geoalchemy2.Geometry = MockGeometry
sqlalchemy.ARRAY = MockArray

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.base_class import Base
from main import app
from app.api.endpoints.payments import get_db
from app.models.user import User
from app.models.transaction import Transaction, TransactionStatus, PaymentStatus, PaymentRecord
from app.models.produce import ProduceListing

# Setup in-memory DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Global session for tests
_db_session = None

def override_get_db():
    global _db_session
    if _db_session:
        yield _db_session
    else:
        # Fallback if not set (shouldn't happen in tests)
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def db_session():
    global _db_session
    _db_session = TestingSessionLocal()
    try:
        yield _db_session
    finally:
        _db_session.close()
        _db_session = None

@pytest.fixture(scope="module")
def test_data(client, db_session):
    # Create users
    seller = User(id="seller1", phone_number="+2348000000001", user_type="farmer")
    buyer = User(id="buyer1", phone_number="+2348000000002", user_type="buyer")
    db_session.add_all([seller, buyer])
    db_session.commit()
    
    # Create listing
    from datetime import datetime, timedelta
    listing = ProduceListing(
        id="list1", 
        farmer_id="seller1", 
        crop_type="Maize", 
        quantity_kg=1000, 
        expected_price_per_kg=500,
        harvest_date=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=30),
        location="POINT(0 0)"
    )
    db_session.add(listing)
    db_session.commit()
    
    # Create transaction
    transaction = Transaction(
        id="tx1",
        produce_listing_id="list1",
        seller_id="seller1",
        buyer_id="buyer1",
        agreed_price_per_kg=500,
        quantity_kg=10,
        total_amount=5000,
        status=TransactionStatus.PENDING
    )
    db_session.add(transaction)
    db_session.commit()
    
    return {"transaction_id": "tx1"}

def test_initialize_payment(client, test_data, db_session):
    """Test payment initialization creates PaymentRecord"""
    
    # Mock PaymentService to avoid real API call
    with patch("app.api.endpoints.payments.PaymentService") as MockService:
        mock_instance = MockService.return_value
        mock_instance.initialize_transaction.return_value = {
            "status": True,
            "message": "Authorization URL created",
            "data": {
                "authorization_url": "https://checkout.paystack.com/test",
                "access_code": "ac_test123",
                "reference": "pay_test_ref"
            }
        }
        
        # Call endpoint
        response = client.post(f"/api/v1/payments/initialize?transaction_id={test_data['transaction_id']}")
        
        #  Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] is True
        assert "authorization_url" in data
        
        # Verify DB record created
        payment_record = db_session.query(PaymentRecord).filter(PaymentRecord.transaction_id == test_data['transaction_id']).first()
        assert payment_record is not None
        assert payment_record.status == PaymentStatus.PENDING
        assert payment_record.amount == 5000
        
        # Verify transaction status updated
        transaction = db_session.query(Transaction).filter(Transaction.id == test_data['transaction_id']).first()
        assert transaction.status == TransactionStatus.PAYMENT_INITIATED

def test_verify_payment_webhook(client, test_data, db_session):
    """Test webhook updates PaymentRecord and Transaction"""
    
    # Ensure payment record exists (from previous test or create new)
    # Let's create one manually to be safe and independent
    tx_id = test_data['transaction_id']
    ref = "pay_webhook_test"
    
    # Check if record exists, if not create
    record = db_session.query(PaymentRecord).filter(PaymentRecord.reference == ref).first()
    if not record:
        from app.models.transaction import PaymentMethod
        record = PaymentRecord(
            transaction_id=tx_id,
            amount=5000,
            reference=ref,
            status="PENDING",  # Use uppercase to match enum
            payment_method=PaymentMethod.PAYSTACK
        )
        db_session.add(record)
        db_session.commit()
    
    # Mock webhook payload
    payload = {
        "event": "charge.success",
        "data": {
            "reference": ref,
            "status": "success",
            "amount": 500000, # kobo
            "gateway_response": "Successful"
        }
    }
    
    # Call webhook endpoint
    # We need to mock signature verification if secret is set
    # Or just rely on the fact that if secret is None (default in test env), it skips verification
    
    with patch("app.core.config.settings.PAYSTACK_WEBHOOK_SECRET", None):
        response = client.post("/api/v1/payments/verify", json=payload)
        
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Verify DB updates
    db_session.refresh(record)
    assert record.status == PaymentStatus.SUCCESS
    
    transaction = db_session.query(Transaction).filter(Transaction.id == tx_id).first()
    assert transaction.status == TransactionStatus.PAYMENT_CONFIRMED

if __name__ == "__main__":
    # Allow running directly
    sys.exit(pytest.main(["-v", __file__]))
