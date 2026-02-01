"""
E-commerce Market Analysis REST API

Production-ready FastAPI server with comprehensive endpoints for market analysis.

Features:
- Synchronous and asynchronous analysis endpoints
- Health monitoring and metrics
- Tool management
- Request validation with Pydantic
- Error handling and logging
- CORS support
- API documentation with Swagger UI

Start with: python api.py
Docs: http://localhost:8000/docs
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import uvicorn
from loguru import logger

# Import agent components
import sys
sys.path.append('..')
from src.agent.orchestrator import MarketAnalysisAgent, OrchestratorConfig, ExecutionStrategy
from src.tools.sentiment_analyzer import SentimentAnalyzerTool
from src.tools.market_trend_analyzer import MarketTrendAnalyzerTool
from src.tools.report_generator import ReportGeneratorTool
from src.tools.product_collector import ProductCollectorTool
from src.utils.models import AnalysisRequest, AnalysisResult


# Pydantic models for API requests/responses
class APIAnalysisRequest(BaseModel):
    """API request model with validation"""
    product_query: str = Field(..., min_length=1, max_length=200, description="Product to analyze")
    analysis_depth: str = Field(default="standard", regex="^(quick|standard|comprehensive)$")
    include_competitors: bool = Field(default=True)
    include_sentiment: bool = Field(default=True)
    execution_strategy: str = Field(default="parallel", regex="^(sequential|parallel)$")
    
    @validator('product_query')
    def validate_product_query(cls, v):
        if not v.strip():
            raise ValueError('Product query cannot be empty')
        return v.strip()


class APIAnalysisResponse(BaseModel):
    """API response model"""
    status: str
    timestamp: str
    approach: str = "native_orchestration"
    execution_time: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    job_id: Optional[str] = None
    message: Optional[str] = None


class APIHealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    agent_ready: bool
    tools_loaded: int
    tools_health: Dict[str, str]
    active_jobs: int
    metrics: Dict[str, Any]


class APIToolsResponse(BaseModel):
    """Tools listing response model"""
    approach: str
    tools: List[str]
    tool_details: Dict[str, Dict[str, str]]


class APIMetricsResponse(BaseModel):
    """Metrics response model"""
    total_analyses: int
    successful_analyses: int
    failed_analyses: int
    success_rate: float
    average_execution_time: Optional[float] = None
    tool_performance: Dict[str, float]
    last_analysis_time: Optional[float] = None
    uptime_seconds: float


class AsyncJobStatus(BaseModel):
    """Async job status model"""
    job_id: str
    status: str  # pending, processing, completed, failed
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    progress: Optional[str] = None


# Global app state
class AppState:
    def __init__(self):
        self.agent: Optional[MarketAnalysisAgent] = None
        self.async_jobs: Dict[str, AsyncJobStatus] = {}
        self.start_time: datetime = datetime.now()
        
    def get_uptime(self) -> float:
        return (datetime.now() - self.start_time).total_seconds()


app_state = AppState()


# FastAPI app initialization
app = FastAPI(
    title="E-commerce Market Analysis API",
    description="Production-ready API for comprehensive market analysis using specialized AI tools",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": str(exc)}
    )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize the agent and tools on startup"""
    logger.info("🚀 Starting E-commerce Market Analysis API")
    
    try:
        # Create optimized configuration for API usage
        config = OrchestratorConfig(
            execution_strategy=ExecutionStrategy.PARALLEL,  # Default to parallel for API
            max_retries=3,
            retry_delay=1.0,
            enable_metrics=True,
            timeout_seconds=120.0  # 2-minute timeout for API requests
        )
        
        # Initialize agent
        app_state.agent = MarketAnalysisAgent(config=config)
        
        # Register all tools
        app_state.agent.register_tool(SentimentAnalyzerTool())
        app_state.agent.register_tool(MarketTrendAnalyzerTool())
        app_state.agent.register_tool(ReportGeneratorTool())
        app_state.agent.register_tool(ProductCollectorTool())
        
        logger.info(f"✅ Initialized agent with {len(app_state.agent.tools)} tools")
        logger.info(f"📊 Available tools: {', '.join(app_state.agent.list_tools())}")
        
        # Perform health check
        health = app_state.agent.health_check()
        logger.info(f"🏥 System health: {health['orchestrator']}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🔄 Shutting down E-commerce Market Analysis API")
    
    # Cancel any pending async jobs
    for job_id, job in app_state.async_jobs.items():
        if job.status in ["pending", "processing"]:
            job.status = "cancelled"
            logger.info(f"📋 Cancelled job: {job_id}")


# API endpoints
@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint - API information and features"""
    return {
        "service": "E-commerce Market Analysis API",
        "version": "1.0.0",
        "status": "operational",
        "approach": "Native Python Orchestration (Enhanced)",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "api_guide": "../question_3/API.md"
        },
        "features": {
            "retry_logic": "Exponential backoff with configurable retries",
            "execution_strategies": ["sequential", "parallel", "adaptive"],
            "metrics_tracking": "Built-in performance monitoring",
            "health_checks": "Orchestrator and tool-level monitoring",
            "event_hooks": "Extensible callback system",
            "async_processing": "Background job support"
        },
        "endpoints": {
            "health": "/health",
            "tools": "/tools",
            "metrics": "/metrics",
            "analyze_sync": "/analyze",
            "analyze_async": "/analyze/async",
            "job_status": "/analyze/{job_id}"
        }
    }


@app.get("/health", response_model=APIHealthResponse)
async def health_check():
    """Health check endpoint with detailed system status"""
    if not app_state.agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    # Get system health
    health = app_state.agent.health_check()
    metrics = app_state.agent.get_metrics()
    
    # Count active async jobs
    active_jobs = len([j for j in app_state.async_jobs.values() 
                      if j.status in ["pending", "processing"]])
    
    return APIHealthResponse(
        status="healthy" if health["orchestrator"] == "healthy" else "degraded",
        timestamp=datetime.now().isoformat(),
        agent_ready=True,
        tools_loaded=len(app_state.agent.tools),
        tools_health=health["tools"],
        active_jobs=active_jobs,
        metrics={
            "total_analyses": metrics["total_analyses"],
            "success_rate": metrics["success_rate"],
            "last_analysis_time": metrics["last_analysis_time"]
        }
    )


@app.get("/tools", response_model=APIToolsResponse)
async def list_tools():
    """List all available analysis tools with descriptions"""
    if not app_state.agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    tools = app_state.agent.list_tools()
    
    # Get tool descriptions
    tool_details = {}
    for tool_name in tools:
        tool = app_state.agent.tools[tool_name]
        tool_details[tool_name] = {
            "name": tool_name,
            "description": tool.description if hasattr(tool, 'description') else "Analysis tool",
            "status": "ready"
        }
    
    return APIToolsResponse(
        approach="native",
        tools=tools,
        tool_details=tool_details
    )


@app.get("/metrics", response_model=APIMetricsResponse)
async def get_metrics():
    """Get comprehensive system metrics"""
    if not app_state.agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    metrics = app_state.agent.get_metrics()
    
    return APIMetricsResponse(
        total_analyses=metrics["total_analyses"],
        successful_analyses=metrics["successful_analyses"],
        failed_analyses=metrics["failed_analyses"],
        success_rate=metrics["success_rate"],
        tool_performance=metrics.get("average_tool_times", {}),
        last_analysis_time=metrics["last_analysis_time"],
        uptime_seconds=app_state.get_uptime()
    )


@app.post("/metrics/reset")
async def reset_metrics():
    """Reset all metrics counters"""
    if not app_state.agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    app_state.agent.reset_metrics()
    
    return {
        "status": "success",
        "message": "Metrics reset successfully",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/analyze", response_model=APIAnalysisResponse)
async def analyze_product(request: APIAnalysisRequest):
    """Synchronous product analysis endpoint"""
    if not app_state.agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    logger.info(f"🔍 Analysis request: {request.product_query}")
    
    try:
        # Convert API request to internal format
        internal_request = AnalysisRequest(
            product_query=request.product_query,
            analysis_depth=request.analysis_depth,
            include_competitors=request.include_competitors,
            include_sentiment=request.include_sentiment
        )
        
        # Configure execution strategy
        if request.execution_strategy == "sequential":
            app_state.agent.config.execution_strategy = ExecutionStrategy.SEQUENTIAL
        else:
            app_state.agent.config.execution_strategy = ExecutionStrategy.PARALLEL
        
        # Execute analysis
        start_time = datetime.now()
        result = app_state.agent.analyze(internal_request)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"✅ Analysis completed in {execution_time:.2f}s")
        
        return APIAnalysisResponse(
            status="completed",
            timestamp=datetime.now().isoformat(),
            execution_time=execution_time,
            result=result.model_dump()
        )
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/async", response_model=APIAnalysisResponse)
async def analyze_product_async(request: APIAnalysisRequest, background_tasks: BackgroundTasks):
    """Asynchronous product analysis endpoint"""
    if not app_state.agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Create job status record
    job_status = AsyncJobStatus(
        job_id=job_id,
        status="pending",
        created_at=datetime.now().isoformat()
    )
    
    app_state.async_jobs[job_id] = job_status
    
    # Add background task
    background_tasks.add_task(process_async_analysis, job_id, request)
    
    logger.info(f"📋 Async analysis submitted: {job_id} for {request.product_query}")
    
    return APIAnalysisResponse(
        status="accepted",
        timestamp=datetime.now().isoformat(),
        job_id=job_id,
        message=f"Analysis job submitted. Check status at /analyze/{job_id}"
    )


@app.get("/analyze/{job_id}", response_model=AsyncJobStatus)
async def get_analysis_status(job_id: str):
    """Get status of asynchronous analysis job"""
    if job_id not in app_state.async_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return app_state.async_jobs[job_id]


# Background task for async processing
async def process_async_analysis(job_id: str, request: APIAnalysisRequest):
    """Process analysis in background"""
    job = app_state.async_jobs[job_id]
    
    try:
        job.status = "processing"
        job.progress = "Starting analysis..."
        
        logger.info(f"🔄 Processing async job: {job_id}")
        
        # Convert API request to internal format
        internal_request = AnalysisRequest(
            product_query=request.product_query,
            analysis_depth=request.analysis_depth,
            include_competitors=request.include_competitors,
            include_sentiment=request.include_sentiment
        )
        
        # Configure execution strategy
        if request.execution_strategy == "sequential":
            app_state.agent.config.execution_strategy = ExecutionStrategy.SEQUENTIAL
        else:
            app_state.agent.config.execution_strategy = ExecutionStrategy.PARALLEL
        
        # Execute analysis
        result = app_state.agent.analyze(internal_request)
        
        # Update job status
        job.status = "completed"
        job.completed_at = datetime.now().isoformat()
        job.result = result.model_dump()
        job.progress = "Analysis completed successfully"
        
        logger.info(f"✅ Async job completed: {job_id}")
        
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        job.completed_at = datetime.now().isoformat()
        job.progress = f"Analysis failed: {str(e)}"
        
        logger.error(f"❌ Async job failed: {job_id} - {str(e)}")


# Development server startup
if __name__ == "__main__":
    logger.info("🚀 Starting E-commerce Market Analysis API server")
    logger.info("📚 API Documentation: http://localhost:8000/docs")
    logger.info("🔧 Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
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
