import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app  # Changed from app.main to main
from app.models.user import User, UserType
from app.models.produce import ProduceListing
from app.models.transaction import Transaction
from app.models.notification import Notification
from app.models.logistics import LogisticsRequest, LogisticsStatus
from app.db.session import Base
from datetime import datetime


class TestAdminEndpoints:
    """
    Test cases for admin endpoints
    """
    
    def setup_method(self):
        """Setup test fixtures before each test method."""
        # Create test database
        SQLALCHEMY_DATABASE_URL = "sqlite:///./test_admin.db"
        engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        Base.metadata.create_all(bind=engine)
        self.db = TestingSessionLocal()
        
        # Create test client
        self.client = TestClient(app)
        
        # Create test admin user
        self.admin_user = User(
            id="usr_admin123",
            phone_number="+1234567890",
            user_type=UserType.ADMIN,
            village="Test Village",
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
        
        # Create test regular user
        self.regular_user = User(
            id="usr_user123",
            phone_number="+1234567891",
            user_type=UserType.FARMER,
            village="Test Village",
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
        
        # Add users to database
        self.db.add(self.admin_user)
        self.db.add(self.regular_user)
        self.db.commit()
    
    def teardown_method(self):
        """Clean up after each test method."""
        self.db.close()
    
    @patch('app.api.deps.get_current_user')
    def test_get_all_users_as_admin(self, mock_get_current_user):
        """Test getting all users as admin"""
        mock_get_current_user.return_value = self.admin_user
        
        response = self.client.get("/api/v1/admin/users")
        assert response.status_code == 200
    
    @patch('app.api.deps.get_current_user')
    def test_get_all_users_as_non_admin(self, mock_get_current_user):
        """Test getting all users as non-admin (should fail)"""
        mock_get_current_user.return_value = self.regular_user
        
        response = self.client.get("/api/v1/admin/users")
        assert response.status_code == 403
    
    @patch('app.api.deps.get_current_user')
    def test_get_platform_statistics_as_admin(self, mock_get_current_user):
        """Test getting platform statistics as admin"""
        mock_get_current_user.return_value = self.admin_user
        
        response = self.client.get("/api/v1/admin/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "user_breakdown" in data
    
    @patch('app.api.deps.get_current_user')
    def test_get_all_transactions_as_admin(self, mock_get_current_user):
        """Test getting all transactions as admin"""
        mock_get_current_user.return_value = self.admin_user
        
        response = self.client.get("/api/v1/admin/transactions")
        assert response.status_code == 200
    
    @patch('app.api.deps.get_current_user')
    def test_get_all_produce_listings_as_admin(self, mock_get_current_user):
        """Test getting all produce listings as admin"""
        mock_get_current_user.return_value = self.admin_user
        
        response = self.client.get("/api/v1/admin/produce-listings")
        assert response.status_code == 200
    
    @patch('app.api.deps.get_current_user')
    def test_get_all_logistics_requests_as_admin(self, mock_get_current_user):
        """Test getting all logistics requests as admin"""
        mock_get_current_user.return_value = self.admin_user
        
        response = self.client.get("/api/v1/admin/logistics-requests")
        assert response.status_code == 200
    
    @patch('app.api.deps.get_current_user')
    def test_get_all_notifications_as_admin(self, mock_get_current_user):
        """Test getting all notifications as admin"""
        mock_get_current_user.return_value = self.admin_user
        
        response = self.client.get("/api/v1/admin/notifications")
        assert response.status_code == 200
    
    @patch('app.api.deps.get_current_user')
    def test_get_activity_logs_as_admin(self, mock_get_current_user):
        """Test getting activity logs as admin"""
        mock_get_current_user.return_value = self.admin_user
        
        response = self.client.get("/api/v1/admin/activity-logs")
        assert response.status_code == 200
        data = response.json()
        assert "period_days" in data
        assert "summary" in data
    
    @patch('app.api.deps.get_current_user')
    def test_broadcast_notification_as_admin(self, mock_get_current_user):
        """Test broadcasting notification as admin"""
        mock_get_current_user.return_value = self.admin_user
        
        response = self.client.post(
            "/api/v1/admin/notifications/broadcast",
            params={
                "title": "Test Broadcast",
                "message": "This is a test broadcast message",
                "user_type": "farmer"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    @patch('app.api.deps.get_current_user')
    def test_update_logistics_status_as_admin(self, mock_get_current_user):
        """Test updating logistics status as admin"""
        # First create a logistics request in the database
        logistics_request = LogisticsRequest(
            id="log_test123",
            transaction_id="trans_test123",
            pickup_location="POINT(0 0)",
            pickup_description="Test pickup",
            dropoff_location="POINT(1 1)",
            dropoff_description="Test dropoff",
            scheduled_pickup=datetime.utcnow(),
            status=LogisticsStatus.REQUESTED
        )
        self.db.add(logistics_request)
        self.db.commit()
        
        mock_get_current_user.return_value = self.admin_user
        
        response = self.client.put(
            f"/api/v1/admin/logistics-requests/{logistics_request.id}/status",
            params={"status": "CONFIRMED"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "request" in data


if __name__ == "__main__":
    pytest.main([__file__])