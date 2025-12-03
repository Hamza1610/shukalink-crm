"""
Test script for the multi-agent system
Run this script to test if the agents are working correctly
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.ai_agent import AIAgent
from app.models.user import User
from unittest.mock import Mock

def test_agent():
    print("=" * 60)
    print("Testing ShukaLink Multi-Agent System")
    print("=" * 60)
    
    # Create a mock user
    mock_user = Mock(spec=User)
    mock_user.id = "test_user_123"
    mock_user.phone_number = "+2348012345678"
    mock_user.village = "Test Village"
    mock_user.user_type = "farmer"
    
    # Initialize the AI agent
    print("\n1. Initializing AI Agent...")
    try:
        agent = AIAgent()
        if not agent.graph:
            print("❌ FAILED: Agent graph not initialized. Check GROQ_API_KEY in .env")
            return False
        print("✅ SUCCESS: Agent initialized successfully")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False
    
    # Test queries
    test_queries = [
        ("Advisory Test", "How do I prevent pest damage on my maize crops?"),
        ("Logistics Test", "I need to transport 50 bags of rice to Kano"),
        ("Payment Test", "Check my payment status"),
    ]
    
    for test_name, query in test_queries:
        print(f"\n2. Testing {test_name}...")
        print(f"   Query: '{query}'")
        try:
            response = agent.process_query(query, user=mock_user)
            print(f"   Response: {response[:200]}...")  # First 200 chars
            print("✅ SUCCESS")
        except Exception as e:
            print(f"❌ FAILED: {e}")
            return False
    
    print("\n" + "=" * 60)
    print("All tests passed! ✅")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_agent()
    sys.exit(0 if success else 1)
