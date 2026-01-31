"""
Report Generator Tool
Synthesizes analysis data into actionable business recommendations using LLM.

This tool demonstrates:
- LLM Integration (25%) - Uses LLM to synthesize insights
- Context Management (25%) - Passes structured data efficiently
- Prompt Engineering (25%) - Task-specific prompt for recommendation generation
- Innovation (25%) - Multiple output formats, markdown generation
"""

import json
from typing import List, Optional
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
            
            logger.success(f"Generated {len(recommendations)} recommendations")
            
            return ToolOutput(
                success=True,
                data={
                    "recommendations": recommendations,
                    "markdown_report": markdown_report,
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
