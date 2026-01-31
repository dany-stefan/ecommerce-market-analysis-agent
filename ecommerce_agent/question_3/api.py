"""
REST API for E-commerce Market Analysis Agent
Question 1: REST API Interface Implementation

Native Approach: Using FastAPI for direct HTTP endpoint management
Alternative Approach (commented): CrewAI with built-in API capabilities

Framework Choice Justification:
Based on the framework comparison:
┌────────────┬──────────────────────┬─────────────────────────────┬──────────────────────────┐
│ Framework  │ Best For...          │ Key Advantage               │ Typical Use Case         │
├────────────┼──────────────────────┼─────────────────────────────┼──────────────────────────┤
│ CrewAI     │ Rapid Prototyping    │ Easiest for role-based      │ Research, content        │
│            │                      │ multi-agent teams           │ pipelines                │
├────────────┼──────────────────────┼─────────────────────────────┼──────────────────────────┤
│ LangGraph  │ Surgical Control     │ Precise state management    │ Complex SaaS products    │
├────────────┼──────────────────────┼─────────────────────────────┼──────────────────────────┤
│ Google ADK │ Enterprise Scale     │ Tight Google Cloud          │ Multimodal agents,       │
│            │                      │ integration                 │ large-scale apps         │
└────────────┴──────────────────────┴─────────────────────────────┴──────────────────────────┘

CrewAI was selected for comparison because:
1. **Rapid Prototyping**: Perfect for 5-hour assignment timeline
2. **Role-Based Architecture**: Matches our tool-based agent design naturally
3. **Built-in Orchestration**: Simplifies agent coordination compared to manual orchestration
4. **Lower Learning Curve**: Easiest to demonstrate alternative implementation approach
5. **Market Analysis Fit**: Designed for research/analysis workflows like ours

However, we chose the Native Approach for:
- Maximum control and transparency for evaluation
- No framework lock-in or abstraction layers
- Easier to demonstrate technical implementation skills
- Better for understanding core orchestration concepts
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import uvicorn
from datetime import datetime
from loguru import logger
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent.orchestrator import MarketAnalysisAgent, OrchestratorConfig, ExecutionStrategy
from src.tools.sentiment_analyzer import SentimentAnalyzerTool
from src.tools.market_trend_analyzer import MarketTrendAnalyzerTool
from src.tools.report_generator import ReportGeneratorTool
from src.utils.models import AnalysisRequest, AnalysisResult
from config.settings import Settings

# ============================================================================
# NATIVE APPROACH: FastAPI REST API
# ============================================================================

app = FastAPI(
    title="E-commerce Market Analysis API",
    description="AI-powered market analysis agent for e-commerce products",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance (initialized on startup)
agent: Optional[MarketAnalysisAgent] = None
settings = Settings()

# In-memory storage for async analysis jobs (for production, use Redis/database)
analysis_jobs: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# ALTERNATIVE APPROACH: CrewAI Framework (Commented for Comparison)
# ============================================================================
"""
If using CrewAI framework, the setup would look like this:

from crewai import Agent, Task, Crew
from crewai.tools import BaseTool

# 1. Define specialized agents (CrewAI's role-based approach)
product_researcher = Agent(
    role='Product Research Specialist',
    goal='Collect comprehensive product information from e-commerce platforms',
    backstory='Expert in web scraping and data collection from online marketplaces',
    tools=[product_collector_tool],  # CrewAI tool wrapper
    verbose=True
)

sentiment_analyst = Agent(
    role='Customer Sentiment Analyst',
    goal='Analyze customer reviews and extract sentiment insights',
    backstory='Experienced in NLP and customer feedback analysis',
    tools=[sentiment_analyzer_tool],
    verbose=True
)

market_strategist = Agent(
    role='Market Strategy Advisor',
    goal='Synthesize data into actionable market recommendations',
    backstory='Senior analyst with expertise in competitive intelligence',
    tools=[report_generator_tool],
    verbose=True
)

# 2. Define tasks (CrewAI's workflow definition)
research_task = Task(
    description='Research product: {product_query}',
    agent=product_researcher,
    expected_output='Comprehensive product data including pricing and specs'
)

sentiment_task = Task(
    description='Analyze customer sentiment for {product_query}',
    agent=sentiment_analyst,
    expected_output='Sentiment analysis with scores and themes'
)

strategy_task = Task(
    description='Generate strategic recommendations',
    agent=market_strategist,
    expected_output='Market analysis report with actionable recommendations',
    context=[research_task, sentiment_task]  # Dependencies
)

# 3. Create crew (CrewAI's orchestration)
analysis_crew = Crew(
    agents=[product_researcher, sentiment_analyst, market_strategist],
    tasks=[research_task, sentiment_task, strategy_task],
    process='sequential',  # or 'hierarchical' for complex workflows
    verbose=True
)

# 4. Execute analysis (simplified API)
result = analysis_crew.kickoff(inputs={'product_query': 'iPhone 15 Pro'})

# CrewAI Advantages:
# - Automatic task coordination and dependency management
# - Built-in memory and context sharing between agents
# - Role-based prompts improve LLM reasoning
# - Less boilerplate code for agent interactions

# CrewAI Trade-offs:
# - Less control over execution flow
# - Framework-specific abstractions
# - Requires understanding of CrewAI patterns
"""


# ============================================================================
# Lifecycle Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup"""
    global agent
    
    logger.info("🚀 Initializing Market Analysis Agent...")
    
    # Native approach: Manual tool registration with enhanced config
    config = OrchestratorConfig(
        max_retries=3,
        execution_strategy=ExecutionStrategy.PARALLEL,  # Use parallel for better API performance
        enable_metrics=True,
        timeout_seconds=300.0
    )
    
    agent = MarketAnalysisAgent(config=config)
    agent.register_tool(SentimentAnalyzerTool(use_llm=False))
    agent.register_tool(MarketTrendAnalyzerTool(use_mock_data=True))
    agent.register_tool(ReportGeneratorTool(use_llm=False))
    
    logger.success(f"✅ Agent initialized with {len(agent.list_tools())} tools")
    logger.info(f"📚 Available tools: {', '.join(agent.list_tools())}")
    logger.info(f"⚙️  Execution strategy: {config.execution_strategy.value}")
    
    # CrewAI Alternative:
    # crew = Crew(agents=[...], tasks=[...])  # One-line initialization
    # logger.success("✅ CrewAI crew assembled")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Market Analysis API")


# ============================================================================
# API Endpoints - Question 1 REST Interface
# ============================================================================

@app.get("/")
async def root():
    """API health check and info"""
    return {
        "service": "E-commerce Market Analysis API",
        "version": "1.0.0",
        "status": "operational",
        "approach": "Native Python Orchestration (Enhanced)",
        "comparison_framework": "CrewAI (commented in code)",
        "features": {
            "retry_logic": "Exponential backoff with configurable retries",
            "execution_strategies": ["sequential", "parallel", "adaptive"],
            "metrics_tracking": "Built-in performance monitoring",
            "health_checks": "Orchestrator and tool-level monitoring",
            "event_hooks": "Extensible callback system"
        },
        "endpoints": {
            "POST /analyze": "Submit market analysis request (sync)",
            "POST /analyze/async": "Submit analysis for background processing",
            "GET /analyze/{job_id}": "Get async analysis results",
            "GET /health": "Service health status with metrics",
            "GET /tools": "List available tools with health status",
            "GET /metrics": "Get performance metrics",
            "POST /metrics/reset": "Reset metrics counters"
        }
    }


@app.get("/health")
async def health_check():
    """Detailed health check with metrics"""
    if not agent:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "reason": "Agent not initialized"}
        )
    
    # Get health status
    health = agent.health_check()
    
    # Add metrics
    metrics = agent.get_metrics()
    
    return {
        "status": health["orchestrator"],
        "timestamp": datetime.now().isoformat(),
        "agent_ready": agent is not None,
        "tools_loaded": len(agent.list_tools()),
        "tools_health": health["tools"],
        "active_jobs": len(analysis_jobs),
        "metrics": {
            "total_analyses": metrics["total_analyses"],
            "success_rate": metrics["success_rate"],
            "last_analysis_time": metrics["last_analysis_time"]
        }
    }


@app.get("/tools")
async def list_tools():
    """List available analysis tools"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    # Native approach: Query registered tools
    tools = agent.list_tools()
    
    # Get health status for each tool
    health = agent.health_check()
    
    # CrewAI alternative:
    # tools = [agent.role for agent in crew.agents]
    
    return {
        "approach": "native",
        "tools": tools,
        "tools_health": health["tools"],
        "count": len(tools)
    }


@app.get("/metrics")
async def get_metrics():
    """
    Get orchestrator performance metrics
    
    Native: Manual metrics tracking with custom implementation
    CrewAI: Built-in metrics via crew.usage_metrics
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    metrics = agent.get_metrics()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics,
        "approach": "native_orchestration"
    }


@app.post("/metrics/reset")
async def reset_metrics():
    """Reset all metrics counters"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    agent.reset_metrics()
    
    return {
        "status": "success",
        "message": "Metrics reset successfully",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/analyze")
async def analyze_product(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Submit a market analysis request
    
    Native Approach: Direct orchestrator call
    CrewAI Alternative: crew.kickoff(inputs={...})
    
    Args:
        request: Analysis parameters (product_query, depth, options)
        
    Returns:
        Analysis results with product data, sentiment, competitors, and recommendations
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(f"📨 Received analysis request: {request.product_query}")
        
        # ====================================================================
        # NATIVE APPROACH: Direct orchestrator execution
        # ====================================================================
        result = agent.analyze(request)
        
        # ====================================================================
        # CREWAI ALTERNATIVE (commented):
        # ====================================================================
        # result = analysis_crew.kickoff(inputs={
        #     'product_query': request.product_query,
        #     'analysis_depth': request.analysis_depth,
        #     'include_sentiment': request.include_sentiment,
        #     'include_competitors': request.include_competitors
        # })
        # 
        # CrewAI Benefits:
        # - Automatic agent coordination (no manual tool orchestration)
        # - Built-in context passing between agents
        # - Role-based prompts improve task specialization
        # 
        # CrewAI handles:
        # 1. Task dependency resolution (sequential/parallel execution)
        # 2. Inter-agent communication
        # 3. Memory management across tasks
        # 4. Error handling and retries
        # ====================================================================
        
        logger.success(f"✅ Analysis complete: {request.product_query}")
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "completed",
                "result": result.model_dump(),
                "timestamp": datetime.now().isoformat(),
                "approach": "native_orchestration"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/async")
async def analyze_product_async(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Submit analysis request for background processing
    
    Returns job_id to check status later
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    # Generate job ID
    job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    # Store job status
    analysis_jobs[job_id] = {
        "status": "pending",
        "request": request.model_dump(),
        "created_at": datetime.now().isoformat(),
        "result": None,
        "error": None
    }
    
    # Add to background tasks
    background_tasks.add_task(process_analysis, job_id, request)
    
    logger.info(f"📋 Created async job: {job_id}")
    
    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Analysis job submitted. Check /analyze/{job_id} for results."
    }


@app.get("/analyze/{job_id}")
async def get_analysis_result(job_id: str):
    """Get results of async analysis job"""
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = analysis_jobs[job_id]
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "created_at": job["created_at"],
        "result": job.get("result"),
        "error": job.get("error")
    }


# ============================================================================
# Background Task Processing
# ============================================================================

async def process_analysis(job_id: str, request: AnalysisRequest):
    """Process analysis in background"""
    try:
        analysis_jobs[job_id]["status"] = "processing"
        
        # Native approach: Execute analysis
        result = agent.analyze(request)
        
        # CrewAI alternative:
        # result = analysis_crew.kickoff(inputs={'product_query': request.product_query})
        
        analysis_jobs[job_id]["status"] = "completed"
        analysis_jobs[job_id]["result"] = result.model_dump()
        
        logger.success(f"✅ Job {job_id} completed")
        
    except Exception as e:
        analysis_jobs[job_id]["status"] = "failed"
        analysis_jobs[job_id]["error"] = str(e)
        logger.error(f"❌ Job {job_id} failed: {str(e)}")


# ============================================================================
# Entry Point
# ============================================================================

def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Start the API server"""
    logger.info(f"🌐 Starting API server on {host}:{port}")
    logger.info(f"📖 API documentation: http://{host}:{port}/docs")
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    # Development mode
    start_server(host="0.0.0.0", port=8000, reload=True)
