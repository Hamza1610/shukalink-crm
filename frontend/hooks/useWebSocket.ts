/**
 * Custom React hook for WebSocket chat connection
 * Handles connection, reconnection, message sending/receiving
 */
import { useEffect, useRef, useState, useCallback } from 'react';

interface ChatMessage {
    type: 'text_message' | 'ai_message' | 'session_created' | 'voice_transcription' | 'error';
    content?: string;
    session_id?: string;
    timestamp?: string;
    language?: string;
    tts_audio_url?: string;
    transcription?: string;
    confidence?: number;
    error?: string;
    details?: string;
}

interface UseWebSocketReturn {
    isConnected: boolean;
    messages: ChatMessage[];
    sessionId: string | null;
    sendMessage: (content: string) => void;
    uploadVoice: (audioBlob: Blob) => Promise<void>;
    clearMessages: () => void;
}

export function useWebSocket(userId: string, token: string): UseWebSocketReturn {
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
    const [isConnected, setIsConnected] = useState(false);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [sessionId, setSessionId] = useState<string | null>(null);

    const connect = useCallback(() => {
        if (!userId || !token) return;

        // Close existing connection

        if (wsRef.current) {
            wsRef.current.close();
        }

        const wsUrl = `ws://localhost:8000/api/v1/chat/ws/chat/${userId}?token=${token}`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('WebSocket connected');
            setIsConnected(true);
        };

        ws.onmessage = (event) => {
            try {
                const data: ChatMessage = JSON.parse(event.data);
                console.log('Received message:', data);

                // Handle session creation
                if (data.type === 'session_created') {
                    setSessionId(data.session_id || null);
                }

                // Add message to list
                setMessages(prev => [...prev, data]);
            } catch (error) {
                console.error('Failed to parse message:', error);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected');
            setIsConnected(false);

            // Auto-reconnect after 3 seconds
            reconnectTimeoutRef.current = setTimeout(() => {
                console.log('Attempting to reconnect...');
                connect();
            }, 3000);
        };

        wsRef.current = ws;
    }, [userId, token]);

    useEffect(() => {
        connect();

        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [connect]);

    const sendMessage = useCallback((content: string) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            console.error('WebSocket not connected');
            return;
        }

        const message = {
            type: 'text_message',
            content,
            ...(sessionId && { session_id: sessionId })
        };

        wsRef.current.send(JSON.stringify(message));

        // Optimistically add user message to UI
        setMessages(prev => [...prev, {
            type: 'text_message',
            content,
            session_id: sessionId || undefined,
            timestamp: new Date().toISOString()
        }]);
    }, [sessionId]);

    const uploadVoice = useCallback(async (audioBlob: Blob) => {
        const formData = new FormData();
        formData.append('file', audioBlob, 'voice.webm');
        if (sessionId) {
            formData.append('session_id', sessionId);
        }

        try {
            const response = await fetch('http://localhost:8000/api/v1/chat/voice', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to upload voice note');
            }

            const data = await response.json();
            console.log('Voice upload response:', data);

        } catch (error) {
            console.error('Error uploading voice:', error);
            setMessages(prev => [...prev, {
                type: 'error',
                error: 'Failed to upload voice note',
                details: error instanceof Error ? error.message : 'Unknown error'
            }]);
        }
    }, [token, sessionId]);

    const clearMessages = useCallback(() => {
        setMessages([]);
        setSessionId(null);
    }, []);

    return {
        isConnected,
        messages,
        sessionId,
        sendMessage,
        uploadVoice,
        clearMessages
    };
}
