# app/models/conversation.py
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Integer, Float, JSON, Boolean, ARRAY
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from enum import Enum as PyEnum

class MessageSource(PyEnum):
    WHATSAPP = "whatsapp"
    VOICE_CALL = "voice_call"
    SMS = "sms"
    IN_APP = "in_app"

class MessageType(PyEnum):
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    LOCATION = "location"
    PAYMENT_LINK = "payment_link"
    LOGISTICS_UPDATE = "logistics_update"

class IntentCategory(PyEnum):
    LIST_PRODUCE = "list_produce"
    SEARCH_BUYERS = "search_buyers"
    PRICE_INQUIRY = "price_inquiry"
    STORAGE_ADVICE = "storage_advice"
    PEST_CONTROL = "pest_control"
    LOGISTICS_REQUEST = "logistics_request"
    PAYMENT_COORDINATION = "payment_coordination"
    GENERAL_INQUIRY = "general_inquiry"
    UNKNOWN = "unknown"

class CropType(PyEnum):
    TOMATOES = "tomatoes"
    ONIONS = "onions"
    PEPPERS = "peppers"
    YAMS = "yams"
    MAIZE = "maize"
    RICE = "rice"
    # Add more as needed for MVP
    
class VoiceMessage(Base):
    __tablename__ = "voice_messages"

    id = Column(String, primary_key=True, default=lambda: f"voice_{uuid4().hex[:8]}")
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Voice data
    audio_file_url = Column(String, nullable=False)  # S3/Cloudflare R2 URL
    audio_duration_seconds = Column(Float, nullable=False)
    language_detected = Column(Enum("english", "hausa", "pidgin", "mixed", name="language_detected_enum"), default="hausa")
    
    # Processing status
    transcription = Column(Text, nullable=True)  # Transcribed text
    transcription_confidence = Column(Float, nullable=True)  # 0.0-1.0
    processing_status = Column(Enum("pending", "processing", "completed", "failed", name="processing_status_enum"), default="pending")
    processed_at = Column(DateTime, nullable=True)
    
    # AI context
    identified_intent = Column(Enum(IntentCategory, name="identified_intent_enum"), default=IntentCategory.UNKNOWN)
    entities_extracted = Column(JSON, nullable=True)  # {"crop_type": "tomatoes", "quantity": "50kg"}
    
    # Metadata
    source = Column(Enum(MessageSource, name="source_enum"), default=MessageSource.WHATSAPP)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="voice_messages")
    chat_sessions = relationship("ChatSession", back_populates="voice_message")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=lambda: f"chat_{uuid4().hex[:8]}")
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    voice_message_id = Column(String, ForeignKey("voice_messages.id"), nullable=True)
    
    # Session context
    session_type = Column(Enum("listing_creation", "buyer_search", "advisory", "payment", "logistics", name="session_type_enum"), default="general_inquiry")
    context_data = Column(JSON, nullable=True)  # Current state of multi-step conversation
    
    # Messages in session
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    ai_voice_response_url = Column(String, nullable=True)  # TTS audio URL
    
    # Processing details
    llm_model_used = Column(String, default="llama3-8b-agriculture")
    processing_time_ms = Column(Integer, nullable=True)
    
    # Status tracking
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    voice_message = relationship("VoiceMessage", back_populates="chat_sessions")

# app/models/conversation.py (continued)

class AdvisoryType(PyEnum):
    STORAGE = "storage"
    PEST_CONTROL = "pest_control"
    MARKET_TIMING = "market_timing"
    PRICE_ALERT = "price_alert"
    WEATHER_ALERT = "weather_alert"

class AdvisoryRecord(Base):
    __tablename__ = "advisory_records"

    id = Column(String, primary_key=True, default=lambda: f"adv_{uuid4().hex[:8]}")
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    produce_listing_id = Column(String, ForeignKey("produce_listings.id"), nullable=True)
    
    # Advisory type
    advisory_type = Column(Enum(AdvisoryType, name="advisory_type_enum"), nullable=False)
    crop_type = Column(Enum(CropType, name="crop_type_enum"), nullable=True)
    
    # Content
    advice_given = Column(Text, nullable=False)
    sources_cited = Column(ARRAY(String), nullable=True)  # ["Kano State Agricultural Extension Service"]
    confidence_level = Column(Float, nullable=True)  # 0.0-1.0
    
    # Context
    environmental_context = Column(JSON, nullable=True)  # {"temperature": 32, "humidity": 65, "season": "dry"}
    storage_context = Column(String, nullable=True)  # "mud_silo", "plastic_bins"
    
    # Effectiveness tracking
    user_followed_advice = Column(Boolean, nullable=True)
    reported_outcome = Column(String, nullable=True)  # "reduced_spoilage", "no_improvement", "worse"
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    produce_listing = relationship("ProduceListing")