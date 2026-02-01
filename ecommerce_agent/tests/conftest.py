"""
Pytest Configuration and Shared Fixtures

Provides common test fixtures and configuration for the test suite.
"""

import pytest
import tempfile
import os
from pathlib import Path

# Import agent components for fixtures
from src.agent.orchestrator import MarketAnalysisAgent, OrchestratorConfig, ExecutionStrategy
from src.tools.sentiment_analyzer import SentimentAnalyzerTool
from src.tools.market_trend_analyzer import MarketTrendAnalyzerTool
from src.tools.report_generator import ReportGeneratorTool
from src.tools.product_collector import ProductCollectorTool
from src.utils.models import AnalysisRequest


@pytest.fixture(scope="session")
def test_config():
    """Shared test configuration for fast execution"""
    return OrchestratorConfig(
        max_retries=2,
        retry_delay=0.1,  # Fast retries for testing
        execution_strategy=ExecutionStrategy.SEQUENTIAL,
        enable_metrics=True,
        timeout_seconds=30.0
    )


@pytest.fixture(scope="session")
def sample_agent(test_config):
    """Pre-configured agent with all tools registered"""
    agent = MarketAnalysisAgent(config=test_config)
    
    # Register all tools
    agent.register_tool(SentimentAnalyzerTool())
    agent.register_tool(MarketTrendAnalyzerTool())
    agent.register_tool(ReportGeneratorTool())
    agent.register_tool(ProductCollectorTool())
    
    return agent


@pytest.fixture
def sample_request():
    """Sample analysis request for testing"""
    return AnalysisRequest(
        product_query="Test Product for Unit Tests",
        analysis_depth="standard",
        include_competitors=True,
        include_sentiment=True
    )


@pytest.fixture
def minimal_request():
    """Minimal analysis request for testing"""
    return AnalysisRequest(
        product_query="Minimal Test Product",
        include_competitors=False,
        include_sentiment=False
    )


@pytest.fixture
def temp_reports_dir():
    """Temporary directory for test report generation"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Ensure reports directory exists
        reports_path = Path(temp_dir) / "reports"
        reports_path.mkdir(exist_ok=True)
        
        # Temporarily change the reports directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        yield reports_path
        
        # Restore original directory
        os.chdir(original_cwd)


@pytest.fixture(scope="session")
def api_base_url():
    """Base URL for API testing"""
    return "http://localhost:8000"


# Test markers
pytest_plugins = []


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests that require API server to be running"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark API tests"""
    for item in items:
        # Mark API tests
        if "test_api" in item.nodeid:
            item.add_marker(pytest.mark.api)
        
        # Mark slow tests
        if "comprehensive" in item.name or "concurrent" in item.name:
            item.add_marker(pytest.mark.slow)
