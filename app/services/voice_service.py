"""
Voice Service for processing voice notes using Whisper models
"""
import asyncio
import aiohttp
import tempfile
import requests
from typing import Optional
from pathlib import Path
import openai
from app.core.config import settings
from app.models.conversation import VoiceMessage
from app.db.session import SessionLocal


class VoiceService:
    """
    Service for handling voice messages, including transcription and text-to-speech
    """
    
    def __init__(self):
        # Initialize OpenAI API for Whisper and TTS
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        self.whisper_model = "whisper-1"
        self.tts_model = "tts-1"
        self.voice = "alloy"  # Default voice for text-to-speech
    
    async def transcribe_voice_note(self, audio_url: str, language: str = "en") -> Optional[str]:
        """
        Transcribe a voice note using Whisper API
        """
        try:
            # Download the audio file
            response = requests.get(audio_url)
            if response.status_code != 200:
                return None
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            # Transcribe using OpenAI Whisper
            with open(temp_file_path, "rb") as audio_file:
                transcript = openai.Audio.transcribe(
                    model=self.whisper_model,
                    file=audio_file,
                    language=language
                )
            
            # Clean up temporary file
            Path(temp_file_path).unlink()
            
            return transcript.text if transcript.text else None
            
        except Exception as e:
            print(f"Error transcribing voice note: {e}")
            # Clean up in case of error
            try:
                Path(temp_file_path).unlink()
            except:
                pass
            return None
    
    async def text_to_speech(self, text: str, voice: str = None) -> Optional[str]:
        """
        Convert text to speech using OpenAI TTS
        Returns URL to the generated audio file
        """
        try:
            if not settings.OPENAI_API_KEY:
                return None
            
            # Use the provided voice or default
            voice = voice or self.voice
            
            # Generate speech using OpenAI TTS
            response = openai.Audio.speech.create(
                model=self.tts_model,
                voice=voice,
                input=text
            )
            
            # Save the audio to a temporary file and return its URL
            # In a real implementation, you would upload to your storage service
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                response.stream_to_file(temp_file.name)
                # Return a placeholder URL - in real implementation, upload to storage
                return f"temp_audio/{Path(temp_file.name).name}"
                
        except Exception as e:
            print(f"Error generating speech: {e}")
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