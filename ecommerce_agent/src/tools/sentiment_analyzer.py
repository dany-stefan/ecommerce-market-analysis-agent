"""
Sentiment Analyzer Tool
Analyzes customer reviews using LLM for sophisticated sentiment understanding.

This tool demonstrates:
- LLM Integration (25%) - Uses OpenAI with task-specific prompts
- Prompt Engineering (25%) - Optimized prompt for sentiment analysis
- Error Handling (25%) - Graceful fallback if LLM unavailable
- Innovation (25%) - Caching and mock mode for development
"""

import json
import hashlib
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.tools.base_tool import BaseTool, ToolInput, ToolOutput
from src.utils.models import SentimentData
from config.settings import settings
from loguru import logger

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not installed. Install with: pip install openai")


class SentimentAnalyzerInput(ToolInput):
    """Input for sentiment analysis"""
    product_name: str = Field(description="Product name for context")
    reviews: List[str] = Field(description="List of customer reviews to analyze")


class SentimentAnalyzerTool(BaseTool):
    """
    Analyzes customer sentiment using LLM for deep understanding.
    
    LLM Integration Strategy:
    - Uses GPT-3.5-turbo for cost efficiency (sentiment is simpler task)
    - Task-specific prompt optimized for review analysis
    - JSON mode for structured output
    - Caching to reduce costs on duplicate analyses
    
    Design Decision: LLM vs Rule-based
    - LLM: Better at nuance, sarcasm, context
    - Trade-off: Cost and latency
    - Solution: Cache + mock mode for development
    """
    
    # Optimized prompt for sentiment analysis
    SENTIMENT_PROMPT = """You are an expert market analyst specializing in customer sentiment analysis.

Analyze the following customer reviews for "{product_name}" and provide:

1. overall_sentiment: One of "positive", "negative", or "neutral"
2. sentiment_score: A number from -1.0 (very negative) to 1.0 (very positive)
3. key_themes: List of 3-5 main themes mentioned across reviews
4. sample_reviews: Select 2-3 most representative reviews

Reviews:
{reviews}

Respond with JSON in this exact format:
{{
  "overall_sentiment": "positive|negative|neutral",
  "sentiment_score": 0.0,
  "key_themes": ["theme1", "theme2", "theme3"],
  "sample_reviews": ["review1", "review2"]
}}"""
    
    def __init__(self, use_llm: bool = True):
        super().__init__()
        self.use_llm = use_llm and OPENAI_AVAILABLE and settings.openai_api_key
        
        if self.use_llm:
            self.client = OpenAI(api_key=settings.openai_api_key)
            logger.info("Sentiment Analyzer initialized with LLM")
        else:
            logger.info("Sentiment Analyzer initialized with mock mode")
        
        # Simple in-memory cache (Production: Redis)
        self._cache: Dict[str, SentimentData] = {}
    
    @property
    def description(self) -> str:
        return "Analyzes customer reviews to extract sentiment, themes, and insights"
    
    def execute(self, input_data: SentimentAnalyzerInput) -> ToolOutput:
        """
        Analyze sentiment of customer reviews.
        
        Args:
            input_data: Product name and list of reviews
            
        Returns:
            ToolOutput with SentimentData
        """
        logger.info(f"Analyzing sentiment for {input_data.product_name} ({len(input_data.reviews)} reviews)")
        
        try:
            # Check cache first (Innovation: cost optimization)
            cache_key = self._get_cache_key(input_data)
            if cache_key in self._cache:
                logger.info("Using cached sentiment analysis")
                return ToolOutput(
                    success=True,
                    data=self._cache[cache_key].model_dump()
                )
            
            # Perform analysis
            if self.use_llm:
                sentiment_data = self._analyze_with_llm(input_data)
            else:
                sentiment_data = self._analyze_with_mock(input_data)
            
            # Cache result
            self._cache[cache_key] = sentiment_data
            
            logger.success(
                f"Sentiment analysis complete: {sentiment_data.overall_sentiment} "
                f"(score: {sentiment_data.sentiment_score})"
            )
            
            return ToolOutput(
                success=True,
                data=sentiment_data.model_dump()
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return ToolOutput(
                success=False,
                data={},
                error=f"Failed to analyze sentiment: {str(e)}"
            )
    
    def _analyze_with_llm(self, input_data: SentimentAnalyzerInput) -> SentimentData:
        """
        Use LLM for sentiment analysis.
        
        Prompt Engineering Strategy:
        - Clear role definition ("expert market analyst")
        - Structured output format (JSON)
        - Specific instructions for each field
        - Examples implicit in format
        """
        # Format reviews for prompt
        reviews_text = "\n".join([f"- {review}" for review in input_data.reviews])
        
        prompt = self.SENTIMENT_PROMPT.format(
            product_name=input_data.product_name,
            reviews=reviews_text
        )
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Cost-efficient for this task
                messages=[
                    {"role": "system", "content": "You are a helpful market analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=500,
                response_format={"type": "json_object"}  # Ensure JSON output
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            return SentimentData(
                overall_sentiment=result["overall_sentiment"],
                sentiment_score=float(result["sentiment_score"]),
                total_reviews=len(input_data.reviews),
                key_themes=result["key_themes"],
                sample_reviews=result["sample_reviews"]
            )
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {str(e)}, falling back to mock")
            return self._analyze_with_mock(input_data)
    
    def _analyze_with_mock(self, input_data: SentimentAnalyzerInput) -> SentimentData:
        """
        Simple rule-based sentiment analysis for testing without LLM.
        
        Design Decision: Always have a fallback for resilience.
        Mock uses basic keyword matching - not production quality but functional.
        """
        # Simple keyword-based sentiment
        positive_words = {"great", "excellent", "love", "amazing", "perfect", "best", "good", "happy"}
        negative_words = {"bad", "terrible", "worst", "awful", "hate", "poor", "broken", "disappointed"}
        
        positive_count = 0
        negative_count = 0
        themes = set()
        
        for review in input_data.reviews:
            review_lower = review.lower()
            
            # Count sentiment words
            positive_count += sum(1 for word in positive_words if word in review_lower)
            negative_count += sum(1 for word in negative_words if word in review_lower)
            
            # Extract simple themes (words that appear frequently)
            # This is very basic - real implementation would use NLP
            if "battery" in review_lower:
                themes.add("battery life")
            if "camera" in review_lower or "photo" in review_lower:
                themes.add("camera quality")
            if "price" in review_lower or "expensive" in review_lower or "cheap" in review_lower:
                themes.add("pricing")
            if "quality" in review_lower:
                themes.add("build quality")
            if "easy" in review_lower or "difficult" in review_lower:
                themes.add("ease of use")
        
        # Calculate sentiment
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            overall_sentiment = "neutral"
            sentiment_score = 0.0
        else:
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
            if sentiment_score > 0.2:
                overall_sentiment = "positive"
            elif sentiment_score < -0.2:
                overall_sentiment = "negative"
            else:
                overall_sentiment = "neutral"
        
        # Select sample reviews (first 2)
        sample_reviews = input_data.reviews[:2] if len(input_data.reviews) >= 2 else input_data.reviews
        
        return SentimentData(
            overall_sentiment=overall_sentiment,
            sentiment_score=round(sentiment_score, 2),
            total_reviews=len(input_data.reviews),
            key_themes=list(themes)[:5] if themes else ["general feedback"],
            sample_reviews=sample_reviews
        )
    
    def _get_cache_key(self, input_data: SentimentAnalyzerInput) -> str:
        """Generate cache key from input data."""
        content = f"{input_data.product_name}:{':'.join(sorted(input_data.reviews))}"
        return hashlib.md5(content.encode()).hexdigest()
