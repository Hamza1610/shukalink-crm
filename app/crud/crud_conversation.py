# app/crud/crud_conversation.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.conversation import VoiceMessage, ChatSession, AdvisoryRecord
from app.schemas.conversation import VoiceMessageCreate, VoiceMessageUpdate, ChatSessionCreate, ChatSessionUpdate, AdvisoryRecordCreate, AdvisoryRecordUpdate


def create_voice_message(db: Session, voice_message: VoiceMessageCreate, user_id: str) -> VoiceMessage:
    """Create a new voice message."""
    db_voice_message = VoiceMessage(
        user_id=user_id,
        audio_file_url=voice_message.audio_file_url,
        audio_duration_seconds=voice_message.audio_duration_seconds,
        language_detected=voice_message.language_detected,
        transcription=voice_message.transcription,
        transcription_confidence=voice_message.transcription_confidence,
        processing_status=voice_message.processing_status,
        identified_intent=voice_message.identified_intent,
        entities_extracted=voice_message.entities_extracted,
        source=voice_message.source
    )
    db.add(db_voice_message)
    db.commit()
    db.refresh(db_voice_message)
    return db_voice_message


def get_voice_message(db: Session, voice_message_id: str) -> Optional[VoiceMessage]:
    """Get a voice message by ID."""
    return db.query(VoiceMessage).filter(VoiceMessage.id == voice_message_id).first()


def get_voice_messages(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[str] = None) -> List[VoiceMessage]:
    """Get a list of voice messages."""
    query = db.query(VoiceMessage)
    if user_id:
        query = query.filter(VoiceMessage.user_id == user_id)
    return query.offset(skip).limit(limit).all()


def update_voice_message(db: Session, voice_message_id: str, voice_message_update: VoiceMessageUpdate) -> Optional[VoiceMessage]:
    """Update a voice message."""
    db_voice_message = get_voice_message(db, voice_message_id)
    if db_voice_message:
        update_data = voice_message_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_voice_message, field, value)
        db.commit()
        db.refresh(db_voice_message)
    return db_voice_message


def delete_voice_message(db: Session, voice_message_id: str) -> bool:
    """Delete a voice message."""
    db_voice_message = get_voice_message(db, voice_message_id)
    if db_voice_message:
        db.delete(db_voice_message)
        db.commit()
        return True
    return False


def create_chat_session(db: Session, chat_session: ChatSessionCreate, user_id: str, voice_message_id: Optional[str] = None) -> ChatSession:
    """Create a new chat session."""
    db_chat_session = ChatSession(
        user_id=user_id,
        voice_message_id=voice_message_id,
        session_type=chat_session.session_type,
        context_data=chat_session.context_data,
        user_message=chat_session.user_message,
        ai_response=chat_session.ai_response,
        ai_voice_response_url=chat_session.ai_voice_response_url,
        llm_model_used=chat_session.llm_model_used
    )
    db.add(db_chat_session)
    db.commit()
    db.refresh(db_chat_session)
    return db_chat_session


def get_chat_session(db: Session, chat_session_id: str) -> Optional[ChatSession]:
    """Get a chat session by ID."""
    return db.query(ChatSession).filter(ChatSession.id == chat_session_id).first()


def get_chat_sessions(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[str] = None) -> List[ChatSession]:
    """Get a list of chat sessions."""
    query = db.query(ChatSession)
    if user_id:
        query = query.filter(ChatSession.user_id == user_id)
    return query.offset(skip).limit(limit).all()


def update_chat_session(db: Session, chat_session_id: str, chat_session_update: ChatSessionUpdate) -> Optional[ChatSession]:
    """Update a chat session."""
    db_chat_session = get_chat_session(db, chat_session_id)
    if db_chat_session:
        update_data = chat_session_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_chat_session, field, value)
        db.commit()
        db.refresh(db_chat_session)
    return db_chat_session


def delete_chat_session(db: Session, chat_session_id: str) -> bool:
    """Delete a chat session."""
    db_chat_session = get_chat_session(db, chat_session_id)
    if db_chat_session:
        db.delete(db_chat_session)
        db.commit()
        return True
    return False


def create_advisory_record(db: Session, advisory_record: AdvisoryRecordCreate, user_id: str, produce_listing_id: Optional[str] = None) -> AdvisoryRecord:
    """Create a new advisory record."""
    db_advisory_record = AdvisoryRecord(
        user_id=user_id,
        produce_listing_id=produce_listing_id,
        advisory_type=advisory_record.advisory_type,
        crop_type=advisory_record.crop_type,
        advice_given=advisory_record.advice_given,
        sources_cited=advisory_record.sources_cited,
        confidence_level=advisory_record.confidence_level,
        environmental_context=advisory_record.environmental_context,
        storage_context=advisory_record.storage_context,
        user_followed_advice=advisory_record.user_followed_advice,
        reported_outcome=advisory_record.reported_outcome
    )
    db.add(db_advisory_record)
    db.commit()
    db.refresh(db_advisory_record)
    return db_advisory_record


def get_advisory_record(db: Session, advisory_record_id: str) -> Optional[AdvisoryRecord]:
    """Get an advisory record by ID."""
    return db.query(AdvisoryRecord).filter(AdvisoryRecord.id == advisory_record_id).first()


def get_advisory_records(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[str] = None) -> List[AdvisoryRecord]:
    """Get a list of advisory records."""
    query = db.query(AdvisoryRecord)
    if user_id:
        query = query.filter(AdvisoryRecord.user_id == user_id)
    return query.offset(skip).limit(limit).all()


def update_advisory_record(db: Session, advisory_record_id: str, advisory_record_update: AdvisoryRecordUpdate) -> Optional[AdvisoryRecord]:
    """Update an advisory record."""
    db_advisory_record = get_advisory_record(db, advisory_record_id)
    if db_advisory_record:
        update_data = advisory_record_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_advisory_record, field, value)
        db.commit()
        db.refresh(db_advisory_record)
    return db_advisory_record


def delete_advisory_record(db: Session, advisory_record_id: str) -> bool:
    """Delete an advisory record."""
    db_advisory_record = get_advisory_record(db, advisory_record_id)
    if db_advisory_record:
        db.delete(db_advisory_record)
        db.commit()
        return True
    return False