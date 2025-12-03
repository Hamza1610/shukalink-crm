from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class VoiceMessageBase(BaseModel):
    user_id: str
    audio_file_url: Optional[str] = None
    audio_duration_seconds: Optional[float] = None
    language_detected: Optional[str] = None
    transcription: Optional[str] = None
    transcription_confidence: Optional[float] = None
    processing_status: str
    identified_intent: Optional[str] = None
    entities_extracted: Optional[Dict[str, Any]] = None
    source: str


class VoiceMessageCreate(VoiceMessageBase):
    pass


class VoiceMessageUpdate(BaseModel):
    audio_file_url: Optional[str] = None
    audio_duration_seconds: Optional[float] = None
    language_detected: Optional[str] = None
    transcription: Optional[str] = None
    transcription_confidence: Optional[float] = None
    processing_status: Optional[str] = None
    identified_intent: Optional[str] = None
    entities_extracted: Optional[Dict[str, Any]] = None
    source: Optional[str] = None


class VoiceMessage(VoiceMessageBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatSessionBase(BaseModel):
    user_id: str
    session_type: str
    context_data: Optional[Dict[str, Any]] = None
    user_message: Optional[str] = None
    ai_response: Optional[str] = None
    ai_voice_response_url: Optional[str] = None
    llm_model_used: Optional[str] = None
    voice_message_id: Optional[str] = None


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionUpdate(BaseModel):
    context_data: Optional[Dict[str, Any]] = None
    user_message: Optional[str] = None
    ai_response: Optional[str] = None
    ai_voice_response_url: Optional[str] = None
    llm_model_used: Optional[str] = None


class ChatSession(ChatSessionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdvisoryRecordBase(BaseModel):
    user_id: str
    advisory_type: str
    crop_type: str
    advice_given: str
    sources_cited: Optional[List[str]] = None
    confidence_level: Optional[float] = None
    environmental_context: Optional[Dict[str, Any]] = None
    storage_context: Optional[Dict[str, Any]] = None
    user_followed_advice: Optional[bool] = None
    reported_outcome: Optional[str] = None
    produce_listing_id: Optional[str] = None


class AdvisoryRecordCreate(AdvisoryRecordBase):
    pass


class AdvisoryRecordUpdate(BaseModel):
    advice_given: Optional[str] = None
    sources_cited: Optional[List[str]] = None
    confidence_level: Optional[float] = None
    environmental_context: Optional[Dict[str, Any]] = None
    storage_context: Optional[Dict[str, Any]] = None
    user_followed_advice: Optional[bool] = None
    reported_outcome: Optional[str] = None


class AdvisoryRecord(AdvisoryRecordBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True