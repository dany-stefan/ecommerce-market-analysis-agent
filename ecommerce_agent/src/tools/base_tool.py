"""
Base Tool Interface
Simple abstract class that all tools inherit from.

MOCK API vs REAL API INTEGRATION APPROACH:
==========================================

MOCK/SIMULATED DATA APPROACH (Current Implementation):
- All tools use simulated data generation for demonstrations
- No external API calls or dependencies required
- Deterministic and reproducible results for testing
- Fast execution without network latency
- No API keys, rate limits, or costs

REAL API INTEGRATION ALTERNATIVE:
If connecting to actual e-commerce APIs (Amazon, eBay, etc.), tools would:

1. API Client Initialization:
   # Real API Approach
   import requests
   from amazon_api import AmazonProductAPI
   
   class ProductCollectorTool(BaseTool):
       def __init__(self, api_key: str, api_secret: str):
           self.api_client = AmazonProductAPI(api_key, api_secret)
           self.session = requests.Session()
   
   # Mock Approach (Current)
   class ProductCollectorTool(BaseTool):
       def __init__(self, use_mock_data: bool = True):
           self.use_mock_data = use_mock_data
           # No API client needed

2. Data Fetching:
   # Real API Approach
   def execute(self, input_data):
       response = self.api_client.search_products(
           keywords=input_data.product_query,
           marketplace='US',
           max_results=10
       )
       products = response.json()['products']
   
   # Mock Approach (Current)
   def execute(self, input_data):
       products = MockDataGenerator.generate_product_data(
           product_query=input_data.product_query,
           realistic=True
       )

3. Error Handling:
   # Real API Approach
   try:
       response = api_client.get_product(asin=product_id)
       if response.status_code == 429:  # Rate limit
           time.sleep(60)
           response = api_client.get_product(asin=product_id)
   except requests.exceptions.RequestException as e:
       logger.error(f"API call failed: {e}")
       fallback_data = load_cached_data()
   
   # Mock Approach (Current)
   # No rate limits, timeouts, or network errors to handle
   data = generate_mock_data()  # Always succeeds

4. Authentication & Configuration:
   # Real API Approach
   # .env file:
   AMAZON_API_KEY=your_key_here
   AMAZON_SECRET=your_secret_here
   EBAY_API_TOKEN=your_token_here
   WALMART_CLIENT_ID=your_client_here
   
   # Mock Approach (Current)
   # No credentials needed - just configuration flags
   use_mock_data=True

5. Cost & Performance:
   # Real API Approach
   - Per-request costs ($0.001-$0.01 per call)
   - Rate limits (e.g., 1 request/second)
   - Network latency (200-500ms per call)
   - Requires retry logic and backoff
   
   # Mock Approach (Current)
   - Zero cost
   - No rate limits
   - Instant execution (<10ms)
   - No retry logic needed

DESIGN RATIONALE for Mock Approach:
===================================
1. Development Speed: No API registration or approval wait times
2. Testing: Deterministic results enable reliable unit tests
3. Demonstrations: Works offline and in sandboxed environments
4. Cost Control: No surprise API bills during development
5. Reproducibility: Same input always produces same output

TRANSITION PATH to Real APIs:
============================
To switch from mock to real APIs:

1. Keep the same tool interface (execute method signature unchanged)
2. Add API client initialization in __init__
3. Replace mock data generators with actual API calls
4. Add error handling for network issues, rate limits
5. Implement caching to reduce API costs
6. Add retry logic with exponential backoff
7. Use configuration flags to toggle between mock/real:
   
   tool = SentimentAnalyzerTool(use_mock=False, api_key='...')

The tool interface remains identical, making the transition seamless.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel


class ToolInput(BaseModel):
    """Base class for tool inputs - ensures consistent data structure"""
    pass


class ToolOutput(BaseModel):
    """Base class for tool outputs - ensures consistent data structure"""
    success: bool
    data: Dict[str, Any]
    error: str = ""


class BaseTool(ABC):
    """
    Abstract base class for all tools.
    
    Design Decision: Keep it simple - each tool has:
    - A name (for identification)
    - A description (for the agent to understand what it does)
    - An execute method (the actual work)
    """
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @property
    @abstractmethod
    def description(self) -> str:
        """What does this tool do? Used by agent for decision making."""
        pass
    
    @abstractmethod
    def execute(self, input_data: ToolInput) -> ToolOutput:
        """
        Execute the tool's functionality.
        
        Args:
            input_data: Validated input data
            
        Returns:
            ToolOutput with success status and results
        """
        pass
    
    def run(self, input_data: ToolInput) -> ToolOutput:
        """
        Public method to run the tool with error handling.
        """
        try:
            return self.execute(input_data)
        except Exception as e:
            return ToolOutput(
                success=False,
                data={},
                error=f"Tool {self.name} failed: {str(e)}"
            )
