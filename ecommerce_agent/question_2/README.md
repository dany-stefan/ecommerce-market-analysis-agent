# Question 2: Testing & Observability

## Overview
Implementation of comprehensive testing strategies, monitoring, and observability features for the e-commerce agent.

## 📁 Files in This Folder

### Documentation
- **[QUESTION_2_IMPLEMENTATION_SUMMARY.md](QUESTION_2_IMPLEMENTATION_SUMMARY.md)** - Implementation summary of testing and observability features
- **[QUESTION_2_PRESENTATION_GUIDE.md](QUESTION_2_PRESENTATION_GUIDE.md)** - Presentation guide for demonstrating testing strategies

## 🎯 Key Deliverables

### 1. Unit Testing
**Location:** `../tests/test_agent.py`, `../tests/test_tools.py`

**Coverage:**
- ✅ Tool unit tests (individual tool validation)
- ✅ Orchestrator unit tests (coordination logic)
- ✅ API endpoint tests (request/response validation)
- ✅ Mock data generators for reproducible tests

**Run Tests:**
```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_agent.py -v

# With coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### 2. Integration Testing
**Location:** `../tests/integration/`

**Test Scenarios:**
- End-to-end workflow testing
- Multi-tool coordination validation
- API integration tests
- Error handling and recovery
- Performance benchmarking

**Run Integration Tests:**
```bash
python -m pytest tests/integration/ -v
```

### 3. Observability Features

#### Metrics Tracking
**Location:** `../src/agent/orchestrator.py`

**Metrics Available:**
- Total analyses performed
- Success/failure rates
- Per-tool execution times
- Average response times
- Last analysis timestamp

**Access Metrics:**
```python
metrics = agent.get_metrics()
print(f"Success rate: {metrics['success_rate']}%")
```

**API Endpoint:**
```bash
curl http://localhost:8000/metrics
```

#### Health Checks
**Location:** `../src/agent/orchestrator.py`, `../api.py`

**Health Monitoring:**
- Orchestrator health status
- Individual tool health checks
- API service status
- Active jobs tracking

**Check Health:**
```bash
curl http://localhost:8000/health
```

#### Logging
**Location:** Throughout codebase using `loguru`

**Log Levels:**
- DEBUG: Detailed execution traces
- INFO: Standard operations
- SUCCESS: Successful completions
- WARNING: Non-critical issues
- ERROR: Critical failures

**Example:**
```python
from loguru import logger

logger.info("Starting analysis...")
logger.success("Analysis complete!")
```

### 4. Performance Monitoring

#### Execution Time Tracking
```python
# Automatic timing for each tool
metrics = agent.get_metrics()
for tool, time in metrics['average_tool_times'].items():
    print(f"{tool}: {time:.3f}s")
```

#### Retry Monitoring
```python
# Track retry attempts
config = OrchestratorConfig(max_retries=3)
# Logs show: "Retry 1/3 for ToolName after 1.0s"
```

## 🧪 Testing Strategy

### Test Pyramid

```
        /\
       /  \      E2E Tests (Few)
      /    \     - Full workflow validation
     /------\    - Docker integration tests
    /        \   
   /  INTEG  \   Integration Tests (Some)
  /    TESTS  \  - Multi-tool coordination
 /____________\ - API endpoint testing

/_____________\  Unit Tests (Many)
  UNIT TESTS     - Individual tool tests
                 - Orchestrator logic tests
```

### Test Categories

#### 1. Unit Tests
**Purpose:** Validate individual components in isolation

**Examples:**
```python
def test_product_collector_tool():
    tool = ProductCollectorTool()
    result = tool.execute("iPhone 15 Pro")
    assert result["success"] == True
    assert "name" in result["data"]

def test_orchestrator_registration():
    agent = MarketAnalysisAgent()
    tool = ProductCollectorTool()
    agent.register_tool(tool)
    assert "ProductCollectorTool" in agent.list_tools()
```

#### 2. Integration Tests
**Purpose:** Validate component interactions

**Examples:**
```python
def test_full_analysis_workflow():
    agent = MarketAnalysisAgent()
    request = AnalysisRequest(product_query="Test Product")
    result = agent.analyze(request)
    assert result.product_data is not None
    assert len(result.recommendations) > 0
```

#### 3. API Tests
**Purpose:** Validate REST endpoints

**Examples:**
```python
def test_analyze_endpoint(client):
    response = client.post("/analyze", json={
        "product_query": "iPhone 15 Pro",
        "include_sentiment": True
    })
    assert response.status_code == 200
    assert "product_data" in response.json()
```

#### 4. Performance Tests
**Purpose:** Validate execution speed and resource usage

**Examples:**
```python
def test_analysis_performance():
    start = time.time()
    result = agent.analyze(request)
    duration = time.time() - start
    assert duration < 1.0  # Must complete in under 1 second
```

## 📊 Monitoring Dashboard

### Key Metrics to Monitor

| Metric | Endpoint | Description |
|--------|----------|-------------|
| Success Rate | `/metrics` | Percentage of successful analyses |
| Avg Response Time | `/metrics` | Average execution time per analysis |
| Tool Health | `/health` | Status of each registered tool |
| Active Jobs | `/health` | Number of async jobs in progress |
| Error Rate | `/metrics` | Percentage of failed analyses |

### Example Monitoring Query
```bash
# Get current metrics
curl -s http://localhost:8000/metrics | jq '{
  success_rate: .success_rate,
  total: .total_analyses,
  avg_time: .last_analysis_time
}'
```

## 🔧 Debugging Tools

### 1. Verbose Logging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. Execution Tracing
```python
# Use event hooks for tracing
def trace_execution(result):
    logger.debug(f"Tool executed: {result}")

agent.register_event_hook("tool_executed", trace_execution)
```

### 3. Performance Profiling
```python
# Profile tool execution
metrics = agent.get_metrics()
slow_tools = {
    tool: time 
    for tool, time in metrics['average_tool_times'].items()
    if time > 0.1
}
```

## 🚨 Error Handling

### Retry Logic
```python
config = OrchestratorConfig(
    max_retries=3,
    retry_delay=1.0  # Exponential backoff
)
```

### Fallback Mechanisms
```python
config = OrchestratorConfig(enable_fallbacks=True)
# Automatically uses fallback data if tools fail
```

### Error Monitoring
```python
def on_error(error):
    logger.error(f"Analysis failed: {error}")
    send_alert_to_ops()

agent.register_event_hook("error_occurred", on_error)
```

## 📈 Continuous Monitoring

### Kubernetes Health Checks
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram

analyses_total = Counter('analyses_total', 'Total analyses')
analysis_duration = Histogram('analysis_duration_seconds', 'Duration')

# Integrate with event hooks
agent.register_event_hook("after_analysis", lambda r: analyses_total.inc())
```

## 🎯 Testing Best Practices

### 1. Test Isolation
- Use fresh agent instances for each test
- Mock external dependencies
- Reset metrics between tests

### 2. Reproducibility
- Use fixed seeds for mock data
- Test with deterministic inputs
- Document test environment requirements

### 3. Coverage Goals
- Unit tests: >80% code coverage
- Integration tests: All workflows
- API tests: All endpoints

### 4. Performance Baselines
- Establish performance benchmarks
- Monitor regression in test suite
- Alert on significant slowdowns

## 📚 Additional Resources

### Testing Tools
- **pytest** - Test framework
- **pytest-cov** - Coverage reporting
- **pytest-asyncio** - Async test support
- **httpx** - API testing

### Monitoring Tools
- **loguru** - Structured logging
- **prometheus_client** - Metrics export
- **uvicorn** - ASGI server with metrics

### Documentation
- `../tests/` - Test suite location
- `../notebooks/03_testing_demo.ipynb` - Interactive testing demos
- API documentation at `/docs` (FastAPI auto-generated)

## ✅ Completion Status

- ✅ Unit test suite implemented
- ✅ Integration tests for workflows
- ✅ API endpoint tests
- ✅ Performance metrics tracking
- ✅ Health check system
- ✅ Structured logging throughout
- ✅ Error handling and retry logic
- ✅ Monitoring endpoints (/health, /metrics)

**Status:** Ready for evaluation ✨
