from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_v1 import api_router
from app.core.config import settings
from app.db.session import engine
from app.db.base_class import Base

# Create tables in database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ShukaLink CRM",
    description="WhatsApp AI Agent for Smallholder Farmers",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
import os

# Create static dir if not exists
os.makedirs("static/produce_images", exist_ok=True)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"message": "ShukaLink CRM - WhatsApp AI Agent for Smallholder Farmers"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}