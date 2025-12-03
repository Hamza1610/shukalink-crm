# ShukaLink CRM — WhatsApp AI Agent for Smallholder Farmers

![ShukaLink Architecture](https://i.imgur.com/ShukaLink_architecture.png)

## 🌾 Project Overview

ShukaLink CRM is a WhatsApp-first AI-powered Customer Relationship Management system connecting Nigerian smallholder farmers with buyers. The system reduces post-harvest losses and increases farmer income through voice-enabled conversational interfaces in English and Hausa languages. Unlike traditional marketplaces, ShukaLink functions as a complete relationship manager—maintaining transaction history, building trust between parties, and guiding users through the entire sales lifecycle via familiar WhatsApp interfaces.

**Core Value Proposition:**
- 99% of farmers already use WhatsApp—zero learning curve
- Voice-first interface works for low-literacy users
- AI agent maintains relationship context across transactions
- Complete transaction lifecycle managed within WhatsApp
- Self-hosted AI infrastructure keeps operational costs minimal

## ⚙️ Technologies Used (Open Source / Free Tier Focused)

### Core Backend
- **FastAPI** (Python): High-performance API framework with automatic docs
- **PostgreSQL** via Supabase free tier: Relational database with geospatial support
- **ChromaDB**: Vector database for conversation context and relationship history
- **Redis**: Message queue for async processing and caching

### AI Layer
- **Llama 3 8B Instruct** (Ollama): Core reasoning engine fine-tuned for agricultural context
- **Whisper-large-v3** (fine-tuned on Hausa): Voice transcription for local dialects
- **Silero VAD**: Voice activity detection for cleaner audio processing
- **LangGraph**: Stateful workflow management for multi-step CRM operations

### Integration Services
- **Twilio WhatsApp API**: Free sandbox for WhatsApp integration
- **Paystack API**: Payment processing (required for Nigerian context)
- **Twilio Voice API**: Feature phone support via voice calls
- **OpenStreetMap Nominatim**: Free geocoding service

### Infrastructure
- **Fly.io**: Free tier hosting for backend services
- **AWS S3** (free tier): Storage for voice recordings
- **Cloudflare R2**: Free object storage for media files
- **Docker**: Containerization for consistent deployment
- **GitHub Actions**: CI/CD pipeline

## 🏗️ System Architecture

```mermaid
graph TD
    A[WhatsApp] -->|Voice/Text Messages| B(FastAPI Backend)
    C[Feature Phones] -->|Voice Calls| D(Twilio IVR)
    D --> B
    B --> E[CRM Context Engine]
    E --> F[Llama 3 8B Agent]
    F --> G[Tool Executors]
    G --> H[Marketplace Service]
    G --> I[Payment Service]
    G --> J[Logistics Service]
    G --> K[Advisory Service]
    H --> L[(PostgreSQL)]
    I --> M[Paystack API]
    K --> N[(ChromaDB Vector Store)]
```

## 🔌 API Endpoints Documentation

### Authentication
All endpoints require authentication via JWT token except WhatsApp webhook.

#### `POST /auth/otp-request`
Request OTP verification code via WhatsApp/SMS
```json
{
  "phone_number": "+2348012345678",
  "language_preference": "english|hausa"
}
```
Response:
```json
{
  "message": "OTP sent to +2348012345678",
  "expires_in": 300
}
```

#### `POST /auth/verify-otp`
Verify OTP code and receive JWT token
```json
{
  "phone_number": "+2348012345678",
  "otp_code": "123456"
}
```
Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "usr_123456",
    "phone_number": "+2348012345678",
    "user_type": "farmer",
    "language_preference": "hausa"
  }
}
```

### WhatsApp Integration
#### `POST /whatsapp/webhook` (Public endpoint)
WhatsApp message handler (no authentication required)
Headers:
- `X-Twilio-Signature`: Twilio request signature for verification

Request (Twilio format):
```json
{
  "From": "whatsapp:+2348012345678",
  "Body": "I want to sell my tomatoes",
  "MediaUrl0": "https://example.com/audio.mp3",
  "ProfileName": "Mallam Ibrahim"
}
```

Response (WhatsApp TwiML format):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Message>
    <Body>Great Mallam Ibrahim! How many kg of tomatoes do you have ready for sale?</Body>
  </Message>
</Response>
```

### Produce Management
#### `POST /produce` (Farmer only)
Create a new produce listing
Headers:
- `Authorization: Bearer <token>`

Request:
```json
{
  "crop_type": "tomatoes",
  "quantity_kg": 50,
  "harvest_date": "2025-12-05T00:00:00Z",
  "quality_indicators": ["firm", "no_blemishes"],
  "expected_price_per_kg": 1300,
  "location": {
    "coordinates": [11.8434, 8.4639],
    "description": "Mallam Ibrahim's farm, Gwarzo"
  }
}
```

Response:
```json
{
  "id": "prod_345678",
  "farmer_id": "usr_123456",
  "crop_type": "tomatoes",
  "quantity_kg": 50,
  "status": "available",
  "created_at": "2025-11-28T14:30:00Z",
  "expires_at": "2025-12-05T00:00:00Z"
}
```

#### `GET /produce` (Buyer/Farmer)
Search and list available produce
Headers:
- `Authorization: Bearer <token>`

Query Parameters:
- `crop_type`: Filter by crop type (optional)
- `min_quantity`: Minimum quantity in kg (optional)
- `radius_km`: Search radius from user's location (optional)
- `max_price`: Maximum price per kg (optional)

Response:
```json
{
  "items": [
    {
      "id": "prod_345678",
      "farmer_name": "Mallam Ibrahim",
      "crop_type": "tomatoes",
      "quantity_kg": 50,
      "price_per_kg": 1300,
      "distance_km": 3.2,
      "harvest_date": "2025-12-05T00:00:00Z",
      "has_transaction_history": true,
      "farmer_reliability_score": 4.8
    },
    {
      "id": "prod_456789",
      "farmer_name": "Aisha",
      "crop_type": "tomatoes",
      "quantity_kg": 30,
      "price_per_kg": 1250,
      "distance_km": 5.1,
      "harvest_date": "2025-12-01T00:00:00Z",
      "has_transaction_history": false,
      "farmer_reliability_score": 4.9
    }
  ],
  "total": 2,
  "page": 1,
  "size": 10
}
```

### Transaction Management
#### `POST /transactions/match`
Create a transaction match between farmer and buyer
Headers:
- `Authorization: Bearer <token>`

Request:
```json
{
  "produce_id": "prod_345678",
  "buyer_id": "usr_234567",
  "agreed_price_per_kg": 1280,
  "pickup_time": "2025-12-06T10:00:00Z"
}
```

Response:
```json
{
  "id": "txn_567890",
  "produce_id": "prod_345678",
  "farmer_id": "usr_123456",
  "buyer_id": "usr_234567",
  "status": "matched",
  "total_amount": 64000,
  "created_at": "2025-11-28T15:00:00Z",
  "payment_link": "https://paystack.com/pay/ShukaLink_567890"
}
```

#### `POST /payments/verify`
Verify payment completion (called by Paystack webhook)
Headers:
- `x-paystack-signature`: Paystack signature header

Request (Paystack format):
```json
{
  "event": "charge.success",
  "data": {
    "reference": "ShukaLink_567890",
    "amount": 6400000,
    "customer": {
      "phone": "+2348023456789"
    }
  }
}
```

Response:
```json
{
  "status": "success",
  "message": "Payment verified successfully"
}
```

### Logistics Coordination
#### `POST /logistics/request`
Request transport for a transaction
Headers:
- `Authorization: Bearer <token>`

Request:
```json
{
  "transaction_id": "txn_567890",
  "pickup_location": {
    "coordinates": [11.8434, 8.4639],
    "description": "Mallam Ibrahim's farm, Gwarzo"
  },
  "dropoff_location": {
    "coordinates": [11.9999, 8.5555],
    "description": "Fatima's warehouse, Kano city"
  },
  "pickup_time_window": {
    "start": "2025-12-06T10:00:00Z",
    "end": "2025-12-06T12:00:00Z"
  }
}
```

Response:
```json
{
  "id": "log_678901",
  "transaction_id": "txn_567890",
  "status": "requested",
  "estimated_cost": 5000,
  "estimated_completion_time": "2025-12-06T14:00:00Z",
  "contact_person": {
    "name": "Driver Aliyu",
    "phone": "+2348034567890"
  }
}
```

### CRM & Relationship Management
#### `GET /crm/relationships/{farmer_id}/{buyer_id}`
Get relationship history between a specific farmer and buyer
Headers:
- `Authorization: Bearer <token>` (Admin only)

Response:
```json
{
  "relationship_id": "rel_789012",
  "farmer_id": "usr_123456",
  "buyer_id": "usr_234567",
  "total_transactions": 5,
  "last_transaction": "2025-11-27T15:30:00Z",
  "average_payment_days": 1.2,
  "quality_ratings": [5, 4, 5, 5, 4],
  "notes": "Prefers early morning pickups; speaks Hausa only",
  "transaction_history": [
    {
      "date": "2025-11-27T15:30:00Z",
      "crop": "tomatoes",
      "quantity_kg": 30,
      "price_per_kg": 1200,
      "total_value": 36000,
      "payment_status": "completed",
      "quality_rating": 5
    },
    {
      "date": "2025-11-15T14:20:00Z",
      "crop": "onions",
      "quantity_kg": 40,
      "price_per_kg": 900,
      "total_value": 36000,
      "payment_status": "completed",
      "quality_rating": 4
    }
  ]
}
```

### Advisory Services
#### `POST /advisory/storage`
Get context-aware storage recommendations
Headers:
- `Authorization: Bearer <token>`

Request:
```json
{
  "crop_type": "yams",
  "quantity_kg": 200,
  "location": {
    "coordinates": [11.8434, 8.4639],
    "description": "Gwarzo, Kano State"
  },
  "storage_method": "mud_silo",
  "current_temperature_celsius": 32
}
```

Response:
```json
{
  "recommendations": [
    "Line the bottom of your mud silo with dry sand (2-inch layer)",
    "Place yams in single layer with space between them for ventilation",
    "Cover with dried neem leaves to prevent pests",
    "Check weekly for signs of rot or pest damage"
  ],
  "estimated_shelf_life_days": 60,
  "risk_factors": [
    "High temperature (32°C) increases moisture loss",
    "Mud silos provide good insulation but need proper ventilation"
  ],
  "expert_contact": {
    "name": "Kano State Agricultural Extension Service",
    "phone": "+2348045678901"
  }
}
```

## 💬 WhatsApp AI Agent Interface

### Core Capabilities
The WhatsApp AI Agent serves as the central CRM interface with these capabilities:

1. **Farmer Onboarding**
   ```
   Farmer: "Hi, I want to sell my crops"
   AI Agent: "Welcome to ShukaLink! I'll help you sell your produce and connect with buyers. What's your name and village?"
   ```

2. **Produce Listing via Voice**
   ```
   Farmer sends voice note in Hausa: "Ina kashe 50kg na tufa gaba da zuwa"
   AI Agent: "I understand you have 50kg of tomatoes ready next week. Your price last time was ₦1,200/kg. Would you like to offer them at ₦1,300/kg this time due to price increases?"
   ```

3. **Buyer Matching with Context**
   ```
   Buyer: "Looking for tomatoes near Kano"
   AI Agent: "🍅 Available tomatoes near you:
   1️⃣ Mallam Ibrahim (3km) - 50kg, ready Tuesday ₦1,300/kg 
      ✅ You bought from him before and rated 5/5
   2️⃣ Aisha (5km) - 30kg, ready today ₦1,250/kg 
      ✅ 98% on-time delivery rate
   Reply with number to connect"
   ```

4. **Payment Coordination**
   ```
   AI Agent: "Perfect! I've connected you with Mallam Ibrahim. Total cost: ₦65,000. Click here to pay securely: https://paystack.com/pay/ShukaLink_567890"
   
   [After payment confirmation]
   AI Agent: "✅ Payment confirmed! Mallam Ibrahim will prepare your tomatoes for pickup tomorrow between 10AM-12PM. Driver Aliyu will contact you at 0803..."
   ```

5. **Proactive Relationship Management**
   ```
   AI Agent (to farmer): "Hello Mallam Ibrahim! Your buyer Fatima has been looking for tomatoes again. She paid on time in 5 previous transactions. Would you like me to notify her when your next harvest is ready?"
   ```

6. **Context-Aware Advisory**
   ```
   Farmer: "My yams are getting soft"
   AI Agent: "Based on your location in Kano and current hot weather (32°C), your yams need better ventilation. Since you're using a mud silo, try these steps:
   1. Line the bottom with dry sand (2-inch layer)
   2. Place yams in single layer with space between them
   3. Cover with dried neem leaves (prevents pests)
   Would you like me to connect you with a storage expert?"
   ```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- Docker and Docker Compose
- Ollama (for local Llama 3 testing)
- Node.js 18+ (for WhatsApp sandbox testing)

### Local Development Setup
```bash
# Clone repository
git clone https://github.com/yourusername/ShukaLink-crm.git
cd ShukaLink-crm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Start database and cache services
docker-compose up -d

# Run database migrations
alembic upgrade head

# Download and set up Hausa fine-tuned models
./scripts/setup_hausa_model.sh

# Start FastAPI server
uvicorn main:app --reload --port 8000
```

### WhatsApp Sandbox Setup
```bash
# Install Twilio CLI
npm install -g twilio-cli

# Login to Twilio
twilio login

# Set up WhatsApp sandbox
twilio api:core:messages:create \
  --from 'whatsapp:+14155238886' \
  --to 'whatsapp:+2348012345678' \
  --body 'join <your-sandbox-keyword>'
```

## ☁️ Deployment Instructions

### Fly.io Deployment (Free Tier)
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login to Fly
flyctl auth login

# Launch app
flyctl launch --no-deploy

# Set secrets
flyctl secrets set \
  WHATSAPP_ACCOUNT_SID=your_sid \
  WHATSAPP_AUTH_TOKEN=your_token \
  PAYSTACK_SECRET_KEY=your_key \
  DATABASE_URL=your_supabase_url

# Deploy
flyctl deploy
```

### Environment Variables
```env
# Core Configuration
APP_ENV=development
APP_DEBUG=true
SECRET_KEY=your_strong_secret_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ShukaLink

# WhatsApp Integration
WHATSAPP_ACCOUNT_SID=your_twilio_sid
WHATSAPP_AUTH_TOKEN=your_twilio_token
WHATSAPP_PHONE_NUMBER=whatsapp:+14155238886

# Payment Integration
PAYSTACK_SECRET_KEY=sk_test_yourkey
PAYSTACK_PUBLIC_KEY=pk_test_yourkey
PAYSTACK_WEBHOOK_SECRET=whsec_yoursecret

# AI Models
LLAMA3_MODEL_PATH=./models/llama3-8b-agriculture.Q4_K_M.gguf
WHISPER_MODEL=large-v3

# Voice Integration
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890

# Storage
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=af-south-1
S3_BUCKET_NAME=ShukaLink-recordings

# Vector Database
CHROMADB_PATH=./data/chromadb
```

## 📊 Data Models

### User Model
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: f"usr_{uuid4().hex[:6]}")
    phone_number = Column(String, unique=True, index=True)
    user_type = Column(Enum("farmer", "buyer", "admin"), default="farmer")
    language_preference = Column(Enum("english", "hausa"), default="english")
    location = Column(Geometry("POINT"))
    village = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    reliability_score = Column(Float, default=5.0)
    
    # Farmer-specific fields
    crops_grown = Column(ARRAY(String))
    storage_capacity_kg = Column(Integer)
    storage_type = Column(String)  # "mud_silo", "plastic_bins", etc.
    
    # Buyer-specific fields
    business_name = Column(String)
    typical_purchase_volume_kg = Column(Integer)
```

### Relationship Model
```python
class Relationship(Base):
    __tablename__ = "relationships"
    
    id = Column(String, primary_key=True, default=lambda: f"rel_{uuid4().hex[:6]}")
    farmer_id = Column(String, ForeignKey("users.id"))
    buyer_id = Column(String, ForeignKey("users.id"))
    relationship_start = Column(DateTime, default=datetime.utcnow)
    total_transactions = Column(Integer, default=0)
    last_transaction = Column(DateTime)
    average_payment_days = Column(Float, default=0.0)
    quality_ratings = Column(ARRAY(Integer))
    notes = Column(Text)
    
    farmer = relationship("User", foreign_keys=[farmer_id])
    buyer = relationship("User", foreign_keys=[buyer_id])
```

## 🗓️ Future Roadmap

### Phase 2 (Post-MVP)
- **Multi-dialect Support**: Pidgin and Yoruba language support
- **USSD Interface**: Basic feature phone support via USSD codes
- **Predictive Analytics**: Recommend optimal harvest and selling times based on market data
- **Credit Scoring**: Build credit profiles for farmers based on transaction history

### Phase 3 (Scale)
- **Cold Chain Integration**: Connect with refrigerated transport providers
- **Input Marketplace**: Link farmers to seed/fertilizer suppliers
- **Government Integration**: Share anonymized data with agricultural ministries for policy planning
- **Multi-country Expansion**: Adapt for Ghana, Kenya markets with localized models

---

**ShukaLink CRM is proudly built with open-source technologies and designed for real-world impact in Nigerian agriculture.** 

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0-black.svg)](https://fastapi.tiangolo.com/)

*Reducing post-harvest losses, increasing farmer income, one WhatsApp message at a time.*