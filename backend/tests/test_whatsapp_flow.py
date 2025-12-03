import pytest
from unittest.mock import Mock, patch
from app.workers.whatsapp_flow import WhatsAppService
from app.models.user import User


class TestWhatsAppFlow:
    """
    Test cases for WhatsApp service flow
    """
    
    def setup_method(self):
        """Setup test fixtures before each test method."""
        self.whatsapp_service = WhatsAppService()
        
        # Create a mock user
        self.mock_user = Mock(spec=User)
        self.mock_user.phone_number = "+1234567890"
        self.mock_user.village = "Test Village"
        self.mock_user.user_type = "farmer"
        self.mock_user.id = 1
        self.mock_user.created_at = None

    def test_initialization(self):
        """Test that WhatsApp service initializes properly"""
        assert self.whatsapp_service.ai_agent is not None
        assert self.whatsapp_service.advisory_service is not None
        assert self.whatsapp_service.logistics_service is not None
        assert self.whatsapp_service.payment_service is not None
        assert self.whatsapp_service.crm_service is not None

    def test_show_main_menu(self):
        """Test main menu response"""
        response = self.whatsapp_service.show_main_menu(self.mock_user)
        
        assert "AgriConnect WhatsApp Service" in response
        assert "Hello Test Village!" in response
        assert "*Crop Advisory*" in response
        assert "*Logistics*" in response
        assert "*Payments*" in response
        assert "*My Profile*" in response
        assert "*Subscription*" in response
        assert "*Support*" in response

    def test_process_message_hello(self):
        """Test processing 'hello' message"""
        response = self.whatsapp_service.process_message(self.mock_user, "hello", None)
        
        assert "AgriConnect WhatsApp Service" in response
        assert "Hello Test Village!" in response

    def test_process_message_menu(self):
        """Test processing 'menu' message"""
        response = self.whatsapp_service.process_message(self.mock_user, "menu", None)
        
        assert "AgriConnect WhatsApp Service" in response
        assert "Choose an option" in response

    def test_process_message_start(self):
        """Test processing 'start' message"""
        response = self.whatsapp_service.process_message(self.mock_user, "start", None)
        
        assert "AgriConnect WhatsApp Service" in response
        assert "Hello Test Village!" in response

    def test_process_message_option_1_advisory(self):
        """Test processing option 1 (advisory)"""
        response = self.whatsapp_service.process_message(self.mock_user, "1", None)
        
        assert "Crop Advisory Services" in response
        assert "farming information" in response

    def test_process_message_advisory_keyword(self):
        """Test processing advisory keyword"""
        response = self.whatsapp_service.process_message(self.mock_user, "advisory", None)
        
        assert "Crop Advisory Services" in response
        assert "farming information" in response

    def test_process_message_option_2_logistics(self):
        """Test processing option 2 (logistics)"""
        response = self.whatsapp_service.process_message(self.mock_user, "2", None)
        
        assert "Logistics Services" in response
        assert "transport" in response

    def test_process_message_logistics_keyword(self):
        """Test processing logistics keyword"""
        response = self.whatsapp_service.process_message(self.mock_user, "logistics", None)
        
        assert "Logistics Services" in response
        assert "transport" in response

    def test_process_message_option_3_payments(self):
        """Test processing option 3 (payments)"""
        response = self.whatsapp_service.process_message(self.mock_user, "3", None)
        
        assert "Payment Services" in response
        assert "payments" in response

    def test_process_message_payments_keyword(self):
        """Test processing payments keyword"""
        response = self.whatsapp_service.process_message(self.mock_user, "payments", None)
        
        assert "Payment Services" in response
        assert "payments" in response

    def test_process_message_option_4_profile(self):
        """Test processing option 4 (profile)"""
        response = self.whatsapp_service.process_message(self.mock_user, "4", None)
        
        assert "Your Profile Information" in response
        assert self.mock_user.phone_number in response

    def test_process_message_profile_keyword(self):
        """Test processing profile keyword"""
        response = self.whatsapp_service.process_message(self.mock_user, "profile", None)
        
        assert "Your Profile Information" in response
        assert self.mock_user.phone_number in response

    def test_process_message_back_to_main_menu(self):
        """Test processing 'back' to return to main menu"""
        response = self.whatsapp_service.process_message(self.mock_user, "back", None)
        
        assert "AgriConnect WhatsApp Service" in response
        assert "Hello Test Village!" in response

    def test_process_message_unknown(self):
        """Test processing unknown message"""
        response = self.whatsapp_service.process_message(self.mock_user, "unknown message", None)
        
        # The AI agent provides helpful response for unknown messages
        assert "farming assistant" in response.lower()
        assert "advisory" in response.lower()
        assert "logistics" in response.lower()
        assert "payments" in response.lower()

    def test_process_message_with_media(self):
        """Test processing message with media URL"""
        media_url = "https://example.com/image.jpg"
        response = self.whatsapp_service.process_message(self.mock_user, "photo", media_url)
        
        # Should handle the message normally, media URL can be processed separately
        assert isinstance(response, str)

    def test_handle_advisory_request_with_specific_query(self):
        """Test advisory request with specific crop query"""
        with patch.object(self.whatsapp_service.advisory_service, 'get_crop_advice') as mock_advice:
            mock_advice.return_value = "Here's advice for your crop"
            
            response = self.whatsapp_service.handle_advisory_request(self.mock_user, "advisory for maize")
            
            mock_advice.assert_called_once_with("for maize", user=self.mock_user)
            assert "Here's advice for your crop" in response

    def test_handle_logistics_request_with_specific_query(self):
        """Test logistics request with specific query"""
        with patch.object(self.whatsapp_service.logistics_service, 'get_transport_info') as mock_logistics:
            mock_logistics.return_value = "Here's transport info"
            
            response = self.whatsapp_service.handle_logistics_request(self.mock_user, "logistics for 10 bags")
            
            mock_logistics.assert_called_once_with("for 10 bags", user=self.mock_user)
            assert "Here's transport info" in response

    def test_handle_payment_request_with_specific_query(self):
        """Test payment request with specific query"""
        with patch.object(self.whatsapp_service.payment_service, 'get_payment_info') as mock_payment:
            mock_payment.return_value = "Here's payment info"
            
            response = self.whatsapp_service.handle_payment_request(self.mock_user, "payment for delivery")
            
            mock_payment.assert_called_once_with("for delivery", user=self.mock_user)
            assert "Here's payment info" in response

    def test_handle_profile_request(self):
        """Test profile request response"""
        response = self.whatsapp_service.handle_profile_request(self.mock_user, "profile")
        
        assert "Your Profile Information" in response
        assert self.mock_user.phone_number in response
        assert "farmer" in response.lower()  # user type (case-insensitive)

    def test_handle_subscription_request(self):
        """Test subscription request response"""
        response = self.whatsapp_service.handle_subscription_request(self.mock_user, "subscription")
        
        assert "Subscription Plan" in response
        assert "Basic Farmer" in response

    def test_handle_support_request(self):
        """Test support request response"""
        response = self.whatsapp_service.handle_support_request(self.mock_user, "support")
        
        assert "Support Services" in response
        assert "here to help" in response

    def test_handle_unknown_message(self):
        """Test handling unknown messages"""
        # Mock the AI agent to return None so fallback is used
        with patch.object(self.whatsapp_service.ai_agent, 'process_query', return_value=None):
            response = self.whatsapp_service.handle_unknown_message(self.mock_user, "random message")
            
            assert "didn't understand" in response.lower()
            assert "1️⃣ Advisory" in response
            assert "2️⃣ Logistics" in response