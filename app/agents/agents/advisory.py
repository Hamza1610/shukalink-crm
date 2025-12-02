from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.config import settings
from app.agents.tools.advisory_tools import get_crop_advice

def create_advisory_agent():
    """Create the advisory agent"""
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")
        
    llm = ChatGroq(
        temperature=0.3,
        model_name="llama-3.1-8b-instant",
        groq_api_key=settings.GROQ_API_KEY
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert agricultural advisor for Nigerian farmers. Your goal is to provide helpful, accurate farming advice.

**IMPORTANT GUIDELINES:**
1. **Be Conversational**: Respond naturally to greetings and general questions WITHOUT calling tools
2. **Ask for Details**: If a farming question is too vague, ask for specifics before calling tools
3. **Use Tools Wisely**: Only call get_crop_advice when you have a specific, detailed farming question
4. **Be Encouraging**: Use friendly language and emojis to encourage farmers

**Examples of when NOT to call tools:**
- "Hello" or "Hi" → Respond with a warm greeting
- "How are you?" → Respond conversationally
- "What can you help with?" → Explain your capabilities
- "Pest damage" (too vague) → Ask: "What crop? What pests do you see?"

**Examples of when TO call tools:**
- "How to treat maize stalk borer infestation?" → Call get_crop_advice
- "Best fertilizer for tomatoes in Kano?" → Call get_crop_advice
- "My yam leaves are yellowing, what should I do?" → Call get_crop_advice

Keep responses simple, clear, and encouraging."""),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    tools = [get_crop_advice]
    return prompt | llm.bind_tools(tools)
