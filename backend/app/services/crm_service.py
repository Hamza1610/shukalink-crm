"""
CRM Service for customer relationship management
"""
from typing import Optional
from app.models.user import User


class CRMService:
    """
    Customer Relationship Management service for managing user interactions
    """
    
    def __init__(self):
        # Initialize CRM data structures
        self.customer_segments = {
            'smallholder': 'Farmers with small plots (<5 hectares)',
            'mediumholder': 'Farmers with medium plots (5-20 hectares)',
            'largeholder': 'Farmers with large plots (>20 hectares)',
            'cooperative': 'Farmer cooperatives and groups',
            'buyer': 'Agricultural produce buyers'
        }
        
        self.communication_history = {}
        self.customer_preferences = {}
    
    def get_customer_info(self, user: User):
        """
        Get detailed customer information
        """
        # In a real system, this would fetch from a database
        # For demo, return mock customer info
        customer_info = {
            'id': user.id,
            'phone': user.phone_number,
            'name': user.village or 'Unknown',
            'type': user.user_type or 'farmer',
            'registration_date': user.created_at,
            'last_interaction': 'Today',
            'preferred_language': 'English',
            'location': 'Nigeria'
        }
        
        info_str = (f"👤 *Customer Profile*\n\n"
                   f"Name: {customer_info['name']}\n"
                   f"Phone: {customer_info['phone']}\n"
                   f"Type: {customer_info['type'].title()}\n"
                   f"Registration: {customer_info['registration_date'] or 'Unknown'}\n"
                   f"Last Interaction: {customer_info['last_interaction']}\n"
                   f"Preferred Language: {customer_info['preferred_language']}\n"
                   f"Location: {customer_info['location']}")
        
        return info_str
    
    def update_customer_preferences(self, user: User, preferences: dict):
        """
        Update customer preferences
        """
        user_id = user.id
        if user_id not in self.customer_preferences:
            self.customer_preferences[user_id] = {}
        
        self.customer_preferences[user_id].update(preferences)
        return f"Preferences updated successfully for user {user.phone_number}"
    
    def get_customer_segment_info(self, user: User):
        """
        Get information about customer segment
        """
        # Determine segment based on user type or other criteria
        user_type = user.user_type or 'farmer'
        
        if 'farmer' in user_type.lower():
            if 'small' in user_type or 'subsistence' in user_type:
                segment = 'smallholder'
            elif 'large' in user_type or 'commercial' in user_type:
                segment = 'largeholder'
            else:
                segment = 'mediumholder'
        else:
            segment = 'buyer'
        
        segment_info = self.customer_segments.get(segment, 'General')
        
        return (f"📊 *Customer Segment: {segment.title()}*\n\n"
               f"Description: {segment_info}\n\n"
               f"Services available for this segment:\n"
               f"• Tailored advisory services\n"
               f"• Specialized logistics options\n"
               f"• Customized payment plans\n"
               f"• Priority support")
    
    def log_interaction(self, user: User, interaction_type: str, notes: str = ""):
        """
        Log customer interaction for relationship management
        """
        user_id = user.id
        if user_id not in self.communication_history:
            self.communication_history[user_id] = []
        
        import datetime
        interaction = {
            'timestamp': datetime.datetime.now(),
            'type': interaction_type,
            'notes': notes
        }
        
        self.communication_history[user_id].append(interaction)
        return f"Interaction logged successfully for {user.phone_number}"
    
    def get_communication_history(self, user: User):
        """
        Get communication history for a customer
        """
        user_id = user.id
        history = self.communication_history.get(user_id, [])
        
        if not history:
            return f"No communication history found for {user.phone_number}"
        
        history_str = f"📞 *Communication History for {user.phone_number}*\n\n"
        for i, interaction in enumerate(history[-5:], 1):  # Show last 5 interactions
            history_str += (f"{i}. {interaction['type'].title()} - "
                           f"{interaction['timestamp'].strftime('%Y-%m-%d %H:%M')}\n")
            if interaction['notes']:
                history_str += f"   Notes: {interaction['notes']}\n"
            history_str += "\n"
        
        return history_str
    
    def send_targeted_message(self, user: User, message_type: str):
        """
        Send targeted message based on customer segment and preferences
        """
        # Determine appropriate message based on type
        if message_type == 'promotional':
            message = ("🎉 *Special Offer for Valued Customers!*\n\n"
                      "Get 10% discount on logistics services this month. "
                      "Book your transport with us and enjoy cost savings. "
                      "Reply 'BOOK' to schedule pickup now!")
        
        elif message_type == 'educational':
            message = ("📚 *Weekly Farming Tip*\n\n"
                      "Crop rotation helps maintain soil fertility and reduces pest buildup. "
                      "Consider rotating legumes with cereals in your farming cycle.")
        
        elif message_type == 'reminders':
            message = ("🔔 *Service Reminder*\n\n"
                      "Don't forget to schedule your produce transport before the weekend. "
                      "Early booking gets you preferential rates. "
                      "Reply 'RATES' for current pricing.")
        
        else:
            message = ("👋 *Personalized Message*\n\n"
                      "Thank you for being a valued customer. "
                      "How can we assist you today? "
                      "Reply with your request or 'MENU' for options.")
        
        return message