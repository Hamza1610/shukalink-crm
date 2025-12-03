"""
Main WhatsApp Service that integrates with Twilio and AI Agent
"""
from typing import Optional
from app.services.ai_agent import AIAgent
from app.services.voice_service import VoiceService


class WhatsAppService:
    """
    Main WhatsApp service that processes messages using AI agent
    """
    
    def __init__(self):
        self.ai_agent = AIAgent()
        self.voice_service = VoiceService()
    
    def process_message(self, user, message: str, media_url: str = None, media_content_type: str = None):
        """
        Process incoming WhatsApp message (text or voice) and return response
        """
        # Handle voice notes
        if media_url and media_content_type:
            if 'audio' in media_content_type.lower() or 'voice' in media_content_type.lower():
                try:
                    # Transcribe using Groq
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    transcribed_text = loop.run_until_complete(
                        self.voice_service.transcribe_voice_note(media_url)
                    )
                    loop.close()
                    
                    if transcribed_text:
                        message = transcribed_text
                    else:
                        return "Sorry, I couldn't understand the voice message. Could you please send a text message instead?"
                except Exception as e:
                    print(f"Error processing voice note: {e}")
                    return "Sorry, there was an issue processing your voice message. Please try sending a text message."
        
        # Simple menu handling
        if message.lower().strip() in ['start', 'menu', 'help']:
            return self._show_menu(user)
        
        # Use AI agent for all other messages
        try:
            response = self.ai_agent.process_query(message, user=user)
            return response if response else "I'm here to help! What would you like to know about farming, logistics, or payments?"
        except Exception as e:
            print(f"Error processing message with AI: {e}")
            return "I encountered an issue processing your request. Please try rephrasing or type 'menu' for options."
    
    def _show_menu(self, user):
        """Show simple welcome menu"""
        menu = f"🌾 *ShukaLink CRM* 🌾\n\n"
        menu += f"Hello {user.village or 'there'}! 👋\n\n"
        menu += "I'm your AI assistant. I can help you with:\n\n"
        menu += "🌱 *Farming Advice* - Crops, pests, soil, fertilizer\n"
        menu += "🚛 *Logistics* - Transport and delivery\n"
        menu += "💳 *Payments* - Transactions and status\n\n"
        menu += "Just ask me anything in plain language!\n\n"
        menu += "_Example: \"How do I treat maize pests?\" or \"I need transport for 50 bags\"_"
        return menu
    
    def send_message(self, to_number: str, message: str, media_url: str = None):
        """
        Send WhatsApp message using Twilio
        """
        from twilio.rest import Client
        from app.core.config import settings
        
        client = Client(settings.WHATSAPP_ACCOUNT_SID, settings.WHATSAPP_AUTH_TOKEN)
        
        if media_url:
            message = client.messages.create(
                body=message,
                media_url=[media_url],
                from_=f'whatsapp:{settings.WHATSAPP_PHONE_NUMBER}',
                to=f'whatsapp:{to_number}'
            )
        else:
            message = client.messages.create(
                body=message,
                from_=f'whatsapp:{settings.WHATSAPP_PHONE_NUMBER}',
                to=f'whatsapp:{to_number}'
            )
        
        return message.sid
    
    def send_media_message(self, to_number: str, message: str, media_url: str):
        """
        Send WhatsApp message with media using Twilio
        """
        return self.send_message(to_number, message, media_url)