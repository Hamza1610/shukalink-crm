"""
Simplified WhatsApp Flow - AI-First Approach
Uses AI agent for all interactions, with minimal hardcoded logic
"""
from typing import Optional
from app.models.user import User
from app.services.ai_agent import AIAgent
from app.models.conversation import ChatSession
from app.db.session import SessionLocal


class WhatsAppService:
    """
    Minimal WhatsApp service that delegates to AI agent
    This is kept for backward compatibility and conversation tracking
    """
    
    def __init__(self):
        self.ai_agent = AIAgent()

    def process_message(self, user: User, message: str, media_url: Optional[str] = None, media_content_type: Optional[str] = None):
        """
        Process incoming WhatsApp messages using AI agent
        """
        message = message.strip()
        
        # Only handle explicit menu requests
        if message.lower() in ['start', 'menu', 'help']:
            return self.show_main_menu(user)
        
        # Everything else goes to AI agent
        ai_response = self.ai_agent.process_query(message, user=user)
        
        # Save conversation to database
        self._save_conversation_to_db(user, message, ai_response, media_url)
        
        # Return AI response with helpful hint
        if ai_response:
            return f"{ai_response}\n\n_Type 'menu' anytime for options_"
        else:
            return "I'm here to help with farming, logistics, and payments. What would you like to know?"

    def _save_conversation_to_db(self, user: User, user_message: str, ai_response: str, media_url: str = None):
        """
        Save conversation to database for context tracking
        """
        db = SessionLocal()
        try:
            chat_session = ChatSession(
                user_id=user.id,
                session_type="ai_conversation",
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
        Show simple welcome menu
        """
        menu = f"🌾 *ShukaLink CRM* 🌾\n\n"
        menu += f"Hello {user.village or 'there'}! 👋\n\n"
        menu += "I'm your AI farming assistant powered by advanced AI. I can help you with:\n\n"
        menu += "🌱 *Farming Advice*\n"
        menu += "   • Crop management\n"
        menu += "   • Pest control\n"
        menu += "   • Soil preparation\n"
        menu += "   • Harvesting tips\n\n"
        menu += "🚛 *Logistics*\n"
        menu += "   • Transport booking\n"
        menu += "   • Delivery tracking\n"
        menu += "   • Rate inquiries\n\n"
        menu += "💳 *Payments*\n"
        menu += "   • Payment processing\n"
        menu += "   • Transaction status\n"
        menu += "   • Payment history\n\n"
        menu += "*Just ask me anything in plain language!*\n\n"
        menu += "📝 *Examples:*\n"
        menu += "_\"How do I treat maize pests?\"_\n"
        menu += "_\"I need transport for 50 bags to Kano\"_\n"
        menu += "_\"Check my payment status\"_"
        
        return menu