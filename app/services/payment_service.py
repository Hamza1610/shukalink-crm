"""
Payment Service for handling transactions
"""
from typing import Optional
from app.models.user import User


class PaymentService:
    """
    Payment service that handles transactions for agricultural services
    """
    
    def __init__(self):
        # Initialize with payment methods and transaction tracking
        self.payment_methods = ['bank_transfer', 'mobile_money', 'cash_on_delivery']
        self.transaction_status = {
            'pending': 'Payment initiated, awaiting confirmation',
            'confirmed': 'Payment confirmed and processed',
            'failed': 'Payment failed, please try again',
            'refunded': 'Payment refunded to your account'
        }
        
        # Mock payment gateway configuration
        self.payment_gateways = {
            'paystack': {'enabled': True, 'fees': 1.5},  # 1.5% fee
            'flutterwave': {'enabled': True, 'fees': 1.4},  # 1.4% fee
        }
    
    def get_payment_info(self, query: str, user: Optional[User] = None):
        """
        Provide payment information based on user query
        """
        query_lower = query.lower().strip()
        
        if 'status' in query_lower or 'confirm' in query_lower or 'verify' in query_lower:
            return self._get_payment_status(query_lower)
        
        elif 'make' in query_lower or 'pay' in query_lower or 'process' in query_lower:
            return self._make_payment_info()
        
        elif 'history' in query_lower or 'past' in query_lower or 'previous' in query_lower:
            return self._get_payment_history()
        
        elif 'method' in query_lower or 'option' in query_lower or 'gateway' in query_lower:
            return self._get_payment_methods()
        
        else:
            # Default response with general payment information
            response = ("💳 *AgriConnect Payment Services*\n\n"
                       "Secure payment options for your agricultural transactions:\n\n"
                       "• Bank Transfer\n"
                       "• Mobile Money (e.g., MTN Mobile Money)\n"
                       "• Cash on Delivery\n\n"
                       "Payment fees: 1.4-1.5% depending on method\n\n"
                       "To get specific info:\n"
                       "- Reply 'status [transaction ID]' to check payment\n"
                       "- Reply 'pay [amount] [service]' to make payment\n"
                       "- Reply 'history' to view payment history")
            return response
    
    def _get_payment_status(self, query: str):
        """
        Get payment status based on transaction ID
        """
        import re
        transaction_id_match = re.search(r'(?:transaction|payment|tx)\s*#?(\w+)', query)
        
        if transaction_id_match:
            tx_id = transaction_id_match.group(1)
            # In a real system, this would look up the transaction in a database
            # For demo, return a random status
            import random
            statuses = list(self.transaction_status.keys())
            status = random.choice(statuses)
            return f"Transaction #{tx_id} status: {self.transaction_status[status]}"
        else:
            return ("To check payment status, reply with 'status [transaction ID]'\n"
                   "Example: 'status TX123ABC'")
    
    def _make_payment_info(self):
        """
        Provide information about making payments
        """
        return ("To make a payment, provide the following information:\n\n"
               "1. Amount to pay\n"
               "2. Service being paid for\n"
               "3. Preferred payment method\n\n"
               "Available payment methods:\n"
               "- Bank Transfer\n"
               "- Mobile Money\n"
               "- Cash on Delivery\n\n"
               "Example: 'Pay ₦5,000 for transport service via mobile money'")
    
    def _get_payment_history(self, user: Optional[User] = None):
        """
        Get payment history for a user
        """
        # In a real system, this would fetch from a database
        # For demo, return mock history
        history = ("📊 *Payment History*\n\n"
                  "1. TX-789012 - ₦15,000 - Transport Service - 2 days ago - Confirmed\n"
                  "2. TX-654321 - ₦8,500 - Advisory Service - 1 week ago - Confirmed\n"
                  "3. TX-112233 - ₦25,000 - Logistics Service - 2 weeks ago - Confirmed\n\n"
                  "For detailed history, visit our web portal or contact support.")
        return history
    
    def _get_payment_methods(self):
        """
        Get available payment methods
        """
        return ("💳 *Available Payment Methods*\n\n"
               "1. Bank Transfer\n"
               "   - Direct transfer to our business account\n"
               "   - Processing time: 1-2 business days\n\n"
               "2. Mobile Money (e.g., MTN, Airtel, GLO)\n"
               "   - Instant payment via mobile wallet\n"
               "   - Available 24/7\n\n"
               "3. Cash on Delivery\n"
               "   - Pay when service is delivered\n"
               "   - Available for local deliveries\n\n"
               "Fees: 1.4-1.5% depending on method used")
    
    def process_payment(self, user: User, amount: float, service: str, method: str = 'mobile_money'):
        """
        Process a payment for a specific service
        """
        # Validate payment method
        if method.lower() not in self.payment_methods:
            return f"Invalid payment method. Available methods: {', '.join(self.payment_methods)}"
        
        # Calculate fees
        gateway = 'paystack' if 'bank' in method.lower() else 'flutterwave'
        fee_percentage = self.payment_gateways[gateway]['fees']
        fee = amount * (fee_percentage / 100)
        total_amount = amount + fee
        
        # Generate mock transaction ID
        import random
        import string
        transaction_id = 'TX-' + ''.join(random.choices(string.digits, k=6))
        
        response = (f"💳 *Payment Processing*\n\n"
                   f"Transaction ID: {transaction_id}\n"
                   f"Service: {service}\n"
                   f"Amount: ₦{amount:,.2f}\n"
                   f"Processing Fee ({fee_percentage}%): ₦{fee:,.2f}\n"
                   f"Total: ₦{total_amount:,.2f}\n"
                   f"Method: {method.title()}\n"
                   f"Status: {self.transaction_status['pending']}\n\n"
                   f"Please complete your payment via {method}. "
                   f"You will receive confirmation once payment is verified. "
                   f"Reply 'status {transaction_id}' to check payment status.")
        
        return response