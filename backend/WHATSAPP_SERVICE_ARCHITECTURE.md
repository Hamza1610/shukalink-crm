# WhatsApp Service Architecture

## Overview
The WhatsApp service in AgriConnect is a comprehensive system that leverages Twilio's WhatsApp API to provide an intelligent conversational interface for farmers and buyers. The service handles both text and voice messages, processes them through an AI agent, and provides intelligent responses and task execution.

## Core Components

### 1. WhatsApp Flow Service (`app/services/whatsapp_flow.py`)
The main WhatsApp service that orchestrates the entire flow:

- **Message Reception**: Handles incoming messages from Twilio webhooks
- **Voice Processing**: Converts voice notes to text using Whisper models
- **AI Integration**: Routes processed messages to the AI agent
- **Conversation Management**: Maintains session state and context
- **Response Generation**: Handles text and voice responses back to users

### 2. AI Agent (`app/services/ai_service.py`)
The intelligent agent that processes user requests:

- **Intent Recognition**: Identifies user intentions from text/voice input
- **Function Calling**: Directly calls other service methods (advisory, logistics, payment, CRM)
- **Context Management**: Maintains conversation context and user state
- **Response Generation**: Generates appropriate responses based on user needs

### 3. Voice Service (`app/services/voice_service.py`)
Handles voice processing using OpenAI's Whisper and TTS:

- **Speech-to-Text**: Converts voice messages to text using Whisper
- **Text-to-Speech**: Converts AI responses to voice using TTS
- **Audio Processing**: Manages audio file handling and storage

### 4. Supporting Services
- **Advisory Service**: Provides farming advice and recommendations
- **Logistics Service**: Manages transport and delivery requests
- **Payment Service**: Handles payment processing and verification
- **CRM Service**: Manages user profiles and relationships

## Schema Architecture

### WhatsApp Schemas (`app/schemas/whatsapp.py`)
- `WhatsAppWebhookRequest`: Incoming message data from Twilio
- `WhatsAppWebhookResponse`: Response structure for Twilio
- `WhatsAppMessageRequest`: Schema for sending messages to users
- `WhatsAppConversationState`: Tracks conversation state and context

### Voice Schemas (`app/schemas/voice.py`)
- `VoiceTranscriptionRequest`: Request for voice transcription
- `VoiceTranscriptionResponse`: Response with transcription results
- `TextToSpeechRequest`: Request for text-to-speech conversion
- `TextToSpeechResponse`: Response with audio URL

### Domain Schemas
- `produce.py`: Schemas for produce listings and management
- `logistics.py`: Schemas for logistics and transport requests
- `transaction.py`: Schemas for transaction management
- `user.py`: User profiles and authentication

## Flow Architecture

### Message Processing Flow
1. **Inbound Message**: Twilio sends message to `/whatsapp/webhook`
2. **Voice Processing**: If voice message, convert to text using Whisper
3. **AI Processing**: Pass processed text to AI agent
4. **Intent Recognition**: AI determines user intent and required actions
5. **Service Calls**: AI agent calls appropriate services directly
6. **Response Generation**: AI generates appropriate response
7. **Outbound Response**: Send response back via Twilio (text or voice)

### Voice Processing Flow
1. **Voice Message Received**: Twilio sends voice message URL
2. **Audio Download**: Download audio from Twilio URL
3. **Speech-to-Text**: Convert audio to text using Whisper
4. **Transcription Processing**: Process transcribed text with AI agent
5. **Response Generation**: Generate text response from AI
6. **Text-to-Speech**: Convert response to voice if needed
7. **Send Response**: Send text or voice response back to user

## Conversation States
The system maintains conversation context through:
- Session state management
- User profile integration
- Multi-turn conversation handling
- Context persistence across messages

## Error Handling
- Fallback mechanisms for AI failures
- Voice processing error handling
- Twilio webhook validation
- Graceful degradation for service failures

## Integration Points
- Twilio WhatsApp API for messaging
- OpenAI Whisper/TTS for voice processing
- Internal services for domain-specific functionality
- Database for state and context persistence

## Security
- Twilio signature verification
- User authentication and authorization
- Secure API key management
- Data privacy compliance

This architecture enables a sophisticated WhatsApp-based agricultural assistant that can understand both text and voice commands, execute complex tasks across multiple services, and maintain intelligent conversations with farmers and buyers.