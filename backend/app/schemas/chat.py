"""
Pydantic schemas for chat API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    """Types of messages in the chat system"""
    TEXT_MESSAGE = "text_message"
    VOICE_MESSAGE = "voice_message"
    AI_MESSAGE = "ai_message"
    TYPING = "typing"
    SESSION_CREATED = "session_created"
    ERROR = "error"


class ChatMessageRequest(BaseModel):
    """Request schema for sending a chat message"""
    type: MessageType = MessageType.TEXT_MESSAGE
    content: str = Field(..., min_length=1, max_length=5000)
    session_id: Optional[str] = None  # Required for all messages except first


class VoiceUploadRequest(BaseModel):
    """Metadata for voice note upload"""
    session_id: Optional[str] = None
    duration_seconds: float = Field(..., gt=0, le=300)  # Max 5 minutes


class ChatMessageResponse(BaseModel):
    """Response schema for chat messages"""
    type: MessageType
    content: str
    session_id: str
    tts_audio_url: Optional[str] = None
    language: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionCreatedResponse(BaseModel):
    """Response when a new chat session is created"""
    type: MessageType = MessageType.SESSION_CREATED
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TypingIndicator(BaseModel):
    """Typing indicator message"""
    type: MessageType = MessageType.TYPING
    status: bool  # True = typing, False = stopped
    session_id: str


class ChatHistoryResponse(BaseModel):
    """Response for chat history request"""
    session_id: str
    messages: List[dict]  # List of message objects
    total_messages: int
    created_at: datetime
    last_activity: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChatSessionSummary(BaseModel):
    """Summary of a chat session"""
    session_id: str
    created_at: datetime
    last_activity: datetime
    message_count: int
    language_used: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    """Error response for chat operations"""
    type: MessageType = MessageType.ERROR
    error: str
    details: Optional[str] = None
    session_id: Optional[str] = None
