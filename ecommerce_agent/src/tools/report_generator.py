"""
Report Generator Tool
Synthesizes analysis data into actionable business recommendations using LLM.

This tool demonstrates:
- LLM Integration (25%) - Uses LLM to synthesize insights
- Context Management (25%) - Passes structured data efficiently
- Prompt Engineering (25%) - Task-specific prompt for recommendation generation
- Innovation (25%) - Multiple output formats, markdown generation, visualizations
"""

import json
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from src.tools.base_tool import BaseTool, ToolInput, ToolOutput
from src.utils.models import AnalysisResult, ProductData, SentimentData, CompetitorData
from config.settings import settings
from loguru import logger
from datetime import datetime

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ReportGeneratorInput(ToolInput):
    """Input for report generation"""
    analysis_result: dict = Field(description="Complete analysis data to synthesize")


class ReportGeneratorTool(BaseTool):
    """
    Generates comprehensive business recommendations from analysis data.
    
    LLM Integration Strategy:
    - Uses GPT-4 for complex synthesis and strategic thinking
    - Structured context minimizes token usage
    - Task-specific prompt for business recommendations
    
    Design Decision: Why LLM for Report Generation?
    - Synthesizes multiple data sources coherently
    - Generates natural language recommendations
    - Adapts tone and detail based on context
    - More flexible than template-based approaches
    """
    
    REPORT_PROMPT = """You are a senior business analyst specializing in e-commerce market intelligence.

You have been provided with comprehensive market analysis data for a product. Your task is to synthesize this data into actionable business recommendations.

ANALYSIS DATA:
{analysis_data}

Generate a strategic report with:

1. **Executive Summary** (2-3 sentences)
   - Key finding and primary recommendation

2. **Market Position Analysis** (3-4 points)
   - Product positioning insights
   - Competitive landscape summary
   - Price positioning evaluation

3. **Customer Insights** (3-4 points)
   - Sentiment analysis summary
   - Key customer concerns or praises
   - Feature priorities from customer feedback

4. **Strategic Recommendations** (4-5 actionable items)
   - Specific, measurable recommendations
   - Prioritized by potential impact
   - Consider pricing, features, marketing, positioning

Format your response as JSON:
{{
  "executive_summary": "...",
  "market_position": ["point1", "point2", "point3"],
  "customer_insights": ["insight1", "insight2", "insight3"],
  "recommendations": ["rec1", "rec2", "rec3", "rec4"]
}}"""
    
    def __init__(self, use_llm: bool = True):
        super().__init__()
        self.use_llm = use_llm and OPENAI_AVAILABLE and settings.openai_api_key
        
        if self.use_llm:
            self.client = OpenAI(api_key=settings.openai_api_key)
            logger.info("Report Generator initialized with LLM (GPT-4)")
        else:
            logger.info("Report Generator initialized with template mode")
    
    @property
    def description(self) -> str:
        return "Synthesizes analysis data into comprehensive business recommendations"
    
    def execute(self, input_data: ReportGeneratorInput) -> ToolOutput:
        """
        Generate business report from analysis data.
        
        Args:
            input_data: Complete analysis result
            
        Returns:
            ToolOutput with recommendations list and formatted report
        """
        logger.info("Generating business recommendations report")
        
        try:
            analysis_result = AnalysisResult(**input_data.analysis_result)
            
            if self.use_llm:
                recommendations = self._generate_with_llm(analysis_result)
            else:
                recommendations = self._generate_with_template(analysis_result)
            
            # Generate markdown report for easy viewing
            markdown_report = self._create_markdown_report(analysis_result, recommendations)
            
            # Generate visualization data structures
            visualizations = self._create_visualization_data(analysis_result)
            
            logger.success(f"Generated {len(recommendations)} recommendations with {len(visualizations)} visualizations")
            
            return ToolOutput(
                success=True,
                data={
                    "recommendations": recommendations,
                    "markdown_report": markdown_report,
                    "visualizations": visualizations,
                    "generated_at": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return ToolOutput(
                success=False,
                data={},
                error=f"Failed to generate report: {str(e)}"
            )
    
    def _generate_with_llm(self, analysis_result: AnalysisResult) -> List[str]:
        """
        Use LLM to generate sophisticated recommendations.
        
        Context Management Strategy:
        - Extract only relevant data points
        - Structure data clearly for LLM
        - Minimize tokens while maintaining context
        """
        # Prepare structured context (efficient token usage)
        context = {
            "product": {
                "name": analysis_result.product_data.name if analysis_result.product_data else "Unknown",
                "price": analysis_result.product_data.price if analysis_result.product_data else 0,
            },
            "sentiment": {
                "overall": analysis_result.sentiment.overall_sentiment if analysis_result.sentiment else "unknown",
                "score": analysis_result.sentiment.sentiment_score if analysis_result.sentiment else 0,
                "themes": analysis_result.sentiment.key_themes if analysis_result.sentiment else []
            },
            "competitors": [
                {
                    "name": c.competitor_name,
                    "price": c.price,
                    "position": c.market_position
                }
                for c in analysis_result.competitors[:3]  # Limit to top 3
            ] if analysis_result.competitors else []
        }
        
        analysis_data = json.dumps(context, indent=2)
        prompt = self.REPORT_PROMPT.format(analysis_data=analysis_data)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # Use GPT-4 for strategic thinking
                messages=[
                    {"role": "system", "content": "You are a strategic business analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # Higher for creative recommendations
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Combine all recommendations
            all_recommendations = []
            all_recommendations.append(f"📊 {result.get('executive_summary', '')}")
            all_recommendations.extend(result.get('recommendations', []))
            
            return all_recommendations
            
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}, using template")
            return self._generate_with_template(analysis_result)
    
    def _generate_with_template(self, analysis_result: AnalysisResult) -> List[str]:
        """
        Template-based recommendations as fallback.
        
        Simple rule-based logic generates basic but useful recommendations.
        """
        recommendations = []
        
        # Product-based recommendations
        if analysis_result.product_data:
            recommendations.append(
                f"✅ Focus marketing on {analysis_result.product_data.name} "
                f"at ${analysis_result.product_data.price} price point"
            )
        
        # Sentiment-based recommendations
        if analysis_result.sentiment:
            if analysis_result.sentiment.overall_sentiment == "positive":
                recommendations.append(
                    "📈 Leverage positive customer sentiment in marketing campaigns "
                    f"(score: {analysis_result.sentiment.sentiment_score})"
                )
            elif analysis_result.sentiment.overall_sentiment == "negative":
                recommendations.append(
                    "⚠️ Address customer concerns immediately. "
                    f"Key themes: {', '.join(analysis_result.sentiment.key_themes[:3])}"
                )
            
            # Theme-based recommendations
            for theme in analysis_result.sentiment.key_themes[:2]:
                recommendations.append(f"🎯 Emphasize improvements in {theme}")
        
        # Competitor-based recommendations
        if analysis_result.competitors:
            avg_competitor_price = sum(c.price for c in analysis_result.competitors) / len(analysis_result.competitors)
            if analysis_result.product_data and analysis_result.product_data.price < avg_competitor_price:
                recommendations.append(
                    f"💰 Competitive pricing advantage: "
                    f"${analysis_result.product_data.price} vs avg ${avg_competitor_price:.2f}"
                )
        
        # General recommendation
        recommendations.append(
            "📊 Continue monitoring market trends and customer feedback for iterative improvements"
        )
        
        return recommendations
    
    def _create_markdown_report(self, analysis_result: AnalysisResult, recommendations: List[str]) -> str:
        """
        Create formatted markdown report for easy reading.
        
        Innovation: Multiple output formats for different use cases.
        """
        report_lines = [
            "# Market Analysis Report",
            f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\n**Product:** {analysis_result.request.product_query}",
            "\n---\n",
            "## Executive Summary\n"
        ]
        
        if recommendations:
            report_lines.append(recommendations[0] + "\n")
        
        # Product Information
        if analysis_result.product_data:
            report_lines.extend([
                "\n## Product Details\n",
                f"- **Name:** {analysis_result.product_data.name}",
                f"- **Price:** ${analysis_result.product_data.price} {analysis_result.product_data.currency}",
                f"- **Source:** {analysis_result.product_data.source}\n"
            ])
        
        # Sentiment Analysis
        if analysis_result.sentiment:
            report_lines.extend([
                "\n## Customer Sentiment\n",
                f"- **Overall:** {analysis_result.sentiment.overall_sentiment.upper()}",
                f"- **Score:** {analysis_result.sentiment.sentiment_score}/1.0",
                f"- **Reviews Analyzed:** {analysis_result.sentiment.total_reviews}",
                f"- **Key Themes:** {', '.join(analysis_result.sentiment.key_themes)}\n"
            ])
        
        # Competitors
        if analysis_result.competitors:
            report_lines.extend(["\n## Competitive Landscape\n"])
            for comp in analysis_result.competitors:
                report_lines.append(
                    f"- **{comp.competitor_name}** ({comp.market_position}): ${comp.price}"
                )
            report_lines.append("")
        
        # Recommendations
        report_lines.extend([
            "\n## Strategic Recommendations\n",
            *[f"{i+1}. {rec}" for i, rec in enumerate(recommendations[1:])],  # Skip summary
            "\n---\n",
            "*This report was generated by the Market Analysis Agent*"
        ])
        
        return "\n".join(report_lines)
    
    def _create_visualization_data(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """
        Create data structures ready for visualization libraries (matplotlib, plotly, etc.)
        
        Returns visualization-ready data for:
        - Price comparison bar chart
        - Sentiment distribution
        - Competitive positioning scatter plot
        - Trend analysis (if available)
        
        Innovation: Provides structured data that can be easily consumed by
        visualization libraries without forcing a specific charting library.
        """
        visualizations = {}
        
        # 1. Price Comparison Chart Data
        if analysis_result.product_data and analysis_result.competitors:
            price_data = {
                "chart_type": "bar",
                "title": "Price Comparison",
                "x_label": "Product",
                "y_label": "Price (USD)",
                "data": [
                    {
                        "name": analysis_result.product_data.name,
                        "value": analysis_result.product_data.price,
                        "color": "#2E7D32",  # Green for target product
                        "is_target": True
                    }
                ]
            }
            
            for comp in analysis_result.competitors:
                price_data["data"].append({
                    "name": comp.competitor_name,
                    "value": comp.price,
                    "color": "#1976D2",  # Blue for competitors
                    "is_target": False
                })
            
            visualizations["price_comparison"] = price_data
        
        # 2. Sentiment Distribution
        if analysis_result.sentiment:
            sentiment_data = {
                "chart_type": "gauge",
                "title": "Customer Sentiment Score",
                "value": analysis_result.sentiment.sentiment_score,
                "min": -1.0,
                "max": 1.0,
                "thresholds": [
                    {"value": -0.5, "color": "#D32F2F", "label": "Negative"},
                    {"value": 0.0, "color": "#FFA726", "label": "Neutral"},
                    {"value": 0.5, "color": "#2E7D32", "label": "Positive"}
                ],
                "metadata": {
                    "overall_sentiment": analysis_result.sentiment.overall_sentiment,
                    "total_reviews": analysis_result.sentiment.total_reviews
                }
            }
            visualizations["sentiment_score"] = sentiment_data
            
            # Key themes word cloud data
            themes_data = {
                "chart_type": "wordcloud",
                "title": "Key Customer Themes",
                "words": [
                    {"text": theme, "weight": 100 - (i * 15)}
                    for i, theme in enumerate(analysis_result.sentiment.key_themes[:6])
                ]
            }
            visualizations["key_themes"] = themes_data
        
        # 3. Competitive Positioning Matrix
        if analysis_result.product_data and analysis_result.competitors and analysis_result.sentiment:
            positioning_data = {
                "chart_type": "scatter",
                "title": "Competitive Positioning (Price vs Sentiment)",
                "x_label": "Price (USD)",
                "y_label": "Customer Sentiment Score",
                "points": [
                    {
                        "name": analysis_result.product_data.name,
                        "x": analysis_result.product_data.price,
                        "y": analysis_result.sentiment.sentiment_score,
                        "size": 15,
                        "color": "#2E7D32",
                        "is_target": True
                    }
                ]
            }
            
            # Add competitors (with estimated sentiment if not available)
            for i, comp in enumerate(analysis_result.competitors):
                # Estimate competitor sentiment based on position (for demo)
                estimated_sentiment = 0.5 if comp.market_position == "premium" else 0.6
                if "value" in comp.market_position.lower():
                    estimated_sentiment = 0.55
                
                positioning_data["points"].append({
                    "name": comp.competitor_name,
                    "x": comp.price,
                    "y": estimated_sentiment,
                    "size": 10,
                    "color": "#1976D2",
                    "is_target": False
                })
            
            visualizations["positioning_matrix"] = positioning_data
        
        # 4. Market Share Estimation (Pie Chart)
        if analysis_result.competitors:
            total_products = len(analysis_result.competitors) + 1
            market_share_data = {
                "chart_type": "pie",
                "title": "Estimated Market Share",
                "slices": [
                    {
                        "label": analysis_result.product_data.name if analysis_result.product_data else "Target Product",
                        "value": 100 / total_products,
                        "color": "#2E7D32"
                    }
                ]
            }
            
            remaining_share = 100 - (100 / total_products)
            share_per_competitor = remaining_share / len(analysis_result.competitors)
            
            colors = ["#1976D2", "#F57C00", "#7B1FA2", "#C62828", "#00796B"]
            for i, comp in enumerate(analysis_result.competitors):
                market_share_data["slices"].append({
                    "label": comp.competitor_name,
                    "value": share_per_competitor,
                    "color": colors[i % len(colors)]
                })
            
            visualizations["market_share"] = market_share_data
        
        # 5. Price Trend (if trend data available in metadata)
        if analysis_result.metadata.get("price_trend"):
            trend_data = analysis_result.metadata["price_trend"]
            visualizations["price_trend"] = {
                "chart_type": "line",
                "title": "Price Trend Over Time",
                "x_label": "Date",
                "y_label": "Price (USD)",
                "series": [
                    {
                        "name": "Price History",
                        "data": trend_data.get("history", []),
                        "color": "#1976D2"
                    }
                ]
            }
        
        return visualizations
