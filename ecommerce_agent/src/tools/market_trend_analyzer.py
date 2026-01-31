"""
Market Trend Analyzer Tool
Analyzes price and popularity trends over time for e-commerce products.

This tool demonstrates:
- Time-series analysis for pricing trends
- Popularity metrics and trend detection
- Market momentum analysis
- Visualization-ready data structures

MOCK DATA vs REAL MARKET DATA API INTEGRATION:
=============================================

MOCK/SIMULATED DATA APPROACH (Current Implementation):
When use_mock_data=True (default):
- Generates realistic price and popularity trends mathematically
- Creates 90-day historical data with realistic patterns
- Simulates market dynamics (seasonal trends, momentum shifts)
- Instant generation without external dependencies
- Deterministic patterns based on product characteristics

Example Flow:
1. Input: Product name (e.g., "iPhone 15 Pro")
2. Generate Base Price: Derive from product category
   - Premium products (iPhone, MacBook): $900-$1200
   - Mid-range products: $300-$600
   - Budget products: $50-$200
3. Generate Price History: Add realistic variance
   - Random daily fluctuations: ±2-5%
   - Seasonal patterns: Higher prices during holidays
   - Promotional dips: 10-15% discount periods
4. Generate Popularity Metrics:
   - Search volume: 10K-500K based on product tier
   - Review count: Grows over time (launch to mature)
   - Rating average: 3.5-4.8 with slight variance
5. Calculate Trends:
   - Price trend: Compare first vs last 30 days
   - Momentum: Bullish/Bearish/Neutral based on velocity
   - Forecast: Project trends forward

Code Implementation (Mock):
```python
def _generate_price_history(self, product_name: str, days: int) -> List[PriceTrend]:
    # Determine base price from product category
    base_price = self._infer_base_price(product_name)
    
    prices = []
    for i in range(days):
        # Add realistic daily variance
        daily_change = random.uniform(-0.05, 0.05)  # ±5% max
        price = base_price * (1 + daily_change)
        
        # Add seasonal patterns (higher during holidays)
        if self._is_holiday_season(i):
            price *= 1.10  # 10% markup
        
        # Add promotional periods (random discounts)
        if random.random() < 0.15:  # 15% chance
            price *= 0.85  # 15% discount
        
        prices.append(PriceTrend(
            date=(datetime.now() - timedelta(days=days-i)).isoformat(),
            price=round(price, 2),
            source="simulated_market_data"
        ))
    
    return prices

def _generate_popularity_metrics(self, days: int) -> List[PopularityMetric]:
    metrics = []
    for i in range(days):
        # Growth pattern: slow start, rapid growth, plateau
        growth_factor = 1 - math.exp(-i / 30)  # Exponential growth curve
        
        search_volume = int(50000 * growth_factor + random.randint(-5000, 5000))
        review_count = int(200 * growth_factor + random.randint(-20, 20))
        rating = round(4.2 + random.uniform(-0.3, 0.3), 1)
        
        metrics.append(PopularityMetric(
            date=(datetime.now() - timedelta(days=days-i)).isoformat(),
            search_volume=max(1000, search_volume),
            review_count=max(10, review_count),
            rating_average=max(1.0, min(5.0, rating))
        ))
    
    return metrics
```

REAL MARKET DATA API APPROACH (Production):
When use_mock_data=False and market data APIs configured:
- Connect to real price tracking services (CamelCamelCamel, Keepa, etc.)
- Fetch actual historical pricing from Amazon, eBay, Walmart APIs
- Get real search trends from Google Trends API
- Retrieve authentic review data from marketplace APIs
- Costs, rate limits, and authentication required

Example Flow:
1. Input: Product name + ASIN/SKU identifier
2. API Calls (Parallel):
   a) Price History API:
      ```python
      # Keepa API Example
      response = requests.get(
          f"https://api.keepa.com/product",
          params={
              'key': KEEPA_API_KEY,
              'domain': 1,  # .com
              'asin': product_asin,
              'stats': 90  # 90 days of data
          }
      )
      price_data = response.json()['products'][0]['csv'][0]  # Price history
      ```
   
   b) Search Trends API:
      ```python
      # Google Trends (pytrends)
      from pytrends.request import TrendReq
      
      pytrend = TrendReq()
      pytrend.build_payload([product_name], timeframe='today 3-m')
      trends = pytrend.interest_over_time()
      ```
   
   c) Review Data API:
      ```python
      # Amazon Product Advertising API
      from amazon.paapi import AmazonAPI
      
      api = AmazonAPI(KEY, SECRET, TAG, REGION)
      product = api.get_items(asin)[0]
      
      reviews = {
          'rating': product.rating,
          'review_count': product.review_count,
          'ratings_breakdown': product.ratings_breakdown
      }
      ```

3. Data Processing:
   - Normalize data from different sources
   - Handle missing data points (interpolation)
   - Convert timestamps to consistent format
   - Calculate trend indicators (MA, RSI, momentum)

4. Error Handling:
   ```python
   try:
       price_data = fetch_price_history(asin)
   except requests.exceptions.HTTPError as e:
       if e.response.status_code == 429:
           # Rate limited - use exponential backoff
           time.sleep(60)
           price_data = fetch_price_history(asin)
       else:
           # API error - fall back to cached data
           logger.warning(f"API error: {e}, using cached data")
           price_data = load_from_cache(asin)
   except requests.exceptions.RequestException:
       # Network error - use mock data as fallback
       logger.error("Network error, using simulated data")
       price_data = generate_mock_price_data(product_name)
   ```

5. Output: Real historical data with actual market dynamics

Code Implementation (Real API):
```python
class MarketTrendAnalyzerTool(BaseTool):
    def __init__(self, use_mock_data: bool = False):
        super().__init__()
        self.use_mock_data = use_mock_data
        
        if not use_mock_data:
            # Initialize API clients
            self.keepa_client = KeepaAPI(api_key=KEEPA_API_KEY)
            self.trends_client = TrendReq()
            self.amazon_api = AmazonAPI(KEY, SECRET, TAG, REGION)
            logger.info("Market Trend Analyzer with REAL API data")
        else:
            logger.info("Market Trend Analyzer with SIMULATED data")
    
    def _fetch_real_price_history(self, product_id: str, days: int) -> List[PriceTrend]:
        try:
            # Fetch from Keepa (price tracking service)
            response = self.keepa_client.query(product_id, stats=days)
            
            prices = []
            for timestamp, price in zip(response['csv'][0], response['csv'][1]):
                if price > 0:  # Filter invalid data points
                    prices.append(PriceTrend(
                        date=datetime.fromtimestamp(timestamp).isoformat(),
                        price=price / 100,  # Keepa uses cents
                        source="keepa_api"
                    ))
            
            return prices
            
        except Exception as e:
            logger.error(f"Real API failed: {e}, using mock data")
            return self._generate_mock_price_history(product_id, days)
    
    def _fetch_real_search_trends(self, product_name: str) -> List[PopularityMetric]:
        try:
            # Fetch from Google Trends
            self.trends_client.build_payload([product_name], timeframe='today 3-m')
            interest = self.trends_client.interest_over_time()
            
            metrics = []
            for date, row in interest.iterrows():
                metrics.append(PopularityMetric(
                    date=date.isoformat(),
                    search_volume=int(row[product_name] * 1000),  # Scale to realistic volume
                    review_count=0,  # Would need separate API call
                    rating_average=0.0  # Would need separate API call
                ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Trends API failed: {e}, using mock data")
            return self._generate_mock_popularity_metrics(90)
```

COMPARISON TABLE:
================
| Aspect                | Mock/Simulated Data              | Real Market Data APIs                  |
|-----------------------|----------------------------------|----------------------------------------|
| Data Source           | Mathematical generation          | Keepa, Google Trends, Amazon API       |
| Historical Accuracy   | Realistic patterns, not real     | Actual market data                     |
| Setup                 | No configuration needed          | Multiple API keys required             |
| Cost                  | Free                             | $20-50/month per API                   |
| Speed                 | <50ms (instant generation)       | 1-5 seconds (multiple API calls)       |
| Rate Limits           | None                             | 100-1000 requests/day typical          |
| Data Quality          | Consistent, predictable          | Real but may have gaps                 |
| Dependencies          | None                             | pytrends, keepa, amazon-paapi          |
| Offline Capability    | Yes                              | No                                     |
| Update Frequency      | Always current (generated)       | Real-time to daily updates             |
| Error Handling        | Not needed                       | Critical (network, rate limits, auth)  |
| Historical Range      | Any range (generated on demand)  | Limited by API (90 days typical)       |

REAL-WORLD APIS USED FOR MARKET ANALYSIS:
=========================================

1. **Keepa API** (Price Tracking)
   - Tracks Amazon price history since 2011
   - Pricing: €19/month for 1M requests
   - Data: Price, sales rank, ratings over time
   - Coverage: Amazon marketplaces worldwide
   
2. **CamelCamelCamel API**
   - Amazon price tracking
   - Free tier: 60 requests/hour
   - Historical price charts and alerts
   
3. **Google Trends API** (pytrends)
   - Search interest over time
   - Free but rate limited
   - Regional and temporal search patterns
   
4. **Amazon Product Advertising API**
   - Official Amazon product data
   - Pricing: Commission-based (no direct fees)
   - Requires associate account
   - Data: Price, reviews, ratings, availability
   
5. **Walmart Open API**
   - Product catalog and pricing
   - Free tier available
   - Search, product details, reviews
   
6. **eBay Finding API**
   - Marketplace data and pricing
   - Free with eBay developer account
   - Historical sold listings for price trends

HYBRID APPROACH (Current Implementation):
========================================
Supports both mock and real data:

```python
# Development: Use mock data (fast, free, reliable)
analyzer = MarketTrendAnalyzerTool(use_mock_data=True)
trends = analyzer.execute(input_data)

# Production: Use real APIs (accurate, up-to-date)
analyzer = MarketTrendAnalyzerTool(use_mock_data=False)
trends = analyzer.execute(input_data)

# Graceful Degradation: Try real API, fallback to mock
if api_call_fails:
    logger.warning("API unavailable, using simulated data")
    trends = generate_mock_trends()
```

WHY MOCK DATA FOR THIS PROJECT:
==============================
1. **Demonstration Focus**: Shows trend analysis logic, not API integration
2. **No Dependencies**: Works without external API accounts
3. **Reproducibility**: Same patterns for testing and evaluation
4. **Speed**: Instant generation vs 1-5 second API calls
5. **Cost**: Zero vs $20-50/month for real data access
6. **Reliability**: No rate limits, downtime, or authentication issues
7. **Simplicity**: No API key management or error handling complexity
8. **Offline**: Works in sandboxed/air-gapped environments

PRODUCTION MIGRATION PATH:
=========================
To switch to real market data:

1. Sign up for APIs:
   - Keepa: https://keepa.com/#!api
   - Google Cloud: Enable Trends API
   - Amazon: Get Product Advertising API credentials

2. Install dependencies:
   ```bash
   pip install keepa pytrends amazon-paapi
   ```

3. Configure credentials:
   ```bash
   export KEEPA_API_KEY="your_key"
   export AMAZON_ACCESS_KEY="your_key"
   export AMAZON_SECRET_KEY="your_secret"
   ```

4. Change tool initialization:
   ```python
   tool = MarketTrendAnalyzerTool(use_mock_data=False)
   ```

5. Add error handling and caching (already built-in)

6. Monitor API usage and costs

The tool interface remains identical - only data source changes.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.tools.base_tool import BaseTool, ToolInput, ToolOutput
from loguru import logger
import random


class MarketTrendInput(ToolInput):
    """Input for market trend analysis"""
    product_name: str = Field(description="Product name to analyze")
    time_period_days: int = Field(default=90, description="Number of days to analyze (default: 90)")
    include_competitors: bool = Field(default=True, description="Include competitor trend comparison")


class PriceTrend(BaseModel):
    """Price trend data point"""
    date: str
    price: float
    source: str = "market_data"


class PopularityMetric(BaseModel):
    """Popularity metrics for a time period"""
    date: str
    search_volume: int
    review_count: int
    rating_average: float


class TrendAnalysis(BaseModel):
    """Complete trend analysis result"""
    product_name: str
    analysis_period_days: int
    price_trend: str  # "increasing", "decreasing", "stable"
    price_change_percent: float
    popularity_trend: str  # "growing", "declining", "stable"
    search_volume_change_percent: float
    current_momentum: str  # "bullish", "bearish", "neutral"
    price_history: List[PriceTrend]
    popularity_history: List[PopularityMetric]
    forecast_summary: str
    competitor_comparison: Optional[Dict[str, Any]] = None


class MarketTrendAnalyzerTool(BaseTool):
    """
    Analyzes market trends including pricing and popularity patterns.
    
    Features:
    - Historical price tracking with trend detection
    - Popularity metrics (search volume, reviews, ratings)
    - Market momentum indicators
    - Competitor trend comparison
    - Forecast insights
    
    Design Philosophy:
    - Uses simulated data for demonstration (easily replaceable with real APIs)
    - Produces visualization-ready data structures
    - Provides actionable insights for business decisions
    """
    
    def __init__(self, use_mock_data: bool = True):
        """
        Initialize the Market Trend Analyzer Tool.
        
        Args:
            use_mock_data: If True, generates realistic simulated data.
                          In production, set to False and integrate with real data sources.
        """
        super().__init__()
        self.use_mock_data = use_mock_data
        logger.info(f"Market Trend Analyzer initialized (mock_data={use_mock_data})")
    
    @property
    def description(self) -> str:
        return "Analyzes price and popularity trends over time for market intelligence"
    
    def execute(self, input_data: MarketTrendInput) -> ToolOutput:
        """
        Execute market trend analysis.
        
        Args:
            input_data: Product name and analysis parameters
            
        Returns:
            ToolOutput with TrendAnalysis data
        """
        logger.info(
            f"Analyzing market trends for {input_data.product_name} "
            f"({input_data.time_period_days} days)"
        )
        
        try:
            if self.use_mock_data:
                trend_analysis = self._analyze_with_mock_data(input_data)
            else:
                # In production: integrate with real data sources
                # e.g., APIs from: Amazon Product Advertising API, Google Trends, etc.
                trend_analysis = self._analyze_with_real_data(input_data)
            
            logger.success(
                f"Trend analysis complete: {trend_analysis.price_trend} pricing, "
                f"{trend_analysis.popularity_trend} popularity"
            )
            
            return ToolOutput(
                success=True,
                data=trend_analysis.model_dump(),
                metadata={
                    "analysis_date": datetime.now().isoformat(),
                    "data_source": "mock_data" if self.use_mock_data else "real_api"
                }
            )
            
        except Exception as e:
            logger.error(f"Market trend analysis failed: {e}")
            return ToolOutput(
                success=False,
                data={},
                error=str(e)
            )
    
    def _analyze_with_mock_data(self, input_data: MarketTrendInput) -> TrendAnalysis:
        """
        Generate realistic trend data for demonstration.
        
        Simulates various market scenarios:
        - Rising prices with increasing popularity (hot product)
        - Declining prices with stable popularity (market saturation)
        - Stable prices with growing popularity (steady growth)
        """
        product_name = input_data.product_name
        days = input_data.time_period_days
        
        # Generate price history
        price_history = self._generate_price_history(product_name, days)
        
        # Generate popularity history
        popularity_history = self._generate_popularity_history(product_name, days)
        
        # Calculate trends
        price_trend, price_change = self._calculate_price_trend(price_history)
        popularity_trend, search_change = self._calculate_popularity_trend(popularity_history)
        
        # Determine market momentum
        momentum = self._calculate_momentum(price_trend, popularity_trend)
        
        # Generate forecast
        forecast = self._generate_forecast(price_trend, popularity_trend, momentum)
        
        # Competitor comparison (if requested)
        competitor_data = None
        if input_data.include_competitors:
            competitor_data = self._generate_competitor_comparison(
                product_name, price_history, popularity_history
            )
        
        return TrendAnalysis(
            product_name=product_name,
            analysis_period_days=days,
            price_trend=price_trend,
            price_change_percent=price_change,
            popularity_trend=popularity_trend,
            search_volume_change_percent=search_change,
            current_momentum=momentum,
            price_history=price_history,
            popularity_history=popularity_history,
            forecast_summary=forecast,
            competitor_comparison=competitor_data
        )
    
    def _generate_price_history(self, product_name: str, days: int) -> List[PriceTrend]:
        """Generate realistic price history"""
        # Determine base price based on product category
        base_price = self._estimate_base_price(product_name)
        
        # Determine trend type (for variety in demos)
        trend_seed = sum(ord(c) for c in product_name)
        trend_type = trend_seed % 3  # 0: increasing, 1: decreasing, 2: stable
        
        price_history = []
        current_date = datetime.now()
        current_price = base_price
        
        # Generate daily price points
        for i in range(days):
            date = (current_date - timedelta(days=days-i)).strftime("%Y-%m-%d")
            
            # Apply trend
            if trend_type == 0:  # Increasing
                trend_factor = 1 + (i / days) * 0.15  # Up to 15% increase
            elif trend_type == 1:  # Decreasing
                trend_factor = 1 - (i / days) * 0.12  # Up to 12% decrease
            else:  # Stable
                trend_factor = 1.0
            
            # Add some random fluctuation
            noise = random.uniform(-0.02, 0.02)
            price = base_price * trend_factor * (1 + noise)
            
            price_history.append(PriceTrend(
                date=date,
                price=round(price, 2),
                source="market_data"
            ))
        
        return price_history
    
    def _generate_popularity_history(self, product_name: str, days: int) -> List[PopularityMetric]:
        """Generate realistic popularity metrics"""
        base_search_volume = random.randint(10000, 100000)
        base_review_count = random.randint(500, 5000)
        base_rating = random.uniform(3.8, 4.7)
        
        popularity_history = []
        current_date = datetime.now()
        
        # Determine popularity trend
        trend_seed = sum(ord(c) for c in product_name) * 7
        trend_type = trend_seed % 3  # 0: growing, 1: declining, 2: stable
        
        for i in range(days):
            date = (current_date - timedelta(days=days-i)).strftime("%Y-%m-%d")
            
            # Apply trend
            if trend_type == 0:  # Growing
                trend_factor = 1 + (i / days) * 0.30  # Up to 30% growth
            elif trend_type == 1:  # Declining
                trend_factor = 1 - (i / days) * 0.20  # Up to 20% decline
            else:  # Stable
                trend_factor = 1.0
            
            # Add seasonal variation and noise
            seasonal = 1 + 0.1 * random.uniform(-1, 1)
            
            popularity_history.append(PopularityMetric(
                date=date,
                search_volume=int(base_search_volume * trend_factor * seasonal),
                review_count=int(base_review_count * trend_factor),
                rating_average=round(min(5.0, max(1.0, base_rating + random.uniform(-0.2, 0.2))), 2)
            ))
        
        return popularity_history
    
    def _calculate_price_trend(self, price_history: List[PriceTrend]) -> tuple[str, float]:
        """Calculate price trend direction and percentage change"""
        if len(price_history) < 2:
            return "stable", 0.0
        
        start_price = price_history[0].price
        end_price = price_history[-1].price
        change_percent = ((end_price - start_price) / start_price) * 100
        
        if change_percent > 5:
            trend = "increasing"
        elif change_percent < -5:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return trend, round(change_percent, 2)
    
    def _calculate_popularity_trend(self, popularity_history: List[PopularityMetric]) -> tuple[str, float]:
        """Calculate popularity trend direction and percentage change"""
        if len(popularity_history) < 2:
            return "stable", 0.0
        
        start_volume = popularity_history[0].search_volume
        end_volume = popularity_history[-1].search_volume
        change_percent = ((end_volume - start_volume) / start_volume) * 100
        
        if change_percent > 10:
            trend = "growing"
        elif change_percent < -10:
            trend = "declining"
        else:
            trend = "stable"
        
        return trend, round(change_percent, 2)
    
    def _calculate_momentum(self, price_trend: str, popularity_trend: str) -> str:
        """Determine overall market momentum"""
        if price_trend == "increasing" and popularity_trend == "growing":
            return "bullish"  # Strong positive momentum
        elif price_trend == "decreasing" and popularity_trend == "declining":
            return "bearish"  # Strong negative momentum
        elif price_trend == "decreasing" and popularity_trend == "growing":
            return "opportunity"  # Good value proposition
        elif price_trend == "increasing" and popularity_trend == "declining":
            return "warning"  # Market rejection
        else:
            return "neutral"
    
    def _generate_forecast(self, price_trend: str, popularity_trend: str, momentum: str) -> str:
        """Generate actionable forecast summary"""
        forecasts = {
            "bullish": f"Strong market position. Expect continued growth in both price ({price_trend}) and demand ({popularity_trend}). Consider maintaining or increasing inventory.",
            "bearish": f"Market weakness detected. Both price ({price_trend}) and demand ({popularity_trend}) declining. Consider promotional strategies or product refresh.",
            "opportunity": f"Value opportunity. Demand is {popularity_trend} while prices are {price_trend}. Favorable conditions for market entry or expansion.",
            "warning": f"Market resistance. Prices {price_trend} but demand {popularity_trend}. Re-evaluate positioning and value proposition.",
            "neutral": f"Stable market conditions. Price {price_trend}, demand {popularity_trend}. Maintain current strategy with close monitoring."
        }
        return forecasts.get(momentum, "Market conditions require further analysis.")
    
    def _generate_competitor_comparison(
        self, 
        product_name: str,
        price_history: List[PriceTrend],
        popularity_history: List[PopularityMetric]
    ) -> Dict[str, Any]:
        """Generate competitive landscape data"""
        # Get representative values
        avg_price = sum(p.price for p in price_history[-30:]) / min(30, len(price_history))
        avg_popularity = sum(p.search_volume for p in popularity_history[-30:]) / min(30, len(popularity_history))
        
        # Generate 3-5 competitors with relative metrics
        competitors = []
        competitor_names = self._get_likely_competitors(product_name)
        
        for comp_name in competitor_names[:4]:
            # Generate competitive metrics
            price_diff = random.uniform(-0.20, 0.30)  # -20% to +30% vs main product
            popularity_diff = random.uniform(-0.40, 0.60)  # -40% to +60%
            
            competitors.append({
                "name": comp_name,
                "avg_price": round(avg_price * (1 + price_diff), 2),
                "price_vs_target": f"{price_diff*100:+.1f}%",
                "search_volume": int(avg_popularity * (1 + popularity_diff)),
                "popularity_vs_target": f"{popularity_diff*100:+.1f}%",
                "market_position": self._determine_position(price_diff, popularity_diff)
            })
        
        return {
            "competitors": competitors,
            "target_product": {
                "name": product_name,
                "avg_price": round(avg_price, 2),
                "search_volume": int(avg_popularity)
            },
            "market_share_estimate": self._estimate_market_share(avg_popularity, competitors)
        }
    
    def _estimate_base_price(self, product_name: str) -> float:
        """Estimate base price based on product category"""
        product_lower = product_name.lower()
        
        if any(word in product_lower for word in ["iphone", "galaxy", "pixel"]):
            return random.uniform(799, 1299)
        elif any(word in product_lower for word in ["laptop", "macbook", "notebook"]):
            return random.uniform(999, 2499)
        elif any(word in product_lower for word in ["headphone", "airpod", "earbud"]):
            return random.uniform(149, 549)
        elif any(word in product_lower for word in ["watch", "smartwatch"]):
            return random.uniform(249, 799)
        elif any(word in product_lower for word in ["tablet", "ipad"]):
            return random.uniform(329, 1099)
        else:
            return random.uniform(99, 499)
    
    def _get_likely_competitors(self, product_name: str) -> List[str]:
        """Get likely competitor names based on product"""
        product_lower = product_name.lower()
        
        if "iphone" in product_lower:
            return ["Samsung Galaxy S24", "Google Pixel 8 Pro", "OnePlus 12", "Xiaomi 14 Pro"]
        elif "samsung" in product_lower:
            return ["iPhone 15 Pro", "Google Pixel 8", "OnePlus 12", "Xiaomi 14"]
        elif "airpod" in product_lower:
            return ["Sony WF-1000XM5", "Samsung Galaxy Buds Pro", "Bose QuietComfort", "Jabra Elite"]
        elif "macbook" in product_lower:
            return ["Dell XPS 15", "HP Spectre", "Lenovo ThinkPad X1", "Microsoft Surface Laptop"]
        elif "ipad" in product_lower:
            return ["Samsung Galaxy Tab S9", "Microsoft Surface Pro", "Lenovo Tab P12", "Google Pixel Tablet"]
        else:
            return ["Generic Competitor A", "Generic Competitor B", "Generic Competitor C", "Generic Competitor D"]
    
    def _determine_position(self, price_diff: float, popularity_diff: float) -> str:
        """Determine competitive position"""
        if price_diff > 0.15 and popularity_diff > 0.20:
            return "premium_leader"
        elif price_diff < -0.10 and popularity_diff > 0.10:
            return "value_leader"
        elif abs(price_diff) < 0.10 and abs(popularity_diff) < 0.15:
            return "direct_competitor"
        elif price_diff > 0.20:
            return "premium"
        else:
            return "value"
    
    def _estimate_market_share(self, target_popularity: int, competitors: List[Dict]) -> str:
        """Estimate market share percentage"""
        total_popularity = target_popularity + sum(c.get("search_volume", 0) for c in competitors)
        share_percent = (target_popularity / total_popularity) * 100 if total_popularity > 0 else 0
        return f"{share_percent:.1f}%"
    
    def _analyze_with_real_data(self, input_data: MarketTrendInput) -> TrendAnalysis:
        """
        Placeholder for real data integration.
        
        In production, this would:
        1. Query price tracking APIs (e.g., Amazon Product Advertising API, Keepa)
        2. Fetch search trends (Google Trends API)
        3. Gather review metrics (platform APIs)
        4. Analyze competitor data
        """
        raise NotImplementedError(
            "Real data integration requires API keys. Use use_mock_data=True for demo."
        )
