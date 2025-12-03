import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from main import app
from app.core.config import settings
from app.models.user import User
from app.schemas.logistics import LogisticsRequest, LogisticsRequestUpdate

client = TestClient(app)

# Mock DB dependency
@pytest.fixture
def mock_db():
    with patch("app.api.endpoints.whatsapp.get_db") as mock:
        yield mock
    with patch("app.api.endpoints.payments.get_db") as mock:
        yield mock
    with patch("app.api.endpoints.logistics.get_db") as mock:
        yield mock

@pytest.fixture
def mock_user():
    user = Mock(spec=User)
    user.id = "user_123"
    user.phone_number = "+1234567890"
    user.user_type = "farmer"
    return user

@pytest.fixture
def mock_get_current_user(mock_user):
    from app.api.deps import get_current_user
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides = {}

class TestWhatsAppEndpoint:
    @patch("app.api.endpoints.whatsapp.WhatsAppService")
    @patch("app.api.endpoints.whatsapp.get_user_by_phone")
    @patch("app.api.endpoints.whatsapp.create_user")
    def test_whatsapp_webhook_success(self, mock_create_user, mock_get_user, mock_service):
        # Setup mocks
        mock_get_user.return_value = Mock(spec=User)
        mock_service_instance = mock_service.return_value
        mock_service_instance.process_message.return_value = "Test Response"
        
        # Disable signature verification for this test
        with patch.object(settings, 'WHATSAPP_AUTH_TOKEN', None):
            response = client.post(
                "/api/v1/whatsapp/webhook",
                data={
                    "From": "whatsapp:+1234567890",
                    "Body": "Hello",
                    "ProfileName": "Test User"
                }
            )
            
        assert response.status_code == 200
        assert "Test Response" in response.text
        mock_service_instance.process_message.assert_called_once()

class TestPaymentsEndpoint:
    @patch("app.api.endpoints.payments.crud_transaction")
    def test_verify_payment_success(self, mock_crud):
        # Setup mocks
        mock_transaction = Mock()
        mock_crud.get_by_reference.return_value = mock_transaction
        
        # Mock signature verification
        with patch("app.api.endpoints.payments.hmac") as mock_hmac:
            mock_hmac.compare_digest.return_value = True
            
            with patch.object(settings, 'PAYSTACK_WEBHOOK_SECRET', 'secret'):
                response = client.post(
                    "/api/v1/payments/verify",
                    json={
                        "event": "charge.success",
                        "data": {
                            "reference": "txn_123",
                            "amount": 100000
                        }
                    },
                    headers={"x-paystack-signature": "valid_signature"}
                )
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        mock_crud.update.assert_called_once()

class TestLogisticsEndpoint:
    @patch("app.api.endpoints.logistics.crud_transaction")
    @patch("app.api.endpoints.logistics.crud_logistics")
    def test_request_logistics_success(self, mock_crud_logistics, mock_crud_txn, mock_get_current_user, mock_user):
        # Setup mocks
        mock_txn = Mock()
        mock_txn.buyer_id = "user_123"
        mock_txn.seller_id = "other_user"
        mock_crud_txn.get.return_value = mock_txn
        
        mock_crud_logistics.create.return_value = {
            "id": "log_123",
            "transaction_id": "txn_123",
            "requester_id": "user_123",
            "status": "requested",
            "pickup_address": "Farm A",
            "delivery_address": "Market B",
            "vehicle_type": "truck",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        response = client.post(
            "/api/v1/logistics/",
            json={
                "transaction_id": "txn_123",
                "pickup_address": "Farm A",
                "delivery_address": "Market B",
                "vehicle_type": "truck"
            }
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == "log_123"

    @patch("app.api.endpoints.logistics.crud_logistics")
    def test_update_logistics_success(self, mock_crud_logistics, mock_get_current_user, mock_user):
        # Setup mocks
        mock_logistics = Mock()
        mock_logistics.requester_id = "user_123"
        mock_crud_logistics.get.return_value = mock_logistics
        mock_crud_logistics.update.return_value = {
            "id": "log_123",
            "transaction_id": "txn_123",
            "requester_id": "user_123",
            "status": "assigned",
            "pickup_address": "Farm A",
            "delivery_address": "Market B",
            "vehicle_type": "truck",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        response = client.put(
            "/api/v1/logistics/log_123",
            json={
                "status": "assigned"
            }
        )
        
        assert response.status_code == 200
        mock_crud_logistics.update.assert_called_once()
