"""
Voice Service for processing voice notes using Groq Whisper
"""
import asyncio
import aiohttp
import tempfile
import requests
from typing import Optional
from pathlib import Path
from groq import Groq
from app.core.config import settings
from app.models.conversation import VoiceMessage
from app.db.session import SessionLocal


class VoiceService:
    """
    Service for handling voice messages using Groq Whisper for transcription
    """
    
    def __init__(self):
        # Initialize Groq client
        if settings.GROQ_API_KEY:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
        else:
            self.client = None
        
        # Use Groq's fastest Whisper model
        self.whisper_model = "whisper-large-v3-turbo"
    
    async def transcribe_voice_note(self, audio_url: str, language: str = "en") -> Optional[str]:
        """
        Transcribe a voice note using Groq Whisper API
        """
        if not self.client:
            print("Groq API key not configured")
            return None
            
        try:
            # Download the audio file
            response = requests.get(audio_url)
            if response.status_code != 200:
                print(f"Failed to download audio: {response.status_code}")
                return None
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            # Transcribe using Groq Whisper
            with open(temp_file_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model=self.whisper_model,
                    language=language,
                    response_format="text"
                )
            
            # Clean up temporary file
            Path(temp_file_path).unlink()
            
            # Groq returns the text directly when response_format="text"
            return transcription if isinstance(transcription, str) else transcription.text
            
        except Exception as e:
            print(f"Error transcribing voice note with Groq: {e}")
            # Clean up in case of error
            try:
                if 'temp_file_path' in locals():
                    Path(temp_file_path).unlink()
            except:
                pass
            return None
    
    def save_voice_message_to_db(self, user_id: str, audio_url: str, transcription: str = None) -> VoiceMessage:
        """
        Save voice message to database
        """
        db = SessionLocal()
        try:
            voice_message = VoiceMessage(
                user_id=user_id,
                audio_file_url=audio_url,
                audio_duration_seconds=0,  # Should calculate from audio file
                transcription=transcription,
                processing_status="completed" if transcription else "pending"
            )
            db.add(voice_message)
            db.commit()
            db.refresh(voice_message)
            return voice_message
        finally:
            db.close()