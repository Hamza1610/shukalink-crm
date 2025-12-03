"""
Logistics Service for transport and delivery management
"""
from typing import Optional
from app.models.user import User


class LogisticsService:
    """
    Logistics service that handles transport and delivery for agricultural products
    """
    
    def __init__(self):
        # Initialize with transport rates and logistics information
        self.transport_rates = {
            'local': 500,  # per bag within local area
            'regional': 1500,  # per bag to nearby regions
            'national': 3000  # per bag to other parts of the country
        }
        
        self.delivery_status = {
            'pending': 'Order placed, awaiting pickup',
            'in_transit': 'In transit to destination',
            'delivered': 'Delivered successfully',
            'delayed': 'Delivery delayed, expected soon'
        }
    
    def get_transport_info(self, query: str, user: Optional[User] = None):
        """
        Provide transport and logistics information based on user query
        """
        query_lower = query.lower().strip()
        
        if 'rate' in query_lower or 'price' in query_lower or 'cost' in query_lower:
            return self._get_transport_rates(query_lower)
        
        elif 'track' in query_lower or 'status' in query_lower or 'delivery' in query_lower:
            return self._get_delivery_status(query_lower)
        
        elif 'book' in query_lower or 'order' in query_lower or 'schedule' in query_lower:
            return self._book_transport_info()
        
        else:
            # Default response with general logistics information
            response = ("🚛 *AgriConnect Logistics Services*\n\n"
                       "We provide reliable transport for your agricultural produce:\n\n"
                       "• Local transport (same region): ₦500 per bag\n"
                       "• Regional transport: ₦1,500 per bag\n"
                       "• National transport: ₦3,000 per bag\n\n"
                       "To get specific rates, track delivery, or book transport:\n"
                       "- Reply 'rates [destination]' for pricing\n"
                       "- Reply 'track [order ID]' to check status\n"
                       "- Reply 'book' to schedule pickup")
            return response
    
    def _get_transport_rates(self, query: str):
        """
        Get transport rates based on destination
        """
        if 'local' in query:
            return f"Local transport rate: ₦{self.transport_rates['local']} per bag"
        elif 'regional' in query or any(region in query for region in ['kano', 'katsina', 'jigawa', 'kaduna']):
            return f"Regional transport rate: ₦{self.transport_rates['regional']} per bag"
        elif 'national' in query or 'country' in query:
            return f"National transport rate: ₦{self.transport_rates['national']} per bag"
        else:
            # Try to determine rate based on number of bags
            import re
            bags_match = re.search(r'(\d+)\s*(bags?|baskets?|loads?)', query)
            if bags_match:
                num_bags = int(bags_match.group(1))
                rate = self.transport_rates['regional']  # default to regional
                total = num_bags * rate
                return (f"Transport rate: ₦{rate} per bag\n"
                       f"Total for {num_bags} bags: ₦{total}\n"
                       f"Reply 'book' to schedule pickup")
            else:
                return ("Transport rates:\n"
                       f"• Local: ₦{self.transport_rates['local']} per bag\n"
                       f"• Regional: ₦{self.transport_rates['regional']} per bag\n"
                       f"• National: ₦{self.transport_rates['national']} per bag")
    
    def _get_delivery_status(self, query: str):
        """
        Get delivery status based on order ID or user context
        """
        import re
        order_id_match = re.search(r'(?:order|delivery|track)\s*#?(\w+)', query)
        
        if order_id_match:
            order_id = order_id_match.group(1)
            # In a real system, this would look up the order in a database
            # For demo, return a random status
            import random
            statuses = list(self.delivery_status.keys())
            status = random.choice(statuses)
            return f"Order #{order_id} status: {self.delivery_status[status]}"
        else:
            return ("To track delivery, reply with 'track [order ID]'\n"
                   "Example: 'track ABC123'")
    
    def _book_transport_info(self):
        """
        Provide information about booking transport
        """
        return ("To book transport, provide the following information:\n\n"
               "1. Number of bags/baskets\n"
               "2. Type of produce\n"
               "3. Pickup location\n"
               "4. Destination\n"
               "5. Preferred pickup time\n\n"
               "Example: 'I need transport for 10 bags of maize from Kaduna to Kano'")
    
    def schedule_pickup(self, user: User, produce_type: str, quantity: int, pickup_location: str, destination: str, time: str):
        """
        Schedule a pickup for agricultural produce
        """
        # Generate a mock order ID
        import random
        import string
        order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        response = (f"🚛 *Transport Scheduled Successfully!*\n\n"
                   f"Order ID: {order_id}\n"
                   f"Produce: {quantity} bags of {produce_type}\n"
                   f"Pickup: {pickup_location}\n"
                   f"Destination: {destination}\n"
                   f"Pickup Time: {time}\n\n"
                   f"Transport cost: ₦{quantity * self.transport_rates['regional']}\n"
                   f"Status: {self.delivery_status['pending']}\n\n"
                   f"You will receive updates on your delivery status. Reply 'track {order_id}' to check status anytime.")
        
        return response