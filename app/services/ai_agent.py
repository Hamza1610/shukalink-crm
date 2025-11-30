"""
AI Agent Service for processing user queries
"""
import json
import re
from typing import Optional, Dict, Any, List
from app.models.user import User
from app.services.advisory_service import AdvisoryService
from app.services.logistics_service import LogisticsService
from app.services.payment_service import PaymentService
from app.services.crm_service import CRMService
from app.services.whatsapp_service import WhatsAppService


class AIAgent:
    """
    AI Agent that processes user queries and provides intelligent responses
    """
    
    def __init__(self):
        # Initialize AI model or API client
        self.model = None  # In a real implementation, this would connect to an AI service
        self.advisory_service = AdvisoryService()
        self.logistics_service = LogisticsService()
        self.payment_service = PaymentService()
        self.crm_service = CRMService()
        self.whatsapp_service = WhatsAppService()
        
        # Define available functions that the agent can call
        self.available_functions = {
            "get_crop_advice": self.advisory_service.get_crop_advice,
            "schedule_transport": self.logistics_service.schedule_pickup,
            "get_transport_info": self.logistics_service.get_transport_info,
            "process_payment": self.payment_service.process_payment,
            "get_payment_info": self.payment_service.get_payment_info,
            "send_message": self.whatsapp_service.send_message,
            "send_media_message": self.whatsapp_service.send_media_message,
        }
    
    def process_query(self, query: str, user: Optional[User] = None):
        """
        Process a user query and return an appropriate response
        """
        query_lower = query.lower().strip()
        
        # Try to identify intent and extract parameters from the query
        intent, params = self._extract_intent_and_params(query_lower, user)
        
        # If we can identify a specific intent and have the required services, execute it
        if intent and intent in self.available_functions:
            try:
                # Call the appropriate service function
                result = self.available_functions[intent](**params)
                return result
            except Exception as e:
                # Fallback if the function call fails
                return f"Sorry, I encountered an issue processing your request: {str(e)}. Please try again or reply with 'menu' for options."
        
        # Handle common farming queries
        if any(keyword in query_lower for keyword in ['hello', 'hi', 'hey', 'good morning']):
            return "Hello! I'm your AgriConnect AI assistant. How can I help you with farming today?"
        
        elif any(keyword in query_lower for keyword in ['weather', 'rain', 'temperature', 'climate']):
            return "For accurate weather information for your farming needs, I recommend checking local weather services or using our dedicated weather advisory feature. Would you like me to connect you to crop advisory instead?"
        
        elif any(keyword in query_lower for keyword in ['pest', 'disease', 'infestation', 'sick plants']):
            return "For pest and disease management, our crop advisory service can provide expert guidance. Would you like to connect with our advisory team or learn about common solutions?"
        
        elif any(keyword in query_lower for keyword in ['fertilizer', 'soil', 'nutrition', 'plant food']):
            return "Proper soil nutrition is key to successful farming. Our advisory service can recommend the best fertilizers for your crops. Would you like specific advice for your crops?"
        
        elif any(keyword in query_lower for keyword in ['harvest', 'harvesting', 'collect', 'gather']):
            return "Harvest timing is crucial for crop quality and yield. Would you like advice on the best time to harvest your specific crops?"
        
        elif any(keyword in query_lower for keyword in ['seed', 'planting', 'sow', 'crop']):
            return "Proper seed selection and planting techniques are fundamental. Would you like specific advice on seed varieties or planting methods for your region?"
        
        elif any(keyword in query_lower for keyword in ['price', 'market', 'sell', 'buy', 'cost']):
            return "Market prices fluctuate regularly. Our platform can help you find the best markets for your produce. Would you like to know more about our logistics services to help you reach markets?"
        
        elif any(keyword in query_lower for keyword in ['transport', 'logistics', 'truck', 'delivery']):
            return "Our logistics service can help transport your produce to markets efficiently. Would you like to learn more about our transport options?"
        
        elif any(keyword in query_lower for keyword in ['payment', 'pay', 'money', 'transaction']):
            return "Our payment services facilitate secure transactions for your farming business. Would you like to know more about our payment options?"
        
        else:
            # For queries that don't match common patterns, provide a general response
            return f"I understand you're asking about: '{query}'. As your farming assistant, I can connect you with specific services. Reply with 'advisory' for crop advice, 'logistics' for transport, 'payments' for payment services, or 'menu' to see all options."
    
    def _extract_intent_and_params(self, query: str, user: Optional[User] = None) -> tuple:
        """
        Extract intent and parameters from the query
        """
        query_lower = query.lower().strip()
        
        # Define patterns for different intents
        patterns = {
            "get_crop_advice": [
                r"advice on (.+)",
                r"advisory for (.+)",
                r"information about (.+)",
                r"tips for (.+)",
            ],
            "schedule_transport": [
                r"transport (.+)",
                r"delivery for (.+)",
                r"pickup (.+)",
            ],
            "get_transport_info": [
                r"transport (info|information|rates|cost)",
                r"delivery (info|information|rates|cost)",
                r"how much for transport",
            ],
            "process_payment": [
                r"make payment",
                r"pay for (.+)",
                r"payment for (.+)",
            ],
            "get_payment_info": [
                r"payment (status|info|information)",
                r"check payment",
            ]
        }
        
        for intent, intent_patterns in patterns.items():
            for pattern in intent_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    # Extract the parameter
                    param = match.group(1).strip()
                    
                    # Prepare parameters based on intent
                    if intent == "get_crop_advice":
                        return intent, {"crop_query": param, "user": user}
                    elif intent == "schedule_transport":
                        return intent, {"request_data": {"produce": param}, "user": user}
                    elif intent == "get_transport_info":
                        return intent, {"query": param, "user": user}
                    elif intent == "process_payment":
                        return intent, {"payment_data": {"description": param}, "user": user}
                    elif intent == "get_payment_info":
                        return intent, {"query": param, "user": user}
        
        return None, {}
    
    def call_function(self, function_name: str, **kwargs):
        """
        Call a specific function with the given parameters
        """
        if function_name in self.available_functions:
            try:
                return self.available_functions[function_name](**kwargs)
            except Exception as e:
                return f"Error calling {function_name}: {str(e)}"
        else:
            return f"Function {function_name} not available"