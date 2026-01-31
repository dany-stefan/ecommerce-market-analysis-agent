"""
Data models for the market analysis agent.
Using Pydantic for validation and clear data structures.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ProductData(BaseModel):
    """Product information collected by tools"""
    name: str
    price: float
    currency: str = "USD"
    description: Optional[str] = None
    specifications: Dict[str, Any] = Field(default_factory=dict)
    source: str  # Where the data came from
    timestamp: datetime = Field(default_factory=datetime.now)


class CompetitorData(BaseModel):
    """Competitor analysis data"""
    competitor_name: str
    product_name: str
    price: float
    market_position: str  # e.g., "premium", "budget", "mid-range"
    key_features: List[str] = Field(default_factory=list)


class SentimentData(BaseModel):
    """Customer sentiment analysis results"""
    overall_sentiment: str  # "positive", "negative", "neutral"
    sentiment_score: float  # -1.0 to 1.0
    total_reviews: int
    key_themes: List[str] = Field(default_factory=list)
    sample_reviews: List[str] = Field(default_factory=list)


class AnalysisRequest(BaseModel):
    """Input for the market analysis agent"""
    product_query: str
    analysis_depth: str = "standard"  # "quick", "standard", "comprehensive"
    include_competitors: bool = True
    include_sentiment: bool = True


class AnalysisResult(BaseModel):
    """Complete analysis output"""
    request: AnalysisRequest
    product_data: Optional[ProductData] = None
    competitors: List[CompetitorData] = Field(default_factory=list)
    sentiment: Optional[SentimentData] = None
    recommendations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
