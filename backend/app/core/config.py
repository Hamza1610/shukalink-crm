from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    WHATSAPP_ACCOUNT_SID: Optional[str] = None
    WHATSAPP_AUTH_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_NUMBER: Optional[str] = None
    PAYSTACK_SECRET_KEY: Optional[str] = None
    PAYSTACK_PUBLIC_KEY: Optional[str] = None
    PAYSTACK_WEBHOOK_SECRET: Optional[str] = None
    LLAMA3_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    WHISPER_MODEL: str = "large-v3"
    CHROMADB_PATH: str = "./data/chromadb"
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")


settings = Settings()