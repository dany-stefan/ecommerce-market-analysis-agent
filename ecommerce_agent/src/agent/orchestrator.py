"""
Market Analysis Agent - Simple Orchestrator
Coordinates tools to produce market analysis reports.

ORCHESTRATION APPROACH COMPARISON:
==================================

NATIVE APPROACH (Current Implementation):
- Manual tool registration and coordination
- Direct control over execution flow and error handling
- Explicit dependency management between tools
- Full transparency in orchestration logic

CREWAI FRAMEWORK ALTERNATIVE (Commented for comparison):
- Role-based agent architecture (Product Researcher, Sentiment Analyst, Market Strategist)
- Automatic task coordination with built-in dependency resolution
- Inter-agent communication and memory sharing
- Declarative workflow definition

Framework Selection Rationale:
CrewAI was chosen for comparison because:
1. Rapid Prototyping: Best for quick implementation (5-hour assignment)
2. Role-Based Design: Natural fit for our specialized tool architecture
3. Built-in Orchestration: Simplifies multi-agent coordination
4. Market Analysis Fit: Designed for research/content pipelines like ours

However, Native Approach was selected for:
- Maximum control and transparency for technical evaluation
- No framework lock-in or learning curve
- Better demonstration of core orchestration concepts
- Easier debugging and customization
"""

from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from datetime import datetime
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger
from src.tools.base_tool import BaseTool
from src.utils.models import AnalysisRequest, AnalysisResult, CompetitorData
from src.tools.product_collector import ProductCollectorTool, ProductCollectorInput
from src.tools.sentiment_analyzer import SentimentAnalyzerTool, SentimentAnalyzerInput
from src.tools.report_generator import ReportGeneratorTool, ReportGeneratorInput
from src.utils.mock_data import MockReviewsGenerator, MockCompetitorGenerator

# ============================================================================
# CREWAI ALTERNATIVE IMPORTS (Commented - for framework comparison)
# ============================================================================
# from crewai import Agent, Task, Crew, Process
# from crewai.tools import BaseTool as CrewAIBaseTool
# from langchain.tools import Tool


class ExecutionStrategy(Enum):
    """Execution strategies for tool orchestration"""
    SEQUENTIAL = "sequential"      # Execute tools one by one
    PARALLEL = "parallel"          # Execute independent tools in parallel
    ADAPTIVE = "adaptive"          # Decide based on dependencies
    
    # CrewAI equivalent: Process.sequential, Process.parallel, Process.hierarchical


class OrchestratorConfig:
    """Configuration for orchestrator behavior"""
    
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        execution_strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL,
        enable_fallbacks: bool = True,
        enable_metrics: bool = True,
        timeout_seconds: Optional[float] = 300.0
    ):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.execution_strategy = execution_strategy
        self.enable_fallbacks = enable_fallbacks
        self.enable_metrics = enable_metrics
        self.timeout_seconds = timeout_seconds
        
    # CrewAI handles configuration automatically with sensible defaults


class MarketAnalysisAgent:
    """
    Simple agent that orchestrates tools to analyze markets.
    
    NATIVE APPROACH - Manual Orchestration:
    =======================================
    Design Decision: Keep orchestration logic simple and transparent.
    - Register tools manually
    - Decide which tools to use based on request
    - Execute tools in sequence with explicit dependency handling
    - Aggregate results with custom logic
    
    Tool Execution Flow:
    1. ProductCollector → Get product data
    2. SentimentAnalyzer → Analyze reviews (uses mock reviews)
    3. CompetitionAnalyzer → Add competitor data (mock)
    4. ReportGenerator → Synthesize everything into recommendations
    
    CREWAI ALTERNATIVE - Role-Based Multi-Agent:
    ============================================
    With CrewAI, this class would be replaced by:
    
    # 1. Define specialized agents (roles)
    product_researcher = Agent(
        role='Product Research Specialist',
        goal='Collect comprehensive product data from e-commerce platforms',
        backstory='Expert in web scraping and API integration for online marketplaces',
        tools=[ProductCollectorTool()],
        verbose=True,
        allow_delegation=False
    )
    
    sentiment_analyst = Agent(
        role='Customer Sentiment Analyst', 
        goal='Analyze customer reviews and extract actionable sentiment insights',
        backstory='Experienced NLP specialist with expertise in customer feedback analysis',
        tools=[SentimentAnalyzerTool()],
        verbose=True,
        allow_delegation=False
    )
    
    competitor_analyst = Agent(
        role='Competitive Intelligence Analyst',
        goal='Research and analyze competitor products and market positioning',
        backstory='Market research expert specializing in competitive analysis',
        tools=[CompetitorAnalysisTool()],
        verbose=True,
        allow_delegation=False
    )
    
    market_strategist = Agent(
        role='Market Strategy Advisor',
        goal='Synthesize research into strategic recommendations',
        backstory='Senior consultant with expertise in e-commerce strategy',
        tools=[ReportGeneratorTool()],
        verbose=True,
        allow_delegation=True  # Can delegate to other agents if needed
    )
    
    # 2. Define tasks with dependencies
    research_task = Task(
        description='Research product: {product_query}. Gather pricing, specs, and availability.',
        agent=product_researcher,
        expected_output='Comprehensive product data with all details'
    )
    
    sentiment_task = Task(
        description='Analyze customer sentiment for: {product_query}',
        agent=sentiment_analyst,
        expected_output='Sentiment analysis with scores, themes, and insights',
        context=[research_task]  # Depends on research
    )
    
    competitor_task = Task(
        description='Identify and analyze top 5 competitors for: {product_query}',
        agent=competitor_analyst,
        expected_output='Competitor comparison with pricing and positioning',
        context=[research_task]  # Depends on research
    )
    
    strategy_task = Task(
        description='Generate strategic recommendations based on all research',
        agent=market_strategist,
        expected_output='Executive report with actionable recommendations',
        context=[research_task, sentiment_task, competitor_task]  # Depends on all
    )
    
    # 3. Create crew with automatic orchestration
    analysis_crew = Crew(
        agents=[product_researcher, sentiment_analyst, competitor_analyst, market_strategist],
        tasks=[research_task, sentiment_task, competitor_task, strategy_task],
        process=Process.sequential,  # or Process.hierarchical for complex workflows
        verbose=True,
        memory=True,  # Enable inter-agent memory
        cache=True    # Cache results for efficiency
    )
    
    # 4. Execute (single line replaces entire analyze() method)
    result = analysis_crew.kickoff(inputs={'product_query': 'iPhone 15 Pro'})
    
    CrewAI Advantages:
    - Automatic task dependency resolution and execution order
    - Built-in memory sharing between agents
    - Role-based prompts improve LLM reasoning quality
    - Less boilerplate code (no manual tool coordination)
    - Built-in error handling and retry logic
    - Hierarchical processing for complex decision trees
    
    CrewAI Trade-offs:
    - Less granular control over execution flow
    - Framework-specific abstractions and conventions
    - Requires understanding of CrewAI's task/agent patterns
    - May be overkill for simple sequential workflows
    """
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        """
        Initialize the orchestrator with enhanced configuration
        
        Native: Manual tool registry with configuration
        CrewAI: Crew initialization with agents and tasks
        
        Args:
            config: Orchestrator configuration (defaults provided)
        """
        self.tools: Dict[str, BaseTool] = {}  # $ Core tool registry
        self.config = config or OrchestratorConfig()  # $ Configuration
        self.metrics: Dict[str, Any] = {  # $ Metrics tracking
            "total_analyses": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "tool_execution_times": {},
            "last_analysis_time": None
        }
        self._event_hooks: Dict[str, List[Callable]] = {
            "before_analysis": [],
            "after_analysis": [],
            "tool_executed": [],
            "error_occurred": []
        }
    
    def register_tool(self, tool: BaseTool):
        """
        Register a tool for use by the orchestrator with validation.
        
        Native Approach: Manual registration with dictionary storage and validation
        CrewAI Approach: Tools assigned directly to agents during initialization
        
        Args:
            tool: Instance of a tool that inherits from BaseTool
            
        Raises:
            ValueError: If tool is invalid or already registered
            
        CrewAI Alternative:
        Tools are assigned when creating agents, not registered separately:
        
        agent = Agent(
            role='Analyst',
            tools=[tool1, tool2, tool3],  # Direct assignment
            ...
        )
        """
        # Validation
        if not isinstance(tool, BaseTool):
            raise ValueError(f"Tool must inherit from BaseTool, got {type(tool)}")
        
        if tool.name in self.tools:
            logger.warning(f"Tool {tool.name} already registered, replacing...")
        
        # Health check (if tool supports it)
        try:
            if hasattr(tool, 'health_check'):
                if not tool.health_check():
                    logger.warning(f"Tool {tool.name} failed health check")
        except Exception as e:
            logger.warning(f"Health check error for {tool.name}: {e}")
        
        self.tools[tool.name] = tool  # $ REGISTER TOOL
        self.metrics["tool_execution_times"][tool.name] = []
        logger.info(f"✅ Registered tool: {tool.name}")
    
    def register_event_hook(self, event: str, callback: Callable):
        """
        Register callback for orchestrator events (extensibility hook)
        
        Native: Manual event system
        CrewAI: Built-in callbacks via agent/task configuration
        
        Args:
            event: Event name ('before_analysis', 'after_analysis', 'tool_executed', 'error_occurred')
            callback: Function to call when event occurs
        """
        if event not in self._event_hooks:
            raise ValueError(f"Unknown event: {event}")
        self._event_hooks[event].append(callback)  # $ REGISTER HOOK
        logger.debug(f"Registered hook for event: {event}")
    
    def _trigger_event(self, event: str, **kwargs):
        """
        Trigger all registered callbacks for an event
        
        Args:
            event: Event name
            **kwargs: Event data passed to callbacks
        """
        if event in self._event_hooks:
            for callback in self._event_hooks[event]:
                try:
                    callback(**kwargs)  # $ TRIGGER EVENT CALLBACK
                except Exception as e:
                    logger.error(f"Event hook error ({event}): {e}")
    
    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Main entry point: Orchestrate tools to produce market analysis.
        
        Native Approach:
        - Manual tool selection and coordination
        - Sequential execution where necessary
        - Parallel execution where possible
        - Error handling and retries
        - Result aggregation
        
        Args:
            request: What the user wants to analyze
            
        Returns:
            Complete analysis with all gathered data
        """
        start_time = time.time()
        self.metrics["total_analyses"] += 1
        
        logger.info(f"🔍 Starting analysis for: {request.product_query}")
        
        # Trigger before_analysis event
        self._trigger_event("before_analysis", request=request)
        
        # Native: Initialize result object manually
        result = AnalysisResult(request=request)
        result.metadata["start_time"] = datetime.now().isoformat()
        result.metadata["execution_strategy"] = self.config.execution_strategy.value
        
        # CrewAI: Result automatically structured by framework
        # result = self.crew.kickoff(inputs={'product_query': request.product_query})
        
        try:
            # ====================================================================
            # Tool Orchestration: Execute tools with enhanced strategy
            # CrewAI handles this automatically via task.context dependencies
            # ====================================================================
            
            if self.config.execution_strategy == ExecutionStrategy.PARALLEL:  # $
                # Execute independent tasks in parallel
                self._execute_parallel(request, result)  # $ PARALLEL EXECUTION
            else:
                # Sequential execution (default)
                self._execute_sequential(request, result)  # $ SEQUENTIAL EXECUTION
                
            self.metrics["successful_analyses"] += 1
            result.metadata["status"] = "success"
            
        except Exception as e:
            self.metrics["failed_analyses"] += 1
            result.metadata["status"] = "failed"
            result.metadata["error"] = str(e)
            logger.error(f"Analysis failed: {e}")
            self._trigger_event("error_occurred", error=e, request=request)
            raise
        finally:
            # Record execution time
            execution_time = time.time() - start_time
            result.metadata["execution_time"] = f"{execution_time:.2f}s"
            self.metrics["last_analysis_time"] = execution_time
            
            # Trigger after_analysis event
            self._trigger_event("after_analysis", result=result)
            
            logger.info(f"✅ Analysis complete in {execution_time:.2f}s")
        
        return result
    
    def _execute_sequential(self, request: AnalysisRequest, result: AnalysisResult):
        """
        Execute tools sequentially with retry logic
        
        Native: Explicit tool selection and execution with retry logic
        CrewAI: Tasks run automatically based on context dependencies
        """
        # 1. Always collect product data first (foundational data)
        # Native: Explicit tool selection and execution
        # CrewAI: research_task runs automatically first (no context dependencies)
        logger.info("📦 Step 1/4: Collecting product data...")
        product_result = self._execute_with_retry(  # $ STEP 1: PRODUCT DATA
            self._collect_product_data,
            request.product_query,
            tool_name="ProductCollectorTool"
        )
        if product_result["success"]:
            result.product_data = product_result["data"]
            result.metadata["product_collection"] = "success"
        else:
            logger.warning(f"Product collection failed: {product_result['error']}")
            result.metadata["product_collection"] = "failed"
        
        # 2. Analyze sentiment if requested (independent of product data)
        # Native: Conditional execution with if/else logic
        # CrewAI: Task conditionally included in crew based on request
        if request.include_sentiment:
            logger.info("💬 Step 2/4: Analyzing customer sentiment...")
            sentiment_result = self._execute_with_retry(  # $ STEP 2: SENTIMENT
                self._analyze_sentiment,
                request.product_query,
                tool_name="SentimentAnalyzerTool"
            )
            if sentiment_result["success"]:
                result.sentiment = sentiment_result["data"]
                result.metadata["sentiment_analysis"] = "success"
            else:
                logger.warning(f"Sentiment analysis failed: {sentiment_result['error']}")
                result.metadata["sentiment_analysis"] = "failed"
        else:
            logger.info("⏭️  Step 2/4: Skipping sentiment analysis (not requested)")
            # CrewAI: Simply don't include sentiment_task in crew initialization
        
        # 3. Get competitor data if requested
        # Native: Another conditional execution with retry
        # CrewAI: Another optional task based on inputs
        if request.include_competitors:
            logger.info("🔍 Step 3/4: Gathering competitor intelligence...")
            competitors_result = self._execute_with_retry(  # $ STEP 3: COMPETITORS
                self._get_competitors,
                request.product_query,
                tool_name="CompetitorAnalysis"
            )
            if competitors_result["success"]:
                result.competitors = competitors_result["data"]
                result.metadata["competitor_analysis"] = "success"
            else:
                logger.warning(f"Competitor analysis failed: {competitors_result['error']}")
                result.metadata["competitor_analysis"] = "failed"
        else:
            logger.info("⏭️  Step 3/4: Skipping competitor analysis (not requested)")
            # CrewAI: Conditional task inclusion
        
        # 4. Generate recommendations (depends on all previous data)
        # Native: Explicit call with aggregated result and retry
        # CrewAI: strategy_task with context=[all_previous_tasks] runs automatically
        logger.info("📊 Step 4/4: Generating strategic recommendations...")
        report_result = self._execute_with_retry(  # $ STEP 4: REPORT GENERATION
            self._generate_report,
            result,
            tool_name="ReportGeneratorTool"
        )
        if report_result["success"]:
            result.recommendations = report_result["data"].get("recommendations", [])
            result.metadata["report"] = report_result["data"]
            result.metadata["report_generation"] = "success"
        else:
            logger.warning(f"Report generation failed: {report_result['error']}")
            result.metadata["report_generation"] = "failed"
        
        # CrewAI Alternative:
        # All steps above replaced by: result = self.crew.kickoff(inputs={...})
        # CrewAI automatically:
        # - Executes tasks in dependency order
        # - Passes context between agents
        # - Handles errors with retries
        # - Aggregates results into structured output
    
    def _execute_parallel(self, request: AnalysisRequest, result: AnalysisResult):
        """
        Execute independent tools in parallel for better performance
        
        Native: Manual parallel execution with ThreadPoolExecutor
        CrewAI: Process.parallel handles this automatically
        """
        logger.info("⚡ Using parallel execution strategy")
        
        # Step 1: Product data (must go first - dependency for others)
        logger.info("📦 Step 1: Collecting product data...")
        product_result = self._execute_with_retry(
            self._collect_product_data,
            request.product_query,
            tool_name="ProductCollectorTool"
        )
        if product_result["success"]:
            result.product_data = product_result["data"]
            result.metadata["product_collection"] = "success"
        else:
            result.metadata["product_collection"] = "failed"
        
        # Step 2 & 3: Execute sentiment and competitor analysis in parallel
        # These are independent and can run concurrently
        with ThreadPoolExecutor(max_workers=2) as executor:  # $ PARALLEL EXECUTOR
            futures = {}
            
            if request.include_sentiment:
                logger.info("💬 Submitting sentiment analysis (parallel)...")
                futures[executor.submit(  # $ SUBMIT SENTIMENT (PARALLEL)
                    self._execute_with_retry,
                    self._analyze_sentiment,
                    request.product_query,
                    tool_name="SentimentAnalyzerTool"
                )] = "sentiment"
            
            if request.include_competitors:
                logger.info("🔍 Submitting competitor analysis (parallel)...")
                futures[executor.submit(  # $ SUBMIT COMPETITORS (PARALLEL)
                    self._execute_with_retry,
                    self._get_competitors,
                    request.product_query,
                    tool_name="CompetitorAnalysis"
                )] = "competitors"
            
            # Collect results as they complete
            for future in as_completed(futures):  # $ COLLECT PARALLEL RESULTS
                task_name = futures[future]
                try:
                    task_result = future.result()  # $ GET RESULT
                    
                    if task_name == "sentiment" and task_result["success"]:
                        result.sentiment = task_result["data"]
                        result.metadata["sentiment_analysis"] = "success"
                        logger.info("✅ Sentiment analysis completed (parallel)")
                    elif task_name == "competitors" and task_result["success"]:
                        result.competitors = task_result["data"]
                        result.metadata["competitor_analysis"] = "success"
                        logger.info("✅ Competitor analysis completed (parallel)")
                    else:
                        logger.warning(f"{task_name} analysis failed in parallel execution")
                        
                except Exception as e:
                    logger.error(f"Parallel task error ({task_name}): {e}")
        
        # Step 4: Generate report (depends on all previous data)
        logger.info("📊 Step 4: Generating strategic recommendations...")
        report_result = self._execute_with_retry(
            self._generate_report,
            result,
            tool_name="ReportGeneratorTool"
        )
        if report_result["success"]:
            result.recommendations = report_result["data"].get("recommendations", [])
            result.metadata["report"] = report_result["data"]
            result.metadata["report_generation"] = "success"
    
    def _execute_with_retry(
        self,
        func: Callable,
        *args,
        tool_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a function with retry logic and exponential backoff
        
        Native: Manual retry implementation
        CrewAI: Built-in retry logic with max_iter parameter
        
        Args:
            func: Function to execute
            tool_name: Name of tool for logging
            *args, **kwargs: Function arguments
            
        Returns:
            Result dictionary with success status
        """
        last_error = None
        
        for attempt in range(1, self.config.max_retries + 1):  # $ RETRY LOOP
            try:
                start_time = time.time()
                result = func(*args, **kwargs)  # $ EXECUTE FUNCTION
                execution_time = time.time() - start_time
                
                # Record metrics
                if tool_name in self.metrics["tool_execution_times"]:
                    self.metrics["tool_execution_times"][tool_name].append(execution_time)
                
                # Trigger event
                self._trigger_event("tool_executed", tool=tool_name, execution_time=execution_time)
                
                logger.debug(f"✓ {tool_name} executed in {execution_time:.2f}s")
                return result
                
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries:
                    delay = self.config.retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                    logger.warning(f"⚠️  {tool_name} failed (attempt {attempt}/{self.config.max_retries}), retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"❌ {tool_name} failed after {self.config.max_retries} attempts: {e}")
        
        # All retries exhausted
        return {
            "success": False,
            "data": None,
            "error": f"Failed after {self.config.max_retries} retries: {last_error}"
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get orchestrator performance metrics
        
        Native: Manual metrics tracking
        CrewAI: Built-in metrics via crew.usage_metrics
        
        Returns:
            Dictionary with execution metrics
        """
        metrics = self.metrics.copy()
        
        # Calculate average execution times per tool
        metrics["average_tool_times"] = {}  # $ CALCULATE AVERAGES
        for tool_name, times in self.metrics["tool_execution_times"].items():
            if times:
                metrics["average_tool_times"][tool_name] = round(sum(times) / len(times), 3)
        
        # Calculate success rate
        total = metrics["total_analyses"]
        if total > 0:
            metrics["success_rate"] = round(metrics["successful_analyses"] / total * 100, 2)  # $ SUCCESS RATE
        else:
            metrics["success_rate"] = 0.0
        
        return metrics
    
    def reset_metrics(self):
        """Reset all metrics counters"""
        self.metrics = {  # $ RESET METRICS
            "total_analyses": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "tool_execution_times": {name: [] for name in self.tools.keys()},
            "last_analysis_time": None
        }
        logger.info("Metrics reset")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on orchestrator and all tools
        
        Native: Manual health check implementation
        CrewAI: Built-in health monitoring
        
        Returns:
            Health status dictionary
        """
        health = {
            "orchestrator": "healthy",
            "tools": {},
            "timestamp": datetime.now().isoformat()
        }
        
        for tool_name, tool in self.tools.items():  # $ CHECK ALL TOOLS
            try:
                if hasattr(tool, 'health_check'):
                    tool_healthy = tool.health_check()  # $ TOOL HEALTH CHECK
                    health["tools"][tool_name] = "healthy" if tool_healthy else "unhealthy"
                else:
                    health["tools"][tool_name] = "unknown"
            except Exception as e:
                health["tools"][tool_name] = f"error: {str(e)}"
                health["orchestrator"] = "degraded"
        
        return health
    
    def _collect_product_data(self, product_query: str) -> Dict[str, Any]:
        """
        Execute product collector tool.
        
        Native: Direct tool execution with explicit input/output handling
        CrewAI: Handled by product_researcher agent executing research_task
        """
        if "ProductCollectorTool" not in self.tools:
            return {"success": False, "error": "ProductCollectorTool not registered"}
        
        tool = self.tools["ProductCollectorTool"]
        output = tool.run(ProductCollectorInput(product_query=product_query))  # $ RUN TOOL
        
        # CrewAI alternative:
        # research_task = Task(
        #     description=f'Research product: {product_query}',
        #     agent=product_researcher,
        #     expected_output='Product data including price and specs'
        # )
        # Result automatically available in subsequent tasks via context
        
        return {
            "success": output.success,
            "data": output.data,
            "error": output.error
        }
    
    def _analyze_sentiment(self, product_query: str) -> Dict[str, Any]:
        """
        Execute sentiment analyzer tool with mock reviews.
        
        Native: Manual review generation and tool execution
        CrewAI: sentiment_analyst agent executes sentiment_task with auto context
        """
        if "SentimentAnalyzerTool" not in self.tools:
            return {"success": False, "error": "SentimentAnalyzerTool not registered"}
        
        # Get mock reviews for demonstration
        reviews = MockReviewsGenerator.get_reviews_for_product(product_query, count=8)  # $ GET REVIEWS
        
        tool = self.tools["SentimentAnalyzerTool"]
        output = tool.run(SentimentAnalyzerInput(  # $ RUN SENTIMENT TOOL
            product_name=product_query,
            reviews=reviews
        ))
        
        # CrewAI alternative:
        # sentiment_task = Task(
        #     description=f'Analyze sentiment for: {product_query}',
        #     agent=sentiment_analyst,
        #     context=[research_task],  # Has access to product data
        #     expected_output='Sentiment analysis with themes and scores'
        # )
        # Agent automatically accesses review data via shared memory
        
        return {
            "success": output.success,
            "data": output.data,
            "error": output.error
        }
    
    def _get_competitors(self, product_query: str) -> Dict[str, Any]:
        """
        Get competitor data (mock for demonstration).
        
        Native: Direct mock data generation
        CrewAI: competitor_analyst agent executes competitor_task
        """
        try:
            # Use mock competitor generator
            competitors_data = MockCompetitorGenerator.get_competitors_for_product(product_query)  # $ GET COMPETITORS
            
            # Convert to CompetitorData objects
            competitors = [CompetitorData(**comp) for comp in competitors_data]  # $ CONVERT TO OBJECTS
            
            # CrewAI alternative:
            # competitor_task = Task(
            #     description=f'Research top 5 competitors for: {product_query}',
            #     agent=competitor_analyst,
            #     context=[research_task],
            #     expected_output='Competitor comparison with pricing and features'
            # )
            
            return {
                "success": True,
                "data": [comp.model_dump() for comp in competitors],
                "error": ""
            }
        except Exception as e:
            return {"success": False, "data": [], "error": str(e)}
    
    def _generate_report(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """
        Execute report generator tool.
        
        Native: Manual aggregation and tool execution
        CrewAI: market_strategist agent executes strategy_task with all context
        """
        if "ReportGeneratorTool" not in self.tools:
            return {"success": False, "error": "ReportGeneratorTool not registered"}
        
        tool = self.tools["ReportGeneratorTool"]
        output = tool.run(ReportGeneratorInput(  # $ RUN REPORT TOOL
            analysis_result=analysis_result.model_dump()
        ))
        
        # CrewAI alternative:
        # strategy_task = Task(
        #     description='Synthesize all research into strategic recommendations',
        #     agent=market_strategist,
        #     context=[research_task, sentiment_task, competitor_task],  # All deps
        #     expected_output='Executive report with actionable recommendations'
        # )
        # Agent has access to all previous task outputs via context
        
        return {
            "success": output.success,
            "data": output.data,
            "error": output.error
        }
    
    def list_tools(self) -> List[str]:
        """
        Return list of available tools.
        
        Native: Query tools dictionary
        CrewAI: Query agents list
        """
        return list(self.tools.keys())  # $ RETURN TOOL LIST
        
        # CrewAI alternative:
        # return [agent.role for agent in self.crew.agents]
