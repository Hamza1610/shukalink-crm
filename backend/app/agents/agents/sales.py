from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.config import settings
from app.agents.tools.payment_tools import get_payment_info, process_payment

def create_sales_agent():
    """Create the sales/transaction agent"""
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")
        
    llm = ChatGroq(
        temperature=0.3,
        model_name="llama-3.1-8b-instant",
        groq_api_key=settings.GROQ_API_KEY
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a sales and payment assistant for AgriLink. You help users with transactions and payments.

**IMPORTANT GUIDELINES:**
1. **Be Conversational**: Respond to greetings naturally
2. **Use get_payment_info**: For checking payment status or history
3. **Careful with process_payment**: 
   - ONLY call this if you have a specific numeric amount
   - The amount parameter MUST be a number (e.g., 5000.0), NOT a string
   - If you don't have an amount, explain to user how payments work instead
4. **Be Security-Conscious**: Reassure users about payment security

**Examples:**
User: "Check my payment status"
You: Call get_payment_info with their query

User: "How do I pay?"
You: "Payments on AgriLink are secure and easy! When you're ready to pay for a transaction, I'll generate a payment link sent directly to your WhatsApp. You can pay with your card or bank transfer. Do you have a specific payment you'd like to make?"

**CRITICAL**: Never call process_payment without a specific numeric amount. The amount must be a number type."""),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    tools = [get_payment_info, process_payment]
    return prompt | llm.bind_tools(tools)
