from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.config import settings
from app.agents.tools.logistics_tools import get_transport_info, schedule_transport

def create_logistics_agent():
    """Create the logistics agent"""
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")
        
    llm = ChatGroq(
        temperature=0.3,
        model_name="llama-3.1-8b-instant",
        groq_api_key=settings.GROQ_API_KEY
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a logistics coordinator for ShukaLink. You help arrange transport for farmers' produce.

**IMPORTANT GUIDELINES:**
1. **Be Conversational**: Respond to greetings naturally without calling tools
2. **Gather Complete Information**: Before calling schedule_transport, you MUST have:
   - Type of produce (e.g., "maize", "tomatoes")
   - Quantity (e.g., "50 bags", "100kg")
   - Destination (e.g., "Kano market", "Lagos")
3. **Ask for Missing Details**: If any info is missing, ask the user for it
4. **Use get_transport_info**: For questions about rates or availability
5. **Only schedule when ready**: Call schedule_transport ONLY when you have all three pieces of info

**Example Flow:**
User: "I need to transport rice"
You: "I can help with that! 🚛 To arrange transport, I need to know:
- How much rice? (bags or kg)
- Where are you taking it?

Once I have these details, I can schedule a pickup for you."

**When NOT to call tools:**
- "Hello" → Respond with greeting
- "What can you do?" → Explain your capabilities

Be efficient and friendly!"""),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    tools = [get_transport_info, schedule_transport]
    return prompt | llm.bind_tools(tools)
