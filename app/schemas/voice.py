from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class VoiceTranscriptionRequest(BaseModel):
    """
    Schema for requesting voice transcription
    """
    audio_url: str
    language: Optional[str] = "en"
    user_id: Optional[str] = None


class VoiceTranscriptionResponse(BaseModel):
    """
    Schema for voice transcription response
    """
    transcription: Optional[str] = None
    success: bool
    error_message: Optional[str] = None
    confidence: Optional[float] = None


class TextToSpeechRequest(BaseModel):
    """
    Schema for requesting text-to-speech conversion
    """
    text: str
    voice: Optional[str] = "alloy"  # Default voice
    language: Optional[str] = "en"


class TextToSpeechResponse(BaseModel):
    """
    Schema for text-to-speech response
    """
    audio_url: Optional[str] = None
    success: bool
    error_message: Optional[str] = None


class VoiceMessageResponse(BaseModel):
    """
    Schema for voice message response
    """
    id: str
    user_id: str
    audio_file_url: Optional[str] = None
    transcription: Optional[str] = None
    processing_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True