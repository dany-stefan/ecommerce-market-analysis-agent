"""
Main entry point for the Market Analysis Agent.
Simple demo script - appropriate for a 5-hour assignment.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run market analysis"""
    print("=" * 70)
    print("E-COMMERCE MARKET ANALYSIS AGENT")
    print("=" * 70)
    print("\nSimple AI agent for analyzing e-commerce products")
    print("Built as a technical assignment (5-hour project)\n")
    
    try:
        from src.agent.orchestrator import MarketAnalysisAgent, OrchestratorConfig, ExecutionStrategy
        from src.tools.product_collector import ProductCollectorTool
        from src.tools.sentiment_analyzer import SentimentAnalyzerTool
        from src.tools.report_generator import ReportGeneratorTool
        from src.utils.models import AnalysisRequest
        
        # Initialize with enhanced configuration
        config = OrchestratorConfig(
            max_retries=3,
            execution_strategy=ExecutionStrategy.SEQUENTIAL,
            enable_metrics=True
        )
        
        agent = MarketAnalysisAgent(config=config)
        agent.register_tool(ProductCollectorTool(use_mock_data=True))
        agent.register_tool(SentimentAnalyzerTool(use_llm=False))
        agent.register_tool(ReportGeneratorTool(use_llm=False))
        
        print("✅ Agent initialized with enhanced orchestration")
        
        # Example analysis
        print("Running example analysis: iPhone 15 Pro\n")
        print("-" * 70)
        
        request = AnalysisRequest(
            product_query="iPhone 15 Pro",
            analysis_depth="comprehensive",
            include_competitors=True,
            include_sentiment=True
        )
        
        result = agent.analyze(request)
        
        print("\n" + "-" * 70)
        print("\nANALYSIS COMPLETE!\n")
        
        # Display results
        if result.product_data:
            # Handle both dict and ProductData objects
            product = result.product_data if isinstance(result.product_data, dict) else result.product_data
            name = product.get('name') if isinstance(product, dict) else product.name
            price = product.get('price') if isinstance(product, dict) else product.price
            print(f"📦 Product: {name}")
            print(f"💰 Price: ${price}")
        
        if result.sentiment:
            # Handle both dict and SentimentData objects
            sentiment = result.sentiment if isinstance(result.sentiment, dict) else result.sentiment
            overall = sentiment.get('overall_sentiment') if isinstance(sentiment, dict) else sentiment.overall_sentiment
            score = sentiment.get('sentiment_score') if isinstance(sentiment, dict) else sentiment.sentiment_score
            themes = sentiment.get('key_themes', []) if isinstance(sentiment, dict) else sentiment.key_themes
            print(f"\n💬 Customer Sentiment: {overall.upper()}")
            print(f"   Score: {score}/1.0")
            print(f"   Key Themes: {', '.join(themes[:3])}")
        
        if result.competitors:
            print(f"\n🔍 Competitors Analyzed: {len(result.competitors)}")
            for comp in result.competitors:
                comp_name = comp.get('competitor_name') if isinstance(comp, dict) else comp.competitor_name
                comp_price = comp.get('price') if isinstance(comp, dict) else comp.price
                print(f"   - {comp_name}: ${comp_price}")
        
        print(f"\n📊 Recommendations Generated: {len(result.recommendations)}")
        for i, rec in enumerate(result.recommendations[:3], 1):
            print(f"   {i}. {rec}")
        
        # Save report
        if result.metadata.get("report") and "markdown_report" in result.metadata["report"]:
            os.makedirs("reports", exist_ok=True)
            filename = "reports/iphone_analysis.md"
            with open(filename, 'w') as f:
                f.write(result.metadata["report"]["markdown_report"])
            print(f"\n📄 Full report saved: {filename}")
        
        # Show performance metrics
        print("\n" + "=" * 70)
        print("PERFORMANCE METRICS")
        print("=" * 70)
        metrics = agent.get_metrics()
        print(f"Execution Time: {metrics.get('last_analysis_time', 0):.2f}s")
        print(f"Success Rate: {metrics.get('success_rate', 0)}%")
        if metrics.get('average_tool_times'):
            print("\nAverage Tool Execution Times:")
            for tool, avg_time in metrics['average_tool_times'].items():
                print(f"  - {tool}: {avg_time:.3f}s")
        
        print("  pip install -r requirements.txt\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
