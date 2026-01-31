# Quick Start: Using the Refined Orchestrator

## Basic Usage

### 1. **Default Configuration (Sequential Execution)**

```python
from src.agent.orchestrator import MarketAnalysisAgent
from src.utils.models import AnalysisRequest

# Initialize with defaults
agent = MarketAnalysisAgent()

# Run analysis
request = AnalysisRequest(
    product_query="iPhone 15 Pro",
    include_sentiment=True,
    include_competitors=True
)

result = agent.analyze(request)
print(f"Analysis complete: {result.product_data['name']}")
```

---

### 2. **Parallel Execution for Performance**

```python
from src.agent.orchestrator import MarketAnalysisAgent, OrchestratorConfig, ExecutionStrategy

# Configure for parallel execution
config = OrchestratorConfig(
    execution_strategy=ExecutionStrategy.PARALLEL,
    enable_metrics=True
)

agent = MarketAnalysisAgent(config=config)

# Sentiment and competitor analysis run in parallel
result = agent.analyze(request)

# Check metrics
metrics = agent.get_metrics()
print(f"Execution time: {metrics['last_analysis_time']}s")
print(f"Success rate: {metrics['success_rate']}%")
```

---

### 3. **Custom Retry Configuration**

```python
# Configure retries for unreliable networks
config = OrchestratorConfig(
    max_retries=5,        # Try 5 times
    retry_delay=2.0,      # Start with 2s delay
    timeout_seconds=600.0 # 10 minute timeout
)

agent = MarketAnalysisAgent(config=config)

# Retries happen automatically with exponential backoff
result = agent.analyze(request)
```

---

### 4. **Using Event Hooks**

```python
# Define custom callbacks
def log_start(request):
    print(f"Starting analysis: {request.product_query}")

def log_complete(result):
    print(f"Analysis complete with {len(result.recommendations)} recommendations")

def on_error(error):
    print(f"Error occurred: {error}")

# Register hooks
agent.register_event_hook("before_analysis", log_start)
agent.register_event_hook("after_analysis", log_complete)
agent.register_event_hook("error_occurred", on_error)

# Run analysis - hooks fire automatically
result = agent.analyze(request)
```

---

### 5. **Monitoring Health and Metrics**

```python
# Check orchestrator health
health = agent.health_check()
print(f"Orchestrator: {health['orchestrator']}")
print(f"Tools: {health['tools']}")

# Get performance metrics
metrics = agent.get_metrics()
print(f"Total analyses: {metrics['total_analyses']}")
print(f"Success rate: {metrics['success_rate']}%")

# Per-tool execution times
for tool, time in metrics['average_tool_times'].items():
    print(f"{tool}: {time:.3f}s")

# Reset metrics (useful for testing)
agent.reset_metrics()
```

---

## API Usage

### Start the Server

```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8000
```

### Test Endpoints

```bash
# Check API info and features
curl http://localhost:8000/

# Health check with metrics
curl http://localhost:8000/health

# Get performance metrics
curl http://localhost:8000/metrics

# Submit analysis (parallel execution by default)
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product_query": "iPhone 15 Pro",
    "include_sentiment": true,
    "include_competitors": true,
    "analysis_depth": "standard"
  }'

# Reset metrics
curl -X POST http://localhost:8000/metrics/reset
```

---

## Configuration Options

### OrchestratorConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_retries` | int | 3 | Maximum retry attempts for failed tool executions |
| `retry_delay` | float | 1.0 | Initial delay in seconds (exponential backoff) |
| `execution_strategy` | ExecutionStrategy | SEQUENTIAL | Tool execution mode |
| `enable_fallbacks` | bool | True | Enable fallback mechanisms |
| `enable_metrics` | bool | True | Track performance metrics |
| `timeout_seconds` | float | 300.0 | Overall analysis timeout |

### ExecutionStrategy Options

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `SEQUENTIAL` | Execute tools one by one | Default, safe, easier debugging |
| `PARALLEL` | Run independent tools concurrently | Performance-critical applications |
| `ADAPTIVE` | Dynamically choose strategy | Future enhancement |

---

## Performance Tuning

### For Maximum Speed
```python
config = OrchestratorConfig(
    execution_strategy=ExecutionStrategy.PARALLEL,
    max_retries=1,           # Fail fast
    timeout_seconds=30.0     # Shorter timeout
)
```

### For Maximum Reliability
```python
config = OrchestratorConfig(
    execution_strategy=ExecutionStrategy.SEQUENTIAL,
    max_retries=5,           # More retries
    retry_delay=2.0,         # Longer delays
    timeout_seconds=600.0    # Extended timeout
)
```

### For Production Balance
```python
config = OrchestratorConfig(
    execution_strategy=ExecutionStrategy.PARALLEL,
    max_retries=3,
    retry_delay=1.0,
    timeout_seconds=300.0,
    enable_metrics=True
)
```

---

## Testing

### Run CLI Demo
```bash
python main.py
```

### Run API Tests
```bash
# Terminal 1: Start server
python -m uvicorn api:app --port 8000

# Terminal 2: Run tests
python -m pytest tests/test_agent.py -v
```

### Docker Deployment
```bash
# Build image
docker build -t ecommerce-agent .

# Run API service
docker-compose up api

# Run batch analysis
docker-compose up batch
```

---

## Monitoring in Production

### Health Check Endpoint
```bash
# Kubernetes liveness probe
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "tools_health": {"...": "healthy"},
  "metrics": {
    "success_rate": 100.0
  }
}
```

### Metrics Collection
```bash
# Prometheus-compatible metrics
curl http://localhost:8000/metrics

# Export to monitoring system
curl http://localhost:8000/metrics | jq '.success_rate'
```

---

## Troubleshooting

### Issue: Low Success Rate
```python
# Check metrics
metrics = agent.get_metrics()
print(f"Failed: {metrics['failed_analyses']}")

# Increase retries
config.max_retries = 5
```

### Issue: Slow Performance
```python
# Check per-tool times
metrics = agent.get_metrics()
slow_tools = {
    tool: time 
    for tool, time in metrics['average_tool_times'].items()
    if time > 1.0
}
print(f"Slow tools: {slow_tools}")

# Switch to parallel execution
config.execution_strategy = ExecutionStrategy.PARALLEL
```

### Issue: Tool Failures
```python
# Check health
health = agent.health_check()
unhealthy = [
    tool for tool, status in health['tools'].items()
    if status != "healthy"
]
print(f"Unhealthy tools: {unhealthy}")
```

---

## Best Practices

### 1. **Always Enable Metrics in Production**
```python
config = OrchestratorConfig(enable_metrics=True)
```

### 2. **Use Parallel Execution for API Services**
```python
# API handles multiple concurrent requests
config = OrchestratorConfig(execution_strategy=ExecutionStrategy.PARALLEL)
```

### 3. **Use Sequential for Debugging**
```python
# Easier to trace issues
config = OrchestratorConfig(execution_strategy=ExecutionStrategy.SEQUENTIAL)
```

### 4. **Monitor Health Regularly**
```python
# Check every minute in production
health = agent.health_check()
if health['orchestrator'] != 'healthy':
    alert_ops_team()
```

### 5. **Reset Metrics Periodically**
```python
# Reset daily for fresh statistics
if datetime.now().hour == 0:
    agent.reset_metrics()
```

---

## Integration Examples

### With Logging
```python
import logging

def log_analysis(result):
    logging.info(f"Analysis complete: {result.product_data['name']}")

agent.register_event_hook("after_analysis", log_analysis)
```

### With Monitoring (Prometheus)
```python
from prometheus_client import Counter, Histogram

analysis_counter = Counter('analyses_total', 'Total analyses')
analysis_duration = Histogram('analysis_duration_seconds', 'Analysis duration')

def track_metrics(result):
    analysis_counter.inc()
    analysis_duration.observe(result.metadata['execution_time'])

agent.register_event_hook("after_analysis", track_metrics)
```

### With Alerting
```python
def check_failures(result):
    if result.metadata.get('status') == 'failed':
        send_alert(f"Analysis failed: {result.metadata.get('error')}")

agent.register_event_hook("error_occurred", check_failures)
```

---

## CrewAI Comparison

### Native Approach (Current)
```python
# Explicit, transparent, full control
agent = MarketAnalysisAgent(config=config)
agent.register_tool(ProductCollectorTool())
result = agent.analyze(request)
```

### CrewAI Alternative
```python
# Declarative, automatic, rapid
from crewai import Agent, Task, Crew

crew = Crew(
    agents=[product_agent, sentiment_agent],
    tasks=[product_task, sentiment_task],
    process=Process.parallel
)
result = crew.kickoff(inputs={'product_query': '...'})
```

**When to use Native:** Production systems, custom requirements, full control  
**When to use CrewAI:** Rapid prototyping, standard workflows, quick demos

---

## Support

For issues or questions:
1. Check logs: `logger.debug()` messages throughout orchestrator
2. Review metrics: `agent.get_metrics()`
3. Check health: `agent.health_check()`
4. See documentation: [README.md](README.md)
5. Review code: [src/agent/orchestrator.py](src/agent/orchestrator.py)
