"""
WhatsApp Service Flow Implementation using Twilio
"""
from typing import Optional
from app.models.user import User
from app.services.ai_agent import AIAgent
from app.services.advisory_service import AdvisoryService
from app.services.logistics_service import LogisticsService
from app.services.payment_service import PaymentService
from app.services.crm_service import CRMService
from app.models.conversation import ChatSession
from app.db.session import SessionLocal


class WhatsAppService:
    """
    WhatsApp service that handles the complete flow of user interactions
    """
    
    def __init__(self):
        self.ai_agent = AIAgent()
        self.advisory_service = AdvisoryService()
        self.logistics_service = LogisticsService()
        self.payment_service = PaymentService()
        self.crm_service = CRMService()
        
        # Define the conversation states
        self.conversation_states = {
            'MAIN_MENU': 0,
            'ADVISORY': 1,
            'LOGISTICS': 2,
            'PAYMENTS': 3,
            'PROFILE': 4,
            'SUBSCRIPTION': 5,
            'SUPPORT': 6,
        }

    def process_message(self, user: User, message: str, media_url: Optional[str] = None, media_content_type: Optional[str] = None):
        """
        Main method to process incoming WhatsApp messages and return appropriate response
        """
        message = message.strip().lower()
        
        # Get user's current state from database or set to default
        current_state = getattr(user, 'conversation_state', self.conversation_states['MAIN_MENU'])
        
        # Process different types of messages
        if message in ['hi', 'hello', 'start', 'help', 'menu']:
            return self.show_main_menu(user)
        
        elif message in ['1', 'advisory', 'crop advisory', 'advice']:
            return self.handle_advisory_request(user, message)
        
        elif message in ['2', 'logistics', 'transport', 'delivery']:
            return self.handle_logistics_request(user, message)
        
        elif message in ['3', 'payments', 'payment', 'pay']:
            return self.handle_payment_request(user, message)
        
        elif message in ['4', 'profile', 'my profile', 'info']:
            return self.handle_profile_request(user, message)
        
        elif message in ['5', 'subscription', 'subscribe', 'plan']:
            return self.handle_subscription_request(user, message)
        
        elif message in ['6', 'support', 'help', 'contact']:
            return self.handle_support_request(user, message)
        
        elif message in ['0', 'main', 'main menu', 'back']:
            return self.show_main_menu(user)
        
        else:
            # Default: use AI agent to handle the query with context
            ai_response = self.ai_agent.process_query(message, user=user)
            
            # Save the conversation to database
            self._save_conversation_to_db(user, message, ai_response, media_url)
            
            return ai_response if ai_response else self.handle_unknown_message(user, message)

    def _save_conversation_to_db(self, user: User, user_message: str, ai_response: str, media_url: str = None):
        """
        Save the conversation to database for context tracking
        """
        db = SessionLocal()
        try:
            chat_session = ChatSession(
                user_id=user.id,
                session_type="general_inquiry",
                context_data={
                    "last_user_message": user_message,
                    "last_ai_response": ai_response,
                    "media_url": media_url
                },
                user_message=user_message,
                ai_response=ai_response
            )
            db.add(chat_session)
            db.commit()
        except Exception as e:
            print(f"Error saving conversation to DB: {e}")
        finally:
            db.close()

    def show_main_menu(self, user: User) -> str:
        """
        Show the main menu options
        """
        welcome_message = f"🌾 AgriConnect WhatsApp Service 🌾\n\n"
        welcome_message += f"Hello {user.village or user.phone_number}!\n\n"
        welcome_message += "How can I help you today?\n\n"
        welcome_message += "Choose an option by typing the number or keyword:\n\n"
        welcome_message += "1️⃣ *Crop Advisory* - Get farming advice and tips\n"
        welcome_message += "2️⃣ *Logistics* - Transport and delivery services\n"
        welcome_message += "3️⃣ *Payments* - Payment processing and tracking\n"
        welcome_message += "4️⃣ *My Profile* - View/update your profile\n"
        welcome_message += "5️⃣ *Subscription* - Manage your plan\n"
        welcome_message += "6️⃣ *Support* - Contact our support team\n\n"
        welcome_message += "_Reply with the option number or keyword (e.g., '1' or 'advisory')_"
        
        return welcome_message

    def handle_advisory_request(self, user: User, message: str) -> str:
        """
        Handle crop advisory requests
        """
        # If the message contains specific crop query, process it directly
        if len(message) > 1 and not message.isdigit():  # Not just '1'
            crop_query = message.replace('advisory', '').replace('crop', '').strip()
            if crop_query:
                return self.advisory_service.get_crop_advice(crop_query, user=user)
        
        # Otherwise, show advisory submenu
        advisory_menu = "🌱 *Crop Advisory Services*\n\n"
        advisory_menu += "What farming information do you need?\n\n"
        advisory_menu += "• _Send a photo of your crops for diagnosis_\n"
        advisory_menu += "• _Ask about specific crops (e.g., maize, rice, cassava)_\n"
        advisory_menu += "• _Ask about pest control_\n"
        advisory_menu += "• _Ask about soil preparation_\n"
        advisory_menu += "• _Ask about harvesting_\n\n"
        advisory_menu += "*Examples:*\n"
        advisory_menu += "_my maize leaves are yellowing_\n"
        advisory_menu += "_how to prepare soil for rice_\n"
        advisory_menu += "_pest control for cassava_\n\n"
        advisory_menu += "Reply with your question or 'back' to return to main menu"
        
        return advisory_menu

    def handle_logistics_request(self, user: User, message: str) -> str:
        """
        Handle logistics requests
        """
        if len(message) > 1 and not message.isdigit():  # Not just '2'
            logistics_query = message.replace('logistics', '').replace('transport', '').strip()
            if logistics_query:
                return self.logistics_service.get_transport_info(logistics_query, user=user)
        
        logistics_menu = "🚛 *Logistics Services*\n\n"
        logistics_menu += "How can we help with logistics?\n\n"
        logistics_menu += "• _Book transport for your produce_\n"
        logistics_menu += "• _Track delivery status_\n"
        logistics_menu += "• _Get transport rates_\n"
        logistics_menu += "• _Schedule pickup_\n\n"
        logistics_menu += "*Examples:*\n"
        logistics_menu += "_I need transport for 10 bags of maize_\n"
        logistics_menu += "_track my delivery_\n"
        logistics_menu += "_transport rates to Kano_\n\n"
        logistics_menu += "Reply with your request or 'back' to return to main menu"
        
        return logistics_menu

    def handle_payment_request(self, user: User, message: str) -> str:
        """
        Handle payment requests
        """
        if len(message) > 1 and not message.isdigit():  # Not just '3'
            payment_query = message.replace('payments', '').replace('payment', '').replace('pay', '').strip()
            if payment_query:
                return self.payment_service.get_payment_info(payment_query, user=user)
        
        payment_menu = "💳 *Payment Services*\n\n"
        payment_menu += "How can we help with payments?\n\n"
        payment_menu += "• _Check payment status_\n"
        payment_menu += "• _Make a payment_\n"
        payment_menu += "• _View payment history_\n"
        payment_menu += "• _Get payment receipts_\n\n"
        payment_menu += "*Examples:*\n"
        payment_menu += "_check payment status_\n"
        payment_menu += "_make payment for delivery_\n"
        payment_menu += "_show my payment history_\n\n"
        payment_menu += "Reply with your request or 'back' to return to main menu"
        
        return payment_menu

    def handle_profile_request(self, user: User, message: str) -> str:
        """
        Handle profile-related requests
        """
        profile_info = "👤 *Your Profile Information*\n\n"
        profile_info += f"*Phone:* {user.phone_number}\n"
        profile_info += f"*Name:* {user.village or 'Not set'}\n"  # Using village field temporarily
        profile_info += f"*User Type:* {user.user_type or 'Farmer'}\n"
        profile_info += f"*Registration Date:* {user.created_at.strftime('%Y-%m-%d') if user.created_at else 'Unknown'}\n\n"
        profile_info += "To update your profile, please contact our support team or visit our web portal.\n\n"
        profile_info += "Reply 'back' to return to main menu"
        
        return profile_info

    def handle_subscription_request(self, user: User, message: str) -> str:
        """
        Handle subscription requests
        """
        subscription_info = "📊 *Subscription Plan*\n\n"
        subscription_info += "Current Plan: *Basic Farmer*\n\n"
        subscription_info += "*Features:*\n"
        subscription_info += "• Basic crop advisory\n"
        subscription_info += "• Standard logistics support\n"
        subscription_info += "• Payment processing\n\n"
        subscription_info += "To upgrade to Premium plan with additional features, contact our sales team.\n\n"
        subscription_info += "Reply 'back' to return to main menu"
        
        return subscription_info

    def handle_support_request(self, user: User, message: str) -> str:
        """
        Handle support requests
        """
        support_info = "🆘 *Support Services*\n\n"
        support_info += "We're here to help!\n\n"
        support_info += "*Contact Options:*\n"
        support_info += "• Reply with your question directly\n"
        support_info += "• Call our support hotline: +234-XXX-XXXX\n"
        support_info += "• Email: support@agriconnect.ng\n\n"
        support_info += "For immediate assistance, describe your issue below.\n\n"
        support_info += "Reply 'back' to return to main menu"
        
        return support_info

    def handle_unknown_message(self, user: User, message: str) -> str:
        """
        Handle messages that don't match specific commands
        """
        # Try to process with AI agent
        ai_response = self.ai_agent.process_query(message, user=user)
        if ai_response:
            ai_response += "\n\nReply 'menu' to see main options"
            return ai_response
        
        # If AI can't handle, provide helpful response
        fallback_message = "I didn't understand that message. Here are the main options:\n\n"
        fallback_message += "1️⃣ Advisory - Get farming advice\n"
        fallback_message += "2️⃣ Logistics - Transport services\n"
        fallback_message += "3️⃣ Payments - Payment processing\n"
        fallback_message += "4️⃣ Profile - View your profile\n"
        fallback_message += "5️⃣ Subscription - Manage plan\n"
        fallback_message += "6️⃣ Support - Contact support\n\n"
        fallback_message += "Reply with 'menu' to see all options"
        
        return fallback_message