"""
Main entry point for the Market Analysis Agent.
Executable code for Question 1 (Agent Orchestration) and Question 2 (Tools Implementation).
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def demo_question_1():
    """
    QUESTION 1: Agent Orchestration & Architecture
    Demonstrates the enhanced orchestrator with retry logic, parallel execution,
    metrics tracking, and health checks.
    """
    print("=" * 80)
    print("QUESTION 1: AGENT ORCHESTRATION & ARCHITECTURE")
    print("=" * 80)
    print("\nDemonstrating native Python agent with enhanced orchestration features\n")
    
    from src.agent.orchestrator import MarketAnalysisAgent, OrchestratorConfig, ExecutionStrategy
    from src.tools.sentiment_analyzer import SentimentAnalyzerTool
    from src.tools.market_trend_analyzer import MarketTrendAnalyzerTool
    from src.tools.report_generator import ReportGeneratorTool
    from src.utils.models import AnalysisRequest
    
    # Configure agent with enhanced features
    config = OrchestratorConfig(
        execution_strategy=ExecutionStrategy.PARALLEL,  # Parallel execution for speed
        max_retries=3,                                  # Retry failed operations
        enable_metrics=True                             # Track performance metrics
    )
    
    agent = MarketAnalysisAgent(config=config)
    
    # Register the 3 specialized tools
    agent.register_tool(SentimentAnalyzerTool(use_llm=False))
    agent.register_tool(MarketTrendAnalyzerTool(use_mock_data=True))
    agent.register_tool(ReportGeneratorTool(use_llm=False))
    
    print("✅ Agent initialized with 3 tools")
    print(f"   - Execution Strategy: {config.execution_strategy.value}")
    print(f"   - Max Retries: {config.max_retries}")
    print(f"   - Metrics Enabled: {config.enable_metrics}")
    
    # Create analysis request
    request = AnalysisRequest(
        product_query="iPhone 15 Pro",
        analysis_depth="comprehensive",
        include_competitors=True,
        include_sentiment=True
    )
    
    print(f"\n📊 Running analysis: {request.product_query}")
    print("-" * 80)
    
    # Execute orchestrated analysis
    result = agent.analyze(request)
    
    print("\n" + "-" * 80)
    print("ANALYSIS RESULTS")
    print("-" * 80)
    
    # Display sentiment analysis
    if result.sentiment:
        sentiment = result.sentiment if isinstance(result.sentiment, dict) else result.sentiment
        overall = sentiment.get('overall_sentiment') if isinstance(sentiment, dict) else sentiment.overall_sentiment
        score = sentiment.get('sentiment_score') if isinstance(sentiment, dict) else sentiment.sentiment_score
        themes = sentiment.get('key_themes', []) if isinstance(sentiment, dict) else sentiment.key_themes
        print(f"\n💬 Sentiment Analysis:")
        print(f"   Overall: {overall.upper()}")
        print(f"   Score: {score:.2f}/1.0")
        print(f"   Key Themes: {', '.join(themes[:3])}")
    
    # Display recommendations
    if result.recommendations:
        print(f"\n📋 Strategic Recommendations: {len(result.recommendations)}")
        for i, rec in enumerate(result.recommendations[:3], 1):
            print(f"   {i}. {rec}")
    
    # Display performance metrics
    print("\n" + "-" * 80)
    print("ORCHESTRATION METRICS")
    print("-" * 80)
    metrics = agent.get_metrics()
    print(f"⏱️  Total Execution Time: {metrics.get('last_analysis_time', 0):.2f}s")
    print(f"✅ Success Rate: {metrics.get('success_rate', 0):.1f}%")
    print(f"🔧 Tools Executed: {metrics.get('total_tools_executed', 0)}")
    
    if metrics.get('average_tool_times'):
        print("\n   Tool Performance:")
        for tool, avg_time in metrics['average_tool_times'].items():
            print(f"     • {tool}: {avg_time:.3f}s")
    
    print("\n✅ Question 1 Demo Complete!")
    return result


def demo_question_2():
    """
    QUESTION 2: Specialized Tools Implementation
    Demonstrates the 3 specialized tools: Sentiment Analyzer, Market Trend Analyzer,
    and Report Generator with visualizations.
    """
    print("\n\n" + "=" * 80)
    print("QUESTION 2: SPECIALIZED TOOLS IMPLEMENTATION")
    print("=" * 80)
    print("\nDemonstrating 3 production-quality tools with mock data\n")
    
    from src.tools.sentiment_analyzer import SentimentAnalyzerTool, SentimentAnalyzerInput
    from src.tools.market_trend_analyzer import MarketTrendAnalyzerTool, MarketTrendInput
    from src.tools.report_generator import ReportGeneratorTool, ReportGeneratorInput
    from src.utils.models import AnalysisResult
    
    # === TOOL 1: Sentiment Analyzer ===
    print("-" * 80)
    print("TOOL 1: SENTIMENT ANALYZER")
    print("-" * 80)
    
    sentiment_tool = SentimentAnalyzerTool(use_llm=False)
    
    sample_reviews = [
        "Amazing phone! Camera quality is incredible and battery lasts all day.",
        "Expensive but worth it. The performance is smooth.",
        "Battery life could be better, but overall great device.",
        "Love the new design and features. Best iPhone yet!",
        "Price is too high for what you get.",
        "Camera is fantastic, especially in low light.",
        "Battery drains quickly with heavy use.",
        "Display is stunning and colors are vibrant."
    ]
    
    sentiment_result = sentiment_tool.run(SentimentAnalyzerInput(
        product_name="iPhone 15 Pro",
        reviews=sample_reviews
    ))
    
    print(f"\n📊 Analyzed {len(sample_reviews)} reviews")
    print(f"   Sentiment: {sentiment_result.data['overall_sentiment'].upper()}")
    print(f"   Score: {sentiment_result.data['sentiment_score']:.2f}/1.0")
    print(f"   Key Themes: {', '.join(sentiment_result.data['key_themes'][:3])}")
    
    # === TOOL 2: Market Trend Analyzer ===
    print("\n" + "-" * 80)
    print("TOOL 2: MARKET TREND ANALYZER")
    print("-" * 80)
    
    trend_tool = MarketTrendAnalyzerTool(use_mock_data=True)
    
    trend_result = trend_tool.run(MarketTrendInput(
        product_name="iPhone 15 Pro",
        time_period_days=90,
        include_competitors=True
    ))
    
    trend_data = trend_result.data
    print(f"\n📈 90-Day Trend Analysis:")
    print(f"   Price Trend: {trend_data.get('price_trend', 'N/A').upper()}")
    if 'price_change_percent' in trend_data:
        print(f"   Price Change: {trend_data['price_change_percent']:+.1f}%")
    print(f"   Popularity Trend: {trend_data.get('popularity_trend', 'N/A').upper()}")
    if 'popularity_change' in trend_data:
        print(f"   Popularity Change: {trend_data['popularity_change']:+.1f}%")
    print(f"   Market Momentum: {trend_data.get('current_momentum', 'N/A').upper()}")
    if 'forecast_summary' in trend_data:
        print(f"\n   💡 Forecast: {trend_data['forecast_summary'][:100]}...")
    
    # === TOOL 3: Report Generator ===
    print("\n" + "-" * 80)
    print("TOOL 3: REPORT GENERATOR (with Visualizations)")
    print("-" * 80)
    
    report_tool = ReportGeneratorTool(use_llm=False)
    
    # Create comprehensive analysis data as dict
    analysis_data = {
        "product_data": {
            "name": "iPhone 15 Pro", 
            "price": 999,
            "currency": "USD",
            "source": "mock"
        },
        "sentiment": sentiment_result.data,
        "competitors": [
            {
                "product_name": "Samsung Galaxy S24", 
                "price": 899,
                "market_position": "competitor",
                "key_features": ["Great camera", "Good battery"]
            },
            {
                "product_name": "Google Pixel 8 Pro", 
                "price": 899,
                "market_position": "competitor",
                "key_features": ["AI features", "Clean software"]
            },
        ],
        "trends": trend_data
    }
    
    report_result = report_tool.run(ReportGeneratorInput(
        analysis_result=analysis_data
    ))
    
    report_data = report_result.data
    print(f"\n📄 Report Generated:")
    if report_data.get('success') and 'recommendations' in report_data:
        print(f"   Recommendations: {len(report_data['recommendations'])}")
        for i, rec in enumerate(report_data['recommendations'][:3], 1):
            print(f"     {i}. {rec}")
    
    if 'visualizations' in report_data:
        print(f"\n   Visualizations: {len(report_data['visualizations'])} chart types")
        for viz_type in report_data['visualizations'].keys():
            print(f"     • {viz_type}")
    
    if 'report' in report_data:
        print(f"\n   Report Length: {len(report_data['report'])} characters")
    elif 'markdown_report' in report_data:
        print(f"\n   Report Length: {len(report_data['markdown_report'])} characters")
        report_content = report_data['markdown_report']
    else:
        report_content = str(report_data)
    
    # Save report to file
    os.makedirs("reports", exist_ok=True)
    report_path = "reports/DEMO_iPhone_15_Pro_Report.md"
    if 'markdown_report' in report_data:
        report_content = report_data['markdown_report']
    elif 'report' in report_data:
        report_content = report_data['report']
    else:
        report_content = str(report_data)
    
    with open(report_path, 'w') as f:
        f.write(report_content)
    print(f"   Saved to: {report_path}")
    
    print("\n✅ Question 2 Demo Complete!")
    return report_data


def main():
    """Run complete demonstration of both questions"""
def main():
    """Run complete demonstration of both questions"""
    
    try:
        # Run Question 1 Demo
        q1_result = demo_question_1()
        
        # Run Question 2 Demo
        q2_result = demo_question_2()
        
        # Final Summary
        print("\n\n" + "=" * 80)
        print("DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("\n✅ Question 1: Agent orchestration with 3 tools executed successfully")
        print("✅ Question 2: Individual tool demonstrations completed")
        print("\n📁 Check the 'reports/' folder for generated analysis reports")
        print("\n" + "=" * 80)
        
    except ImportError as e:
        print(f"\n❌ Missing dependency: {e}")
        print("\nPlease install required packages:")
        print("  pip install -r requirements.txt\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
