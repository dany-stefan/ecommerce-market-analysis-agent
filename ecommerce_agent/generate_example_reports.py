"""
Simple script to generate example reports.
Run: python generate_example_reports.py
"""

import sys
sys.path.append('.')

from src.agent.orchestrator import MarketAnalysisAgent
from src.tools.product_collector import ProductCollectorTool
from src.tools.sentiment_analyzer import SentimentAnalyzerTool
from src.tools.report_generator import ReportGeneratorTool
from src.utils.models import AnalysisRequest
from datetime import datetime
import json


def generate_iphone_report():
    """Generate example report for iPhone 15 Pro"""
    print("🔍 Generating Market Analysis Report for iPhone 15 Pro...")
    print("="*70 + "\n")
    
    # Initialize agent
    agent = MarketAnalysisAgent()
    agent.register_tool(ProductCollectorTool(use_mock_data=True))
    agent.register_tool(SentimentAnalyzerTool(use_llm=False))
    agent.register_tool(ReportGeneratorTool(use_llm=False))
    
    # Run analysis
    request = AnalysisRequest(
        product_query="iPhone 15 Pro",
        analysis_depth="comprehensive",
        include_competitors=True,
        include_sentiment=True
    )
    
    result = agent.analyze(request)
    
    # Save markdown report
    if result.metadata.get("report") and "markdown_report" in result.metadata["report"]:
        report_content = result.metadata["report"]["markdown_report"]
        
        filename = "reports/iphone_15_pro_analysis.md"
        with open(filename, 'w') as f:
            f.write(report_content)
        
        print(f"\n✅ Report saved to: {filename}\n")
        print("="*70)
        print(report_content)
        print("="*70)
    
    # Save JSON summary
    summary = {
        "product": result.product_data.name if result.product_data else "Unknown",
        "price": result.product_data.price if result.product_data else 0,
        "sentiment": result.sentiment.overall_sentiment if result.sentiment else "unknown",
        "sentiment_score": result.sentiment.sentiment_score if result.sentiment else 0,
        "competitors_analyzed": len(result.competitors),
        "recommendations_count": len(result.recommendations),
        "generated_at": datetime.now().isoformat()
    }
    
    json_filename = "reports/iphone_15_pro_summary.json"
    with open(json_filename, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Summary saved to: {json_filename}")
    
    return result


def generate_airpods_report():
    """Generate example report for AirPods Pro"""
    print("\n\n🔍 Generating Market Analysis Report for AirPods Pro...")
    print("="*70 + "\n")
    
    agent = MarketAnalysisAgent()
    agent.register_tool(ProductCollectorTool(use_mock_data=True))
    agent.register_tool(SentimentAnalyzerTool(use_llm=False))
    agent.register_tool(ReportGeneratorTool(use_llm=False))
    
    request = AnalysisRequest(
        product_query="AirPods Pro",
        analysis_depth="standard",
        include_competitors=True,
        include_sentiment=True
    )
    
    result = agent.analyze(request)
    
    if result.metadata.get("report") and "markdown_report" in result.metadata["report"]:
        report_content = result.metadata["report"]["markdown_report"]
        
        filename = "reports/airpods_pro_analysis.md"
        with open(filename, 'w') as f:
            f.write(report_content)
        
        print(f"\n✅ Report saved to: {filename}")
    
    return result


if __name__ == "__main__":
    import os
    
    # Create reports directory
    os.makedirs("reports", exist_ok=True)
    
    # Generate example reports
    print("Generating Example Market Analysis Reports")
    print("="*70 + "\n")
    
    iphone_result = generate_iphone_report()
    airpods_result = generate_airpods_report()
    
    print("\n" + "="*70)
    print("✅ All example reports generated successfully!")
    print("="*70)
    print("\nGenerated files:")
    print("  📄 reports/iphone_15_pro_analysis.md")
    print("  📄 reports/iphone_15_pro_summary.json")
    print("  📄 reports/airpods_pro_analysis.md")
    print("\nYou can view these reports to see the system output.")
