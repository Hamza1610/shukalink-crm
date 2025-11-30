from pydantic import BaseModel
from typing import Optional, List


class WhatsAppWebhookRequest(BaseModel):
    """
    Schema for incoming WhatsApp webhook requests from Twilio
    """
    From: str  # WhatsApp number of sender in format: whatsapp:+1234567890
    To: str    # WhatsApp number of recipient in format: whatsapp:+1234567890
    Body: str  # The actual message text
    MessageSid: str  # Twilio's unique identifier for the message
    AccountSid: str  # Twilio account identifier
    FromCity: Optional[str] = None  # City of sender (if available)
    FromCountry: Optional[str] = None  # Country of sender (if available)
    FromState: Optional[str] = None  # State of sender (if available)
    FromZip: Optional[str] = None  # Zip code of sender (if available)
    NumMedia: Optional[str] = "0"  # Number of media files attached
    ProfileName: Optional[str] = None  # Profile name of sender
    SmsMessageSid: Optional[str] = None  # SMS message SID if applicable
    NumSegments: Optional[str] = "1"  # Number of segments in the message
    
    # Media related fields (if any media is attached)
    MediaUrl0: Optional[str] = None  # URL of first media item
    MediaContentType0: Optional[str] = None  # Content type of first media item
    MediaUrl1: Optional[str] = None  # URL of second media item (if any)
    MediaContentType1: Optional[str] = None  # Content type of second media item (if any)


class WhatsAppWebhookResponse(BaseModel):
    """
    Schema for outgoing WhatsApp responses to Twilio
    """
    message: str
    success: bool = True
    message_sid: Optional[str] = None


class WhatsAppMessageRequest(BaseModel):
    """
    Schema for sending WhatsApp messages via API
    """
    to: str  # Recipient phone number in format: +1234567890
    message: str  # Message text to send
    media_url: Optional[str] = None  # Optional media URL to send with message


class WhatsAppConversationState(BaseModel):
    """
    Schema for tracking WhatsApp conversation state
    """
    user_id: str
    state: str  # Current conversation state
    context: Optional[dict] = {}  # Additional context data
    last_message: Optional[str] = None
    last_interaction: Optional[str] = None