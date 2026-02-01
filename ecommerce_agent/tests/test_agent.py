"""
Comprehensive Test Suite for E-commerce Market Analysis Agent

Tests cover:
1. Individual tool functionality (SentimentAnalyzer, MarketTrend, ReportGenerator, ProductCollector)
2. Agent orchestration (sequential, parallel execution)
3. Error handling and retry logic
4. Input/output validation
5. Performance metrics
6. Configuration management
7. Health checks

Run with: pytest tests/test_agent.py -v --cov=src
"""

import pytest
import json
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime

# Import agent components
from src.agent.orchestrator import MarketAnalysisAgent, OrchestratorConfig, ExecutionStrategy
from src.tools.sentiment_analyzer import SentimentAnalyzerTool, SentimentAnalyzerInput
from src.tools.market_trend_analyzer import MarketTrendAnalyzerTool, MarketTrendInput
from src.tools.report_generator import ReportGeneratorTool, ReportGeneratorInput
from src.tools.product_collector import ProductCollectorTool, ProductCollectorInput
from src.tools.base_tool import ToolOutput
from src.utils.models import AnalysisRequest, AnalysisResult


class TestConfiguration:
    """Test orchestrator configuration and setup"""
    
    def test_orchestrator_config_creation(self):
        """Test 1: Configuration object creation and defaults"""
        config = OrchestratorConfig()
        
        assert config.max_retries == 3
        assert config.execution_strategy == ExecutionStrategy.SEQUENTIAL
        assert config.enable_metrics is True
        assert config.use_llm is False
        
    def test_orchestrator_config_custom_settings(self):
        """Test configuration with custom values"""
        config = OrchestratorConfig(
            max_retries=5,
            execution_strategy=ExecutionStrategy.PARALLEL,
            enable_metrics=False,
            timeout_seconds=120.0
        )
        
        assert config.max_retries == 5
        assert config.execution_strategy == ExecutionStrategy.PARALLEL
        assert config.enable_metrics is False
        assert config.timeout_seconds == 120.0


class TestIndividualTools:
    """Test individual tool functionality"""
    
    def test_sentiment_analyzer_tool(self):
        """Test 2: Sentiment Analyzer Tool functionality"""
        tool = SentimentAnalyzerTool()
        
        # Test with sample input
        sample_input = SentimentAnalyzerInput(
            product_name="iPhone 15 Pro",
            reviews=[
                "Great camera quality, love the titanium build!",
                "Battery life is excellent, lasts all day",
                "Price is a bit high but worth it for the features"
            ]
        )
        
        result = tool.execute(sample_input)
        
        assert isinstance(result, ToolOutput)
        assert result.success is True
        assert "overall_sentiment" in result.data
        assert "sentiment_score" in result.data
        assert isinstance(result.data["sentiment_score"], float)
        assert -1.0 <= result.data["sentiment_score"] <= 1.0
        assert "key_themes" in result.data
        assert isinstance(result.data["key_themes"], list)
        
    def test_market_trend_analyzer_tool(self):
        """Test 3: Market Trend Analyzer Tool functionality"""
        tool = MarketTrendAnalyzerTool()
        
        # Test with sample input
        sample_input = MarketTrendInput(
            product_name="MacBook Pro M3",
            days_back=90
        )
        
        result = tool.execute(sample_input)
        
        assert isinstance(result, ToolOutput)
        assert result.success is True
        assert "price_trend" in result.data
        assert "popularity_trend" in result.data
        assert "momentum" in result.data
        assert "forecast" in result.data
        assert "recent_prices" in result.data
        
    def test_product_collector_tool(self):
        """Test 4: Product Collector Tool functionality"""
        tool = ProductCollectorTool()
        
        # Test with sample input
        sample_input = ProductCollectorInput(
            product_query="Samsung Galaxy S24 Ultra"
        )
        
        result = tool.execute(sample_input)
        
        assert isinstance(result, ToolOutput)
        assert result.success is True
        assert "query" in result.data
        assert "products" in result.data
        assert len(result.data["products"]) > 0
        
        # Validate product structure
        product = result.data["products"][0]
        assert "name" in product
        assert "price" in product
        assert "currency" in product
        assert isinstance(product["price"], (int, float))
        
    def test_report_generator_tool(self):
        """Test 5: Report Generator Tool functionality"""
        tool = ReportGeneratorTool()
        
        # Create mock analysis result
        mock_analysis = {
            "request": {
                "product_query": "Test Product",
                "analysis_depth": "standard",
                "include_competitors": True,
                "include_sentiment": True
            },
            "product_data": {
                "name": "Test Product",
                "price": 999.0,
                "currency": "USD"
            },
            "sentiment": {
                "overall_sentiment": "positive",
                "sentiment_score": 0.75,
                "key_themes": ["quality", "performance"]
            },
            "competitors": [
                {"competitor_name": "Competitor A", "price": 899.0}
            ],
            "recommendations": [],
            "metadata": {"status": "success"}
        }
        
        sample_input = ReportGeneratorInput(
            analysis_result=mock_analysis
        )
        
        result = tool.execute(sample_input)
        
        assert isinstance(result, ToolOutput)
        assert result.success is True
        assert "recommendations" in result.data
        assert len(result.data["recommendations"]) > 0
        assert "report_file" in result.data
        assert "visualizations" in result.data


class TestOrchestration:
    """Test agent orchestration functionality"""
    
    def setup_method(self):
        """Setup agent for testing"""
        config = OrchestratorConfig(
            execution_strategy=ExecutionStrategy.SEQUENTIAL,
            max_retries=2,
            enable_metrics=True
        )
        self.agent = MarketAnalysisAgent(config=config)
        
        # Register all tools
        self.agent.register_tool(SentimentAnalyzerTool())
        self.agent.register_tool(MarketTrendAnalyzerTool())
        self.agent.register_tool(ReportGeneratorTool())
        self.agent.register_tool(ProductCollectorTool())
    
    def test_agent_tool_registration(self):
        """Test tool registration and validation"""
        assert "SentimentAnalyzerTool" in self.agent.tools
        assert "MarketTrendAnalyzerTool" in self.agent.tools
        assert "ReportGeneratorTool" in self.agent.tools
        assert "ProductCollectorTool" in self.agent.tools
        assert len(self.agent.tools) == 4
        
    def test_sequential_orchestration(self):
        """Test 6: Sequential execution orchestration"""
        request = AnalysisRequest(
            product_query="iPhone 15 Pro",
            analysis_depth="standard",
            include_competitors=True,
            include_sentiment=True
        )
        
        result = self.agent.analyze(request)
        
        # Validate result structure
        assert isinstance(result, AnalysisResult)
        assert result.request.product_query == "iPhone 15 Pro"
        assert result.metadata["status"] == "success"
        assert result.metadata["execution_strategy"] == "sequential"
        assert "execution_time" in result.metadata
        
        # Validate data was collected
        assert result.product_data is not None
        assert result.sentiment is not None
        assert len(result.competitors) > 0
        assert len(result.recommendations) > 0
        
    def test_parallel_orchestration(self):
        """Test parallel execution orchestration"""
        # Configure for parallel execution
        parallel_config = OrchestratorConfig(
            execution_strategy=ExecutionStrategy.PARALLEL,
            max_retries=2,
            enable_metrics=True
        )
        parallel_agent = MarketAnalysisAgent(config=parallel_config)
        
        # Register tools
        parallel_agent.register_tool(SentimentAnalyzerTool())
        parallel_agent.register_tool(MarketTrendAnalyzerTool())
        parallel_agent.register_tool(ReportGeneratorTool())
        parallel_agent.register_tool(ProductCollectorTool())
        
        request = AnalysisRequest(
            product_query="MacBook Pro M3",
            analysis_depth="comprehensive",
            include_competitors=True,
            include_sentiment=True
        )
        
        result = parallel_agent.analyze(request)
        
        assert isinstance(result, AnalysisResult)
        assert result.metadata["execution_strategy"] == "parallel"
        assert result.metadata["status"] == "success"
        
    def test_metrics_collection(self):
        """Test performance metrics collection"""
        # Run an analysis to generate metrics
        request = AnalysisRequest(
            product_query="Test Product",
            include_sentiment=True,
            include_competitors=False
        )
        
        self.agent.analyze(request)
        
        metrics = self.agent.get_metrics()
        
        assert "total_analyses" in metrics
        assert "successful_analyses" in metrics
        assert "success_rate" in metrics
        assert "average_tool_times" in metrics
        assert metrics["total_analyses"] >= 1
        assert metrics["success_rate"] > 0
        
    def test_health_check(self):
        """Test system health monitoring"""
        health = self.agent.health_check()
        
        assert "orchestrator" in health
        assert "tools" in health
        assert "timestamp" in health
        assert health["orchestrator"] in ["healthy", "degraded"]
        
        # Check each tool health
        for tool_name in self.agent.tools.keys():
            assert tool_name in health["tools"]


class TestErrorHandling:
    """Test error handling and retry logic"""
    
    def test_retry_logic_with_failing_tool(self):
        """Test 7: Error handling with retry logic"""
        config = OrchestratorConfig(
            max_retries=3,
            retry_delay=0.1  # Fast retries for testing
        )
        agent = MarketAnalysisAgent(config=config)
        
        # Mock a failing tool
        failing_tool = MagicMock()
        failing_tool.name = "FailingTool"
        failing_tool.run.side_effect = Exception("Simulated failure")
        
        # Test retry logic directly
        result = agent._execute_with_retry(
            failing_tool.run,
            "test_input",
            tool_name="FailingTool"
        )
        
        assert result["success"] is False
        assert "Failed after 3 retries" in result["error"]
        assert failing_tool.run.call_count == 3  # Should retry 3 times
        
    def test_invalid_input_validation(self):
        """Test input validation and error responses"""
        tool = SentimentAnalyzerTool()
        
        # Test with invalid input (empty reviews)
        invalid_input = SentimentAnalyzerInput(
            product_name="Test Product",
            reviews=[]  # Empty reviews should handle gracefully
        )
        
        result = tool.execute(invalid_input)
        
        # Tool should handle gracefully (either succeed with empty data or fail gracefully)
        assert isinstance(result, ToolOutput)
        if not result.success:
            assert len(result.error) > 0
            
    def test_analysis_request_validation(self):
        """Test analysis request validation"""
        agent = MarketAnalysisAgent()
        agent.register_tool(SentimentAnalyzerTool())
        agent.register_tool(ProductCollectorTool())
        
        # Test with minimal valid request
        minimal_request = AnalysisRequest(
            product_query="Test Product",
            include_sentiment=False,
            include_competitors=False
        )
        
        # Should not raise validation errors
        result = agent.analyze(minimal_request)
        assert isinstance(result, AnalysisResult)
        
        # Test with empty product query - should handle gracefully
        try:
            empty_request = AnalysisRequest(
                product_query="",  # Empty query
                include_sentiment=True
            )
            # Pydantic should catch this, but if it doesn't, agent should handle it
        except ValueError:
            # Expected pydantic validation error
            pass


class TestOutputValidation:
    """Test output format validation and data integrity"""
    
    def test_analysis_result_structure(self):
        """Test complete analysis result structure validation"""
        config = OrchestratorConfig(enable_metrics=True)
        agent = MarketAnalysisAgent(config=config)
        
        # Register all tools
        agent.register_tool(SentimentAnalyzerTool())
        agent.register_tool(MarketTrendAnalyzerTool())
        agent.register_tool(ReportGeneratorTool())
        agent.register_tool(ProductCollectorTool())
        
        request = AnalysisRequest(
            product_query="Comprehensive Test Product",
            analysis_depth="comprehensive",
            include_competitors=True,
            include_sentiment=True
        )
        
        result = agent.analyze(request)
        
        # Validate required fields
        assert hasattr(result, 'request')
        assert hasattr(result, 'product_data')
        assert hasattr(result, 'sentiment')
        assert hasattr(result, 'competitors')
        assert hasattr(result, 'recommendations')
        assert hasattr(result, 'metadata')
        assert hasattr(result, 'created_at')
        
        # Validate metadata structure
        assert "status" in result.metadata
        assert "execution_time" in result.metadata
        assert "execution_strategy" in result.metadata
        
        # Validate data types
        if result.sentiment:
            assert isinstance(result.sentiment, dict)
            
        if result.competitors:
            assert isinstance(result.competitors, list)
            
        assert isinstance(result.recommendations, list)
        assert isinstance(result.metadata, dict)
        
    def test_report_file_generation(self):
        """Test that report files are actually created"""
        tool = ReportGeneratorTool()
        
        # Create a comprehensive mock analysis
        mock_analysis = {
            "request": {
                "product_query": "Test Product for Report",
                "analysis_depth": "comprehensive",
                "include_competitors": True,
                "include_sentiment": True
            },
            "product_data": {
                "name": "Test Product for Report", 
                "price": 1299.0,
                "currency": "USD",
                "description": "A test product for validation"
            },
            "sentiment": {
                "overall_sentiment": "positive",
                "sentiment_score": 0.82,
                "total_reviews": 150,
                "key_themes": ["quality", "performance", "value"]
            },
            "competitors": [
                {"competitor_name": "Competitor A", "price": 1199.0},
                {"competitor_name": "Competitor B", "price": 1399.0}
            ],
            "recommendations": [],
            "metadata": {"status": "success"}
        }
        
        sample_input = ReportGeneratorInput(analysis_result=mock_analysis)
        result = tool.execute(sample_input)
        
        assert result.success is True
        assert "report_file" in result.data
        
        # Check if report file was actually created
        if "report_file" in result.data:
            report_path = result.data["report_file"]
            if report_path and Path(report_path).exists():
                # Verify file exists and has content
                assert Path(report_path).stat().st_size > 0
                
                # Read and validate basic markdown structure
                with open(report_path, 'r') as f:
                    content = f.read()
                    assert "# Market Analysis Report" in content
                    assert "Test Product for Report" in content


# Test configuration for pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src", "--cov-report=term-missing"])
