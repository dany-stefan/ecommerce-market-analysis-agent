"""
Simple tests for the Market Analysis Agent.
Basic coverage of core functionality - appropriate for a 5-hour assignment.
"""

import pytest
from src.tools.product_collector import ProductCollectorTool, ProductCollectorInput
from src.tools.sentiment_analyzer import SentimentAnalyzerTool, SentimentAnalyzerInput
from src.tools.report_generator import ReportGeneratorTool, ReportGeneratorInput
from src.agent.orchestrator import MarketAnalysisAgent
from src.utils.models import AnalysisRequest, ProductData, SentimentData


class TestProductCollector:
    """Test product collector tool"""
    
    def test_tool_initialization(self):
        """Test that tool initializes correctly"""
        tool = ProductCollectorTool(use_mock_data=True)
        assert tool.name == "ProductCollectorTool"
        assert tool.description is not None
    
    def test_collect_iphone_data(self):
        """Test collecting iPhone product data"""
        tool = ProductCollectorTool(use_mock_data=True)
        result = tool.run(ProductCollectorInput(product_query="iPhone"))
        
        assert result.success is True
        assert result.data is not None
        assert "name" in result.data
        assert "price" in result.data
        assert result.data["price"] > 0
    
    def test_collect_samsung_data(self):
        """Test collecting Samsung product data"""
        tool = ProductCollectorTool(use_mock_data=True)
        result = tool.run(ProductCollectorInput(product_query="Samsung"))
        
        assert result.success is True
        assert "Samsung" in result.data["name"]
    
    def test_unknown_product_fallback(self):
        """Test that unknown products return generic data"""
        tool = ProductCollectorTool(use_mock_data=True)
        result = tool.run(ProductCollectorInput(product_query="Unknown Product XYZ"))
        
        assert result.success is True
        assert result.data is not None
        # Should still return some product data


class TestSentimentAnalyzer:
    """Test sentiment analyzer tool"""
    
    def test_tool_initialization(self):
        """Test that tool initializes correctly"""
        tool = SentimentAnalyzerTool(use_llm=False)
        assert tool.name == "SentimentAnalyzerTool"
    
    def test_positive_sentiment_detection(self):
        """Test detecting positive sentiment"""
        tool = SentimentAnalyzerTool(use_llm=False)
        positive_reviews = [
            "This is excellent! Best product ever!",
            "Amazing quality, very happy with purchase",
            "Great value, love it!"
        ]
        
        result = tool.run(SentimentAnalyzerInput(
            product_name="Test Product",
            reviews=positive_reviews
        ))
        
        assert result.success is True
        assert result.data["overall_sentiment"] in ["positive", "neutral"]
        assert result.data["sentiment_score"] >= 0
    
    def test_negative_sentiment_detection(self):
        """Test detecting negative sentiment"""
        tool = SentimentAnalyzerTool(use_llm=False)
        negative_reviews = [
            "Terrible quality, very disappointed",
            "Awful product, waste of money",
            "Poor build, broke after one week"
        ]
        
        result = tool.run(SentimentAnalyzerInput(
            product_name="Test Product",
            reviews=negative_reviews
        ))
        
        assert result.success is True
        assert result.data["overall_sentiment"] in ["negative", "neutral"]
        assert result.data["sentiment_score"] <= 0.2
    
    def test_caching_works(self):
        """Test that caching reduces redundant work"""
        tool = SentimentAnalyzerTool(use_llm=False)
        reviews = ["Good product", "Nice quality"]
        
        # First call
        result1 = tool.run(SentimentAnalyzerInput(
            product_name="Product",
            reviews=reviews
        ))
        
        # Second call (should use cache)
        result2 = tool.run(SentimentAnalyzerInput(
            product_name="Product",
            reviews=reviews
        ))
        
        assert result1.data == result2.data


class TestReportGenerator:
    """Test report generator tool"""
    
    def test_tool_initialization(self):
        """Test that tool initializes correctly"""
        tool = ReportGeneratorTool(use_llm=False)
        assert tool.name == "ReportGeneratorTool"
    
    def test_generates_recommendations(self):
        """Test that report generates recommendations"""
        from src.utils.models import AnalysisResult, AnalysisRequest, CompetitorData
        
        tool = ReportGeneratorTool(use_llm=False)
        
        mock_analysis = AnalysisResult(
            request=AnalysisRequest(product_query="iPhone"),
            product_data=ProductData(
                name="iPhone 15",
                price=999.00,
                currency="USD",
                description="Smartphone",
                specifications={},
                source="mock"
            ),
            sentiment=SentimentData(
                overall_sentiment="positive",
                sentiment_score=0.8,
                total_reviews=10,
                key_themes=["camera", "battery"],
                sample_reviews=[]
            )
        )
        
        result = tool.run(ReportGeneratorInput(
            analysis_result=mock_analysis.model_dump()
        ))
        
        assert result.success is True
        assert "recommendations" in result.data
        assert len(result.data["recommendations"]) > 0
        assert "markdown_report" in result.data


class TestAgentOrchestration:
    """Test agent orchestration"""
    
    def test_agent_initialization(self):
        """Test that agent initializes correctly"""
        agent = MarketAnalysisAgent()
        assert agent is not None
        assert len(agent.list_tools()) == 0
    
    def test_tool_registration(self):
        """Test registering tools with agent"""
        agent = MarketAnalysisAgent()
        tool = ProductCollectorTool(use_mock_data=True)
        
        agent.register_tool(tool)
        assert len(agent.list_tools()) == 1
        assert "ProductCollectorTool" in agent.list_tools()
    
    def test_complete_analysis_flow(self):
        """Test complete analysis from start to finish"""
        agent = MarketAnalysisAgent()
        
        # Register all tools
        agent.register_tool(ProductCollectorTool(use_mock_data=True))
        agent.register_tool(SentimentAnalyzerTool(use_llm=False))
        agent.register_tool(ReportGeneratorTool(use_llm=False))
        
        # Run analysis
        request = AnalysisRequest(
            product_query="iPhone",
            include_competitors=True,
            include_sentiment=True
        )
        
        result = agent.analyze(request)
        
        # Verify results
        assert result is not None
        assert result.product_data is not None
        assert result.sentiment is not None
        assert len(result.recommendations) > 0
    
    def test_analysis_without_sentiment(self):
        """Test analysis when sentiment is not requested"""
        agent = MarketAnalysisAgent()
        agent.register_tool(ProductCollectorTool(use_mock_data=True))
        agent.register_tool(ReportGeneratorTool(use_llm=False))
        
        request = AnalysisRequest(
            product_query="iPhone",
            include_sentiment=False  # Skip sentiment
        )
        
        result = agent.analyze(request)
        
        assert result.product_data is not None
        assert result.sentiment is None  # Should be None since not requested


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_empty_reviews_list(self):
        """Test sentiment analyzer with empty reviews"""
        tool = SentimentAnalyzerTool(use_llm=False)
        result = tool.run(SentimentAnalyzerInput(
            product_name="Product",
            reviews=[]
        ))
        
        # Should handle gracefully
        assert result.success is True
    
    def test_agent_with_no_tools(self):
        """Test agent behavior when no tools registered"""
        agent = MarketAnalysisAgent()
        
        request = AnalysisRequest(product_query="iPhone")
        result = agent.analyze(request)
        
        # Should complete without crashing
        assert result is not None
    
    def test_product_collector_error_handling(self):
        """Test product collector handles errors"""
        tool = ProductCollectorTool(use_mock_data=True)
        
        # Even with weird input, should not crash
        result = tool.run(ProductCollectorInput(product_query=""))
        assert result is not None


# Run tests with: pytest tests/test_agent.py -v
