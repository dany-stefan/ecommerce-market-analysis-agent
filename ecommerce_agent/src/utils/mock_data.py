"""
Mock data generator for demonstrations.
Provides realistic mock data without requiring external APIs.
"""

from typing import List, Dict
import random


class MockReviewsGenerator:
    """
    Generates realistic mock reviews for testing sentiment analysis.
    
    Design Decision: Realistic mock data allows:
    - Testing without API dependencies
    - Consistent reproducible results
    - Demonstration of full pipeline
    """
    
    IPHONE_REVIEWS = [
        "The camera quality is absolutely amazing! Best phone I've ever owned. Battery lasts all day.",
        "Great phone but very expensive. The titanium design feels premium though.",
        "Love the new Action button, makes it so easy to launch camera quickly.",
        "Battery life could be better. Otherwise solid phone with excellent performance.",
        "The A17 Pro chip is incredibly fast. Gaming experience is smooth.",
        "Disappointed with the price increase. Good phone but not worth the premium.",
        "Perfect upgrade from my iPhone 12. The camera improvements are noticeable.",
        "Best display I've seen on a phone. Colors are vibrant and accurate."
    ]
    
    SAMSUNG_REVIEWS = [
        "The S Pen is a game changer! Great for note taking and drawing.",
        "200MP camera takes stunning photos. AI features are genuinely useful.",
        "Battery life is excellent, easily lasts a full day with heavy use.",
        "A bit pricey but you get what you pay for. Premium build quality.",
        "The screen is gorgeous. Best display on any smartphone.",
        "Software can feel bloated at times, but overall performance is great.",
        "Love the customization options. Much more flexible than other phones.",
        "Camera zoom capabilities are insane. Can see details from far away."
    ]
    
    AIRPODS_REVIEWS = [
        "Noise cancellation is impressive. Great for travel and commuting.",
        "Sound quality is good but not audiophile level. Convenient though.",
        "Battery life is decent. The case provides plenty of extra charges.",
        "Very comfortable to wear for extended periods. Lightweight design.",
        "Expensive for earbuds but the ecosystem integration with iPhone is seamless.",
        "Transparency mode works well. Can hear surroundings when needed.",
        "Spatial audio is a nice feature for movies and music.",
        "Fit could be better. They sometimes feel loose during exercise."
    ]
    
    MACBOOK_REVIEWS = [
        "The M3 chip is blazing fast. Renders videos in no time.",
        "Battery life is incredible. Can work all day without charging.",
        "The display is stunning. Perfect for photo and video editing.",
        "Expensive but worth it for professionals. Build quality is top-notch.",
        "Fanless design means completely silent operation. Amazing.",
        "Keyboard and trackpad are the best I've used on any laptop.",
        "Ports could be more plentiful. Had to buy adapters.",
        "Best laptop for developers. macOS and the hardware work perfectly together."
    ]
    
    GENERIC_POSITIVE = [
        "Excellent product! Exceeded my expectations in every way.",
        "Great quality and value for money. Highly recommended.",
        "Very satisfied with this purchase. Does exactly what I needed.",
        "Outstanding performance and build quality. Worth every penny.",
        "Best in its category. Would definitely buy again."
    ]
    
    GENERIC_NEGATIVE = [
        "Disappointed with the quality. Not worth the price.",
        "Poor build quality. Started having issues after a few weeks.",
        "Customer service was unhelpful when I had problems.",
        "Overpriced for what you get. Many better alternatives available.",
        "Would not recommend. Save your money for something better."
    ]
    
    @classmethod
    def get_reviews_for_product(cls, product_query: str, count: int = 5) -> List[str]:
        """
        Get mock reviews for a product based on query.
        
        Args:
            product_query: Product name or description
            count: Number of reviews to return
            
        Returns:
            List of review strings
        """
        query_lower = product_query.lower()
        
        # Match to appropriate review set
        if "iphone" in query_lower:
            reviews = cls.IPHONE_REVIEWS
        elif "samsung" in query_lower or "galaxy" in query_lower:
            reviews = cls.SAMSUNG_REVIEWS
        elif "airpods" in query_lower or "earbuds" in query_lower:
            reviews = cls.AIRPODS_REVIEWS
        elif "macbook" in query_lower or "laptop" in query_lower:
            reviews = cls.MACBOOK_REVIEWS
        else:
            # Mix of positive and negative for generic products
            reviews = cls.GENERIC_POSITIVE + cls.GENERIC_NEGATIVE
        
        # Return random sample
        return random.sample(reviews, min(count, len(reviews)))


class MockCompetitorGenerator:
    """Generates mock competitor data for demonstration."""
    
    SMARTPHONE_COMPETITORS = [
        {
            "competitor_name": "Google",
            "product_name": "Pixel 8 Pro",
            "price": 999.00,
            "market_position": "premium",
            "key_features": ["AI features", "Great camera", "Clean Android", "7 years updates"]
        },
        {
            "competitor_name": "OnePlus",
            "product_name": "OnePlus 12",
            "price": 799.00,
            "market_position": "mid-range",
            "key_features": ["Fast charging", "Good value", "Powerful processor"]
        }
    ]
    
    LAPTOP_COMPETITORS = [
        {
            "competitor_name": "Dell",
            "product_name": "XPS 15",
            "price": 1699.00,
            "market_position": "premium",
            "key_features": ["OLED display", "Powerful specs", "Windows ecosystem"]
        },
        {
            "competitor_name": "Lenovo",
            "product_name": "ThinkPad X1 Carbon",
            "price": 1499.00,
            "market_position": "business",
            "key_features": ["Durable build", "Great keyboard", "Business features"]
        }
    ]
    
    @classmethod
    def get_competitors_for_product(cls, product_query: str) -> List[Dict]:
        """Get mock competitor data based on product."""
        query_lower = product_query.lower()
        
        if any(word in query_lower for word in ["phone", "iphone", "samsung", "smartphone"]):
            return cls.SMARTPHONE_COMPETITORS
        elif any(word in query_lower for word in ["laptop", "macbook", "computer"]):
            return cls.LAPTOP_COMPETITORS
        else:
            # Generic competitors
            return [
                {
                    "competitor_name": "Competitor A",
                    "product_name": f"Alternative {product_query}",
                    "price": random.uniform(299, 1299),
                    "market_position": "mid-range",
                    "key_features": ["Good value", "Reliable", "Popular choice"]
                }
            ]
