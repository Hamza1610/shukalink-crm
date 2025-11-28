from pydantic_settings import Settings
from typing import Optional


class Settings(Settings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/agrilink"
    WHATSAPP_ACCOUNT_SID: Optional[str] = None
    WHATSAPP_AUTH_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_NUMBER: Optional[str] = None
    PAYSTACK_SECRET_KEY: Optional[str] = None
    PAYSTACK_PUBLIC_KEY: Optional[str] = None
    PAYSTACK_WEBHOOK_SECRET: Optional[str] = None
    LLAMA3_MODEL_PATH: str = "./models/llama3-8b-agriculture.Q4_K_M.gguf"
    WHISPER_MODEL: str = "large-v3"
    CHROMADB_PATH: str = "./data/chromadb"


settings = Settings()