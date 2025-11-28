from fastapi import APIRouter
from app.api.endpoints import auth, whatsapp, produce, payments, logistics, admin

api_router = APIRouter()

# Include API endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])
api_router.include_router(produce.router, prefix="/produce", tags=["produce"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(logistics.router, prefix="/logistics", tags=["logistics"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])