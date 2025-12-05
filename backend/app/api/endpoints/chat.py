"""
Chat endpoint for WebSocket and REST-based chat functionality
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import logging
import json
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.conversation import ChatSession, VoiceMessage, MessageSource, MessageType as DBMessageType
from app.schemas.chat import (
    ChatMessageRequest, ChatMessageResponse, SessionCreatedResponse,
    ErrorResponse, ChatHistoryResponse, ChatSessionSummary, MessageType
)
from app.services.websocket_manager import manager
from app.services.ai_agent import AIAgent
from app.services.voice_service import VoiceService
from app.core.security import verify_token
from uuid import uuid4

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
ai_agent = AIAgent()
voice_service = VoiceService()


async def authenticate_websocket_user(token: str, db: Session) -> Optional[User]:
    """Authenticate WebSocket user from JWT token (call after accept)"""
    try:
        payload = verify_token(token)
        if not payload:
            return None
            
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        from app.crud.crud_user import get_user
        user = get_user(db, user_id)
        return user
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        return None


@router.websocket("/ws/chat/{user_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: str
):
    """
    WebSocket endpoint for real-time chat
    Connect: ws://localhost:8000/api/v1/chat/ws/chat/{user_id}?token={jwt_token}
    """
    logger.info(f"[WS] New connection attempt for user {user_id}")
    
    # MUST accept WebSocket connection FIRST before any other operations
    await websocket.accept()
    logger.info(f"[WS] WebSocket accepted")
    
    # Create database session manually (not using Depends)
    from app.db.session import SessionLocal
    db = SessionLocal()
    
    try:
        logger.info(f"[WS] Authenticating user {user_id}")
        # Authenticate user
        user = await authenticate_websocket_user(token, db)
        if not user:
            logger.error(f"[WS] Authentication failed - user is None")
            await websocket.close(code=1008, reason="Authentication failed")
            return
        if user.id != user_id:
            logger.error(f"[WS] User ID mismatch: {user.id} != {user_id}")
            await websocket.close(code=1008, reason="User ID mismatch")
            return
        
        logger.info(f"[WS] Authentication successful for {user_id}")
        
        # Register connection in manager
        await manager.connect(websocket, user_id)
        logger.info(f"[WS] WebSocket connected for user {user_id}")
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                logger.debug(f"Received from {user_id}: {data}")
                
                try:
                    message_data = json.loads(data)
                    message_type = message_data.get("type")
                    
                    if message_type == "text_message":
                        await handle_text_message(websocket, user, message_data, db)
                    elif message_type == "typing":
                        # Just echo typing indicator (could broadcast to other users in future)
                        pass
                    else:
                        await manager.send_personal_message({
                            "type": "error",
                            "error": f"Unknown message type: {message_type}"
                        }, user_id)
                        
                except json.JSONDecodeError:
                    await manager.send_personal_message({
                        "type": "error",
                        "error": "Invalid JSON format"
                    }, user_id)
                except Exception as e:
                    logger.error(f"Error processing message from {user_id}: {e}", exc_info=True)
                    await manager.send_personal_message({
                        "type": "error",
                        "error": "Internal server error",
                        "details": str(e)
                    }, user_id)
                    
        except WebSocketDisconnect:
            logger.info(f"[WS] Client disconnected: {user_id}")
            manager.disconnect(user_id)
        except Exception as e:
            logger.error(f"[WS] Error in message loop for {user_id}: {e}", exc_info=True)
            manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"[WS] Fatal error for {user_id}: {e}", exc_info=True)
    finally:
        # Close database session when WebSocket closes
        logger.info(f"[WS] Closing connection and DB session for {user_id}")
        db.close()




def get_conversation_history(session: ChatSession, limit: int = 20) -> list:
    """Extract conversation history from session's context_data"""
    if not session.context_data:
        return []
    
    messages = session.context_data.get("messages", [])
    # Return last 'limit' messages
    return messages[-limit:] if len(messages) > limit else messages


async def handle_text_message(websocket: WebSocket, user: User, message_data: dict, db: Session):
    """Handle incoming text message and send AI response"""
    content = message_data.get("content", "").strip()
    session_id = message_data.get("session_id")
    
    if not content:
        await manager.send_personal_message({
            "type": "error",
            "error": "Message content cannot be empty"
        }, user.id)
        return
    
    # Check if session_id is required (not first message)
    if session_id:
        # Validate session exists and belongs to user
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user.id
        ).first()
        
        if not session:
            await manager.send_personal_message({
                "type": "error",
                "error": "Invalid session_id"
            }, user.id)
            return
    else:
        # Create new session
        session_id = f"chat_{uuid4().hex[:8]}"
        session = ChatSession(
            id=session_id,
            user_id=user.id,
            user_message="",  # Will update after getting AI response
            ai_response="",
            session_type="advisory"  # Changed from general_inquiry to avoid enum error
        )
        db.add(session)
        db.commit()
        
        # Notify client of new session
        await manager.send_personal_message({
            "type": "session_created",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }, user.id)
    
    # Get conversation history from session
    conversation_history = get_conversation_history(session)
    
    # Process message with AI agent (with context)
    try:
        logger.info(f"Processing message for session {session_id} with {len(conversation_history)} previous messages")
        ai_response = await ai_agent.process_query(content, user=user, conversation_history=conversation_history)
        
        # Update conversation history in context_data
        if not session.context_data:
            session.context_data = {"messages": []}
        elif "messages" not in session.context_data:
            session.context_data["messages"] = []
        
        # Add user message to history
        session.context_data["messages"].append({
            "role": "user",
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Add AI response to history  
        session.context_data["messages"].append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Mark context_data as modified for SQLAlchemy to track changes
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(session, "context_data")
        
        # Update session with latest message (for backward compatibility)
        session.user_message = content
        session.ai_response = ai_response
        db.commit()
        
        # Send AI response back to client
        response_message = {
            "type": "ai_message",
            "content": ai_response,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "language": user.language_preference.value if user.language_preference else "english"
        }
        
        await manager.send_personal_message(response_message, user.id)
        logger.info(f"Sent AI response for session {session_id}")
        
    except Exception as e:
        logger.error(f"Error processing AI query: {e}", exc_info=True)
        await manager.send_personal_message({
            "type": "error",
            "error": "Failed to process message",
            "details": str(e),
            "session_id": session_id
        }, user.id)


@router.get("/history")
async def get_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for a specific session"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # For now, returning simple structure (can be enhanced with full message history)
    messages = [
        {
            "type": "user_message",
            "content": session.user_message,
            "timestamp": session.created_at.isoformat()
        },
        {
            "type": "ai_message",
            "content": session.ai_response,
            "timestamp": session.updated_at.isoformat() if session.updated_at else session.created_at.isoformat()
        }
    ]
    
    return ChatHistoryResponse(
        session_id=session.id,
        messages=messages,
        total_messages=len(messages),
        created_at=session.created_at,
        last_activity=session.updated_at
    )


@router.get("/sessions")
async def list_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all chat sessions for the current user"""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.created_at.desc()).limit(10).all()  # Limit to recent 10
    
    return [
        ChatSessionSummary(
            session_id=s.id,
            created_at=s.created_at,
            last_activity=s.updated_at,
            message_count=2,  # Simplified for now
            language_used=None
        )
        for s in sessions
    ]


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(session)
    db.commit()
    
    return {"message": "Session deleted successfully", "session_id": session_id}




@router.get("/active-session")
async def get_active_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get or create user's active chat session with full message history"""
    # Get most recent session
    session = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.created_at.desc()).first()
    
    if not session:
        # Create new session
        session_id = f"chat_{uuid4().hex[:8]}"
        session = ChatSession(
            id=session_id,
            user_id=current_user.id,
            user_message="",
            ai_response="",
            session_type="advisory",
            context_data={"messages": []}
        )
        db.add(session)
        db.commit()
    
    # Get conversation history
    messages = get_conversation_history(session)
    
    return {
        "session_id": session.id,
        "messages": messages,
        "created_at": session.created_at,
        "message_count": len(messages)
    }


@router.post("/voice")
async def upload_voice_note(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a voice note for transcription and AI processing
    
    Process:
    1. Save audio file temporarily
    2. Transcribe using Groq Whisper
    3. Detect language
    4. Process with AI agent
    5. Send response via WebSocket
    6. Optionally generate TTS response
    """
    import aiofiles
    import os
    from pathlib import Path
    import time
    
    # Validate file type
    if not file.content_type or 'audio' not in file.content_type:
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    # Validate or create session
    if session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Invalid session_id")
    else:
        # Create new session
        session_id = f"chat_{uuid4().hex[:8]}"
        session = ChatSession(
            id=session_id,
            user_id=current_user.id,
            user_message="",
            ai_response="",
            session_type="advisory"
        )
        db.add(session)
        db.commit()
        
        # Notify via WebSocket if connected
        if manager.is_connected(current_user.id):
            await manager.send_personal_message({
                "type": "session_created",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }, current_user.id)
    
    try:
        # Save file temporarily
        temp_dir = Path("temp_audio")
        temp_dir.mkdir(exist_ok=True)
        
        file_extension = Path(file.filename).suffix or ".ogg"
        temp_filename = f"voice_{uuid4().hex[:8]}{file_extension}"
        temp_path = temp_dir / temp_filename
        
        # Write file asynchronously
        async with aiofiles.open(temp_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        logger.info(f"Saved voice file: {temp_path}")
        
        # Transcribe using VoiceService
        transcription_result = await voice_service.transcribe_voice_note(str(temp_path))
        
        if not transcription_result:
            raise HTTPException(status_code=500, detail="Transcription failed")
        
        # Detect language (simplified - can enhance with language detection)
        detected_language = "english"  # Default
        # You can add language detection here based on transcription
        
        # Create VoiceMessage record
        voice_message = VoiceMessage(
            id=f"voice_{uuid4().hex[:8]}",
            user_id=current_user.id,
            audio_file_url=str(temp_path),  # In production, upload to S3/R2
            audio_duration_seconds=0.0,  # Can extract from file metadata
            language_detected=detected_language,
            transcription=transcription_result,
            transcription_confidence=0.95,
            processing_status="completed",
            processed_at=datetime.utcnow(),
            source=MessageSource.IN_APP
        )
        db.add(voice_message)
        db.commit()
        
        logger.info(f"Transcription: {transcription_result}")
        
        # Send transcription via WebSocket
        if manager.is_connected(current_user.id):
            await manager.send_personal_message({
                "type": "voice_transcription",
                "transcription": transcription_result,
                "confidence": 0.95,
                "language": detected_language,
                "session_id": session_id
            }, current_user.id)
        
        # Process with AI agent
        ai_response = await ai_agent.process_query(transcription_result, user=current_user)
        
        # Update session
        session.user_message = transcription_result
        session.ai_response = ai_response
        session.voice_message_id = voice_message.id
        db.commit()
        
        # Optional: Generate TTS response (placeholder for now)
        tts_audio_url = None
        # TODO: Implement TTS generation
        # tts_audio_url = await generate_tts(ai_response, language=detected_language)
        
        # Send AI response via WebSocket
        if manager.is_connected(current_user.id):
            await manager.send_personal_message({
                "type": "ai_message",
                "content": ai_response,
                "session_id": session_id,
                "tts_audio_url": tts_audio_url,
                "language": detected_language,
                "timestamp": datetime.utcnow().isoformat()
            }, current_user.id)
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        return {
            "session_id": session_id,
            "transcription": transcription_result,
            "ai_response": ai_response,
            "language": detected_language,
            "tts_audio_url": tts_audio_url
        }
        
    except Exception as e:
        logger.error(f"Error processing voice note: {e}", exc_info=True)
        
        # Send error via WebSocket
        if manager.is_connected(current_user.id):
            await manager.send_personal_message({
                "type": "error",
                "error": "Failed to process voice note",
                "details": str(e),
                "session_id": session_id
            }, current_user.id)
        
        raise HTTPException(status_code=500, detail=f"Error processing voice note: {str(e)}")

