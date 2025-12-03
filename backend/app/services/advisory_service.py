"""
Advisory Service for crop and farming advice
"""
from typing import Optional
from app.models.user import User


class AdvisoryService:
    """
    Advisory service that provides crop and farming-related advice
    """
    
    def __init__(self):
        # Initialize with common crop advice database
        self.crop_advice_db = {
            'maize': {
                'planting': 'Plant maize during the rainy season with spacing of 75cm x 25cm. Use 18-6-12 or 15-15-15 fertilizer at planting.',
                'pests': 'Common pests include stem borers and fall armyworm. Use appropriate insecticides and crop rotation.',
                'harvesting': 'Harvest when cobs are fully developed and kernels are in the dough stage, typically 90-120 days after planting.'
            },
            'rice': {
                'planting': 'Prepare well-leveled fields with proper water management. Transplant seedlings at 20x20cm spacing.',
                'pests': 'Watch for brown planthopper and rice stem borer. Maintain proper water levels to reduce pest pressure.',
                'harvesting': 'Harvest when 80-85% of grains have turned golden yellow, typically 3-6 months after transplanting.'
            },
            'cassava': {
                'planting': 'Plant during early rainy season. Use healthy stem cuttings at 1x1m spacing in well-drained soil.',
                'pests': 'Major pests include cassava mosaic disease and green mites. Use disease-free planting materials.',
                'harvesting': 'Harvest 8-12 months after planting when leaves begin to yellow. Roots can remain in ground for up to 24 months.'
            }
        }
    
    def get_crop_advice(self, crop_query: str, user: Optional[User] = None):
        """
        Provide crop-specific advice based on user query
        """
        crop_query_lower = crop_query.lower().strip()
        
        # Identify crop from query
        crop = self._identify_crop_from_query(crop_query_lower)
        
        if crop:
            advice = self.crop_advice_db.get(crop, {})
            if advice:
                response = f"🌾 *{crop.title()} Advisory*\n\n"
                
                if 'planting' in crop_query_lower or 'plant' in crop_query_lower:
                    response += f"🌱 *Planting Tips:*\n{advice.get('planting', 'No specific planting advice available.')}\n\n"
                elif 'pest' in crop_query_lower or 'disease' in crop_query_lower or 'pests' in crop_query_lower:
                    response += f"🪲 *Pest Management:*\n{advice.get('pests', 'No specific pest management advice available.')}\n\n"
                elif 'harvest' in crop_query_lower or 'harvesting' in crop_query_lower:
                    response += f" reap *Harvesting Tips:*\n{advice.get('harvesting', 'No specific harvesting advice available.')}\n\n"
                else:
                    # Provide all advice if no specific category is requested
                    response += f"🌱 *Planting Tips:*\n{advice.get('planting', 'No planting advice available.')}\n\n"
                    response += f"🪲 *Pest Management:*\n{advice.get('pests', 'No pest management advice available.')}\n\n"
                    response += f" reap *Harvesting Tips:*\n{advice.get('harvesting', 'No harvesting advice available.')}\n\n"
                
                response += "For more specific advice, please provide details about your farming conditions."
                return response
            else:
                return f"Sorry, I don't have specific advice for {crop}. Try asking about maize, rice, or cassava."
        else:
            return "I can provide advice for specific crops like maize, rice, or cassava. Please specify which crop you need advice for."
    
    def _identify_crop_from_query(self, query: str):
        """
        Identify crop from user query
        """
        if any(crop in query for crop in ['maize', 'corn']):
            return 'maize'
        elif any(crop in query for crop in ['rice', 'paddy']):
            return 'rice'
        elif any(crop in query for crop in ['cassava', 'gari', 'tapioca']):
            return 'cassava'
        else:
            return None
    
    def get_general_advice(self, topic: str, user: Optional[User] = None):
        """
        Provide general farming advice on various topics
        """
        topic_lower = topic.lower().strip()
        
        if 'soil' in topic_lower or 'fertilizer' in topic_lower:
            return ("For soil health, test your soil pH and nutrient levels before planting. "
                   "Apply organic manure and balanced NPK fertilizers based on crop requirements. "
                   "Practice crop rotation to maintain soil fertility.")
        
        elif 'weather' in topic_lower or 'rain' in topic_lower:
            return ("Monitor weather patterns for optimal planting times. "
                   "Ensure proper drainage to prevent waterlogging during heavy rains. "
                   "Consider drought-resistant varieties if rainfall is insufficient.")
        
        elif 'market' in topic_lower or 'price' in topic_lower:
            return ("To get better prices, consider collective marketing with other farmers. "
                   "Harvest and sell when demand is high and supply is low. "
                   "Maintain quality to command premium prices.")
        
        else:
            return ("I can provide advice on soil management, weather considerations, and market strategies. "
                   "For crop-specific advice, please mention the crop name in your query.")