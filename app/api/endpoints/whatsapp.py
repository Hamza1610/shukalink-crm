from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import PlainTextResponse
import hashlib
import hmac
import os
from app.core.config import settings
from app.db.session import SessionLocal
from app.crud.crud_user import crud_user
from app.services.whatsapp_flow import WhatsAppService
from twilio.request_validator import RequestValidator
from twilio.rest import Client
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_twilio_response(message: str):
    """Create TwiML response for WhatsApp"""
    root = Element("Response")
    message_elem = SubElement(root, "Message")
    message_elem.text = message
    
    rough_string = tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return PlainTextResponse(
        content=reparsed.toprettyxml(indent="  ")[23:],  # Remove XML declaration
        media_type="text/xml"
    )

@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    WhatsApp webhook handler (public endpoint)
    Receives messages from Twilio WhatsApp API
    """
    form_data = await request.form()
    
    # Extract message data
    from_number = form_data.get("From", "").replace("whatsapp:", "")
    body = form_data.get("Body", "")
    profile_name = form_data.get("ProfileName", "")
    media_url = form_data.get("MediaUrl0", "")
    
    # Verify Twilio signature (in production)
    # For now, we'll skip this for development
    # validator = RequestValidator(settings.WHATSAPP_AUTH_TOKEN)
    # signature = request.headers.get("X-Twilio-Signature", "")
    # uri = str(request.url)
    # if not validator.validate(uri, form_data, signature):
    #     raise HTTPException(status_code=400, detail="Invalid Twilio signature")
    
    # Get or create user
    db = next(get_db())
    try:
        user = crud_user.get_by_phone(db, phone_number=from_number)
        if not user:
            # Create new user
            user_data = {
                "phone_number": from_number,
                "whatsapp_id": form_data.get("From", ""),
                "user_type": "farmer"  # Default to farmer
            }
            if profile_name:
                user_data["village"] = profile_name  # Using village field for name temporarily
            user = crud_user.create(db, obj_in=user_data)
        
        # Process the message with WhatsApp service
        whatsapp_service = WhatsAppService()
        response_message = whatsapp_service.process_message(user, body, media_url)
        
        return create_twilio_response(response_message)
    finally:
        db.close()

@router.get("/webhook")
async def verify_webhook():
    """
    Verify webhook setup (for Twilio verification)
    """
    return {"status": "whatsapp webhook active"}