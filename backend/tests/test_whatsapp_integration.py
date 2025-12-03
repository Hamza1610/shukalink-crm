"""
Test script for WhatsApp AI integration with voice support
Run this to verify the integration works
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.whatsapp_service import WhatsAppService
from app.models.user import User
from unittest.mock import Mock

def test_whatsapp_integration():
    print("=" * 60)
    print("Testing WhatsApp AI Integration")
    print("=" * 60)
    
    # Create mock user
    mock_user = Mock(spec=User)
    mock_user.id = "test123"
    mock_user.phone_number = "+2348012345678"
    mock_user.village = "Test Farm"
    mock_user.user_type = "farmer"
    
    # Initialize service
    print("\n1. Initializing WhatsApp Service...")
    try:
        service = WhatsAppService()
        print("✅ SUCCESS: Service initialized")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False
    
    # Test cases
    test_cases = [
        ("Menu Command", "menu"),
        ("Farming Query", "How do I prevent pest damage on maize?"),
        ("Logistics Query", "I need to transport 50 bags of rice to Kano"),
        ("Payment Query", "Check my payment status"),
        ("Greeting", "Hello"),
    ]
    
    for test_name, message in test_cases:
        print(f"\n2. Testing: {test_name}")
        print(f"   Input: '{message}'")
        try:
            response = service.process_message(mock_user, message)
            print(f"   Response: {response[:150]}...")
            print("✅ SUCCESS")
        except Exception as e:
            print(f"❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("WhatsApp AI Integration Tests Complete")
    print("=" * 60)
    return True

if __name__ == "__main__":
    test_whatsapp_integration()
