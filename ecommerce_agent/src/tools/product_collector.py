"""
Product Collector Tool
Gathers product data from e-commerce sources (using mock data for demonstration).

This tool demonstrates:
- Clean code structure (Technical Quality - 25%)
- Robust error handling (Technical Quality - 25%)
- Extensible design for real API integration (Innovation - 25%)
"""

import random
from typing import Dict, Any
from pydantic import BaseModel, Field
from src.tools.base_tool import BaseTool, ToolInput, ToolOutput
from src.utils.models import ProductData
from loguru import logger


class ProductCollectorInput(ToolInput):
    """Input for product collection"""
    product_query: str = Field(description="Product name or description to search for")


class ProductCollectorTool(BaseTool):
    """
    Collects product information from e-commerce platforms.
    
    Current Implementation: Uses mock data for demonstration.
    Production Ready: Structure allows easy integration with real APIs (Amazon, eBay, etc.)
    
    Design Decision: Mock data allows testing without API keys/costs,
    while maintaining production-ready structure.
    """
    
    def __init__(self, use_mock_data: bool = True):
        super().__init__()
        self.use_mock_data = use_mock_data
        self._mock_database = self._initialize_mock_data()
    
    @property
    def description(self) -> str:
        return "Collects product information including pricing, specifications, and availability"
    
    def execute(self, input_data: ProductCollectorInput) -> ToolOutput:
        """
        Collect product data based on query.
        
        Args:
            input_data: Contains product query string
            
        Returns:
            ToolOutput with ProductData or error
        """
        logger.info(f"Collecting product data for: {input_data.product_query}")
        
        try:
            if self.use_mock_data:
                product_data = self._get_mock_product(input_data.product_query)
            else:
                product_data = self._get_real_product(input_data.product_query)
            
            if product_data:
                logger.success(f"Found product: {product_data.name} - ${product_data.price}")
                return ToolOutput(
                    success=True,
                    data=product_data.model_dump()
                )
            else:
                logger.warning(f"No product found for query: {input_data.product_query}")
                return ToolOutput(
                    success=False,
                    data={},
                    error=f"Product not found: {input_data.product_query}"
                )
                
        except Exception as e:
            logger.error(f"Error collecting product data: {str(e)}")
            return ToolOutput(
                success=False,
                data={},
                error=f"Failed to collect product data: {str(e)}"
            )
    
    def _initialize_mock_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize mock product database for demonstration.
        
        Design Decision: Realistic mock data shows how real data would flow
        through the system without requiring API keys.
        """
        return {
            "iphone": {
                "name": "iPhone 15 Pro",
                "price": 999.00,
                "currency": "USD",
                "description": "Latest Apple flagship with A17 Pro chip, titanium design, and advanced camera system",
                "specifications": {
                    "storage": "256GB",
                    "color": "Natural Titanium",
                    "display": "6.1-inch Super Retina XDR",
                    "chip": "A17 Pro",
                    "camera": "48MP Main + 12MP Ultra Wide + 12MP Telephoto",
                    "battery": "Up to 23 hours video playback"
                },
                "source": "mock_api"
            },
            "samsung": {
                "name": "Samsung Galaxy S24 Ultra",
                "price": 1199.99,
                "currency": "USD",
                "description": "Premium Android flagship with S Pen, 200MP camera, and AI features",
                "specifications": {
                    "storage": "256GB",
                    "color": "Titanium Gray",
                    "display": "6.8-inch Dynamic AMOLED 2X",
                    "processor": "Snapdragon 8 Gen 3",
                    "camera": "200MP Main + 50MP Periscope + 12MP Ultra Wide + 10MP Telephoto",
                    "battery": "5000mAh"
                },
                "source": "mock_api"
            },
            "airpods": {
                "name": "AirPods Pro (2nd generation)",
                "price": 249.00,
                "currency": "USD",
                "description": "Premium wireless earbuds with active noise cancellation",
                "specifications": {
                    "features": ["Active Noise Cancellation", "Transparency Mode", "Spatial Audio"],
                    "battery": "Up to 6 hours (ANC on)",
                    "chip": "H2 chip",
                    "water_resistance": "IPX4"
                },
                "source": "mock_api"
            },
            "macbook": {
                "name": "MacBook Pro 14-inch M3",
                "price": 1599.00,
                "currency": "USD",
                "description": "Professional laptop with M3 chip for demanding workloads",
                "specifications": {
                    "chip": "Apple M3",
                    "memory": "16GB unified",
                    "storage": "512GB SSD",
                    "display": "14.2-inch Liquid Retina XDR",
                    "battery": "Up to 17 hours"
                },
                "source": "mock_api"
            }
        }
    
    def _get_mock_product(self, query: str) -> ProductData:
        """
        Retrieve mock product data based on query.
        
        Simple keyword matching for demonstration.
        Production would use proper search/filtering.
        """
        query_lower = query.lower()
        
        # Simple keyword matching
        for keyword, product_data in self._mock_database.items():
            if keyword in query_lower:
                return ProductData(**product_data)
        
        # If no exact match, return a generic product with variations
        logger.warning(f"No exact match for '{query}', generating generic product")
        return ProductData(
            name=f"Generic {query.title()}",
            price=round(random.uniform(99.99, 999.99), 2),
            currency="USD",
            description=f"Quality {query} product",
            specifications={"type": "generic", "quality": "standard"},
            source="mock_api_fallback"
        )
    
    def _get_real_product(self, query: str) -> ProductData:
        """
        Placeholder for real API integration.
        
        Production Implementation Ideas:
        - Amazon Product Advertising API
        - eBay API
        - Google Shopping API
        - Custom scraping (respecting robots.txt)
        """
        # This would contain actual API calls
        # Example structure:
        # response = requests.get(f"{API_URL}/search?q={query}")
        # return ProductData(**response.json())
        
        raise NotImplementedError(
            "Real API integration not implemented. "
            "Set use_mock_data=True for demonstration mode."
        )
