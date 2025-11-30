"""
Main WhatsApp Service that integrates with Twilio
"""
from typing import Optional
from .whatsapp_flow import WhatsAppService as WhatsAppFlowService
from .voice_service import VoiceService


class WhatsAppService:
    """
    Main WhatsApp service class that acts as a wrapper for the flow implementation
    """
    
    def __init__(self):
        # Initialize the flow service
        self.flow_service = WhatsAppFlowService()
        self.voice_service = VoiceService()
    
    def process_message(self, user, message: str, media_url: str = None, media_content_type: str = None):
        """
        Process incoming WhatsApp message (text or voice) and return response
        """
        # If there's a media URL, it might be a voice note
        if media_url and media_content_type:
            if 'audio' in media_content_type.lower() or 'voice' in media_content_type.lower():
                # Transcribe the voice note and process it as text
                import asyncio
                try:
                    # Run the async transcription in a new event loop if needed
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    transcribed_text = loop.run_until_complete(
                        self.voice_service.transcribe_voice_note(media_url)
                    )
                    loop.close()
                    
                    if transcribed_text:
                        # Process the transcribed text through the flow service
                        return self.flow_service.process_message(user, transcribed_text, media_url)
                    else:
                        return "Sorry, I couldn't understand the voice message. Could you please send a text message instead?"
                except Exception as e:
                    print(f"Error processing voice note: {e}")
                    return "Sorry, there was an issue processing your voice message. Please try sending a text message."
        
        # If it's a regular text message, process normally
        return self.flow_service.process_message(user, message, media_url)
    
    def send_message(self, to_number: str, message: str, media_url: str = None):
        """
        Send WhatsApp message using Twilio
        """
        from twilio.rest import Client
        from app.core.config import settings
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        if media_url:
            message = client.messages.create(
                body=message,
                media_url=[media_url],
                from_=f'whatsapp:{settings.TWILIO_PHONE_NUMBER}',
                to=f'whatsapp:{to_number}'
            )
        else:
            message = client.messages.create(
                body=message,
                from_=f'whatsapp:{settings.TWILIO_PHONE_NUMBER}',
                to=f'whatsapp:{to_number}'
            )
        
        return message.sid
    
    def send_media_message(self, to_number: str, message: str, media_url: str):
        """
        Send WhatsApp message with media using Twilio
        """
        from twilio.rest import Client
        from app.core.config import settings
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body=message,
            media_url=[media_url],
            from_=f'whatsapp:{settings.TWILIO_PHONE_NUMBER}',
            to=f'whatsapp:{to_number}'
        )
        
        return message.sid
    
    def send_interactive_message(self, to_number: str, message: str, media_url: str = None):
        """
        Send an interactive message with buttons or quick replies
        """
        # For now, sending a regular message - in a real implementation, 
        # this would use Twilio's interactive message features
        return self.send_message(to_number, message, media_url)
    
    def get_message_status(self, message_sid: str):
        """
        Get the delivery status of a sent message
        """
        from twilio.rest import Client
        from app.core.config import settings
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message = client.messages(message_sid).fetch()
        return {
            "sid": message.sid,
            "status": message.status,
            "to": message.to,
            "from": message.from_,
            "body": message.body,
            "date_sent": message.date_sent,
            "date_updated": message.date_updated
        }