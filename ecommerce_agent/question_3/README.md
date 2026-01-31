# Question 3: REST API & Production Deployment

## Overview

Production-ready REST API implementation with comprehensive testing, Docker containerization, and deployment configurations for the e-commerce market analysis agent.

**Key Deliverables:**
- ✅ FastAPI server with 8 production endpoints
- ✅ Complete API documentation (see [API.md](./API.md))
- ✅ Docker multi-stage builds with health checks
- ✅ Docker Compose orchestration
- ✅ Comprehensive testing (unit, integration)
- ✅ Monitoring and observability

---

## 🎯 Assignment Requirements

**Task:** Demonstrate production readiness through:
- ✅ **REST API** - FastAPI with 8 endpoints, auto-docs, validation
- ✅ **API Documentation** - Complete guide with examples (API.md)
- ✅ **Docker** - Multi-stage Dockerfile, docker-compose.yml
- ✅ **Testing** - Unit tests (>85% coverage), integration tests
- ✅ **Monitoring** - Health checks, metrics tracking, logging
- ✅ **Production Features** - CORS, error handling, async processing

---

## 📡 Part 1: REST API Implementation

### 1.1 FastAPI Application

**Location:** [`api.py`](./api.py) (484 lines)

**Complete Documentation:** See [API.md](./API.md) for full endpoint descriptions, examples, and usage.

**Key Features:**
- ✅ 8 production-ready endpoints
- ✅ Automatic OpenAPI/Swagger documentation at /docs
- ✅ Request validation with Pydantic models
- ✅ CORS middleware for cross-origin requests
- ✅ Background task processing for async analysis
- ✅ Health checks and metrics endpoints
- ✅ Comprehensive error handling

**Quick Start:**
```bash
# From question_3 folder
cd question_3

# Install dependencies
pip install -r requirements.txt

# Run API server
uvicorn api:app --reload

# Test health endpoint
curl http://localhost:8000/health

# View interactive docs
open http://localhost:8000/docs
```

**8 API Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check and status |
| GET | `/metrics` | Performance metrics |
| POST | `/api/v1/analyze` | Run synchronous analysis |
| POST | `/api/v1/analyze/async` | Start async analysis job |
| GET | `/api/v1/job/{job_id}` | Check async job status |
| DELETE | `/api/v1/job/{job_id}` | Cancel async job |
| GET | `/api/v1/jobs` | List all jobs |
| GET | `/docs` | Interactive API documentation |

**Example Analysis Request:**
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product_query": "iPhone 15 Pro",
    "analysis_depth": "comprehensive",
    "include_competitors": true,
    "include_sentiment": true
  }'
```

**Tools Configuration:**
The API uses 3 specialized tools:
- `SentimentAnalyzerTool` - Rule-based or GPT-3.5-turbo sentiment analysis
- `MarketTrendAnalyzerTool` - 90-day price/popularity trends
- `ReportGeneratorTool` - Template or GPT-4 report generation (auto-saves to `reports/`)

*Note: All tools support mock mode (`use_llm=False`) for testing without API keys.*

---

## 🐳 Part 2: Docker Deployment

### 2.1 Docker Configuration

**Location:** [`Dockerfile`](./Dockerfile)

**Features:**
- ✅ Multi-stage builds (base → builder → runner)
- ✅ Optimized image size (~150MB)
- ✅ Non-root user for security
- ✅ Health checks configured
- ✅ Layer caching for fast rebuilds

**Build & Run:**
```bash
# From question_3 folder
cd question_3

# Build image
docker build -t ecommerce-agent:latest -f Dockerfile ..

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=${OPENAI_API_KEY} \
  ecommerce-agent:latest

# With volume for reports
docker run -p 8000:8000 \
  -v $(pwd)/../reports:/app/reports \
  ecommerce-agent:latest

# Check health
curl http://localhost:8000/health
```

---

### 2.2 Docker Compose Orchestration

**Location:** [`docker-compose.yml`](./docker-compose.yml)

**Services:**
- `api` - FastAPI server (port 8000)
- Volumes for `reports/` and `logs/`
- Health checks every 30s
- Auto-restart on failure

**Usage:**
```bash
# From question_3 folder
cd question_3

# Start all services
docker-compose up

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build
```

**Environment Variables:**
Create `.env` file in question_3 folder:
```bash
OPENAI_API_KEY=sk-...
LOG_LEVEL=INFO
ENABLE_METRICS=true
```

---

## 📦 Part 3: Testing

### 3.1 Unit Testing

**Location:** [`../tests/test_tools.py`](../tests/test_tools.py), [`../tests/test_agent.py`](../tests/test_agent.py)

**Coverage:**
- ✅ Tool unit tests (individual tool validation)
- ✅ Orchestrator unit tests (coordination logic)
- ✅ API endpoint tests (request/response validation)
- ✅ Mock data generators for reproducible tests

**Test Framework:** pytest + pytest-cov

**Run Tests:**
```bash
# All unit tests
python -m pytest tests/ -v

# With coverage report
python -m pytest tests/ --cov=src --cov-report=html

# View coverage
open htmlcov/index.html
```

**Test Coverage Target:** >85%
**Current Test Stats:**
- Total Tests: ~25
- Test Files: 3 (`test_tools.py`, `test_agent.py`, `test_api.py`)
- Coverage: >85%

---

### 3.2 Integration Testing

**Test Scenarios:**
- End-to-end workflow testing
- Multi-tool coordination validation
- API integration tests
- Error handling and recovery
- Performance benchmarking

---

### 3.3 Test Pyramid

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

---

## 📊 Part 4: Monitoring & Observability

### 4.1 Metrics Tracking

**Location:** [`api.py`](./api.py)

**Metrics Available:**
- Total analyses performed
- Success/failure rates
- Per-tool execution times
- Average response times
- Last analysis timestamp

**Access Metrics:**
```bash
curl http://localhost:8000/metrics

# Response:
{
  "total_analyses": 42,
  "success_count": 40,
  "failure_count": 2,
  "success_rate": 95.24,
  "avg_response_time": 1.23,
  "last_analysis": "2026-01-31T10:30:00"
}
```

---

### 4.2 Health Checks

**Location:** [`api.py`](./api.py)

**Health Monitoring:**
- Orchestrator health status
- Tool registration count (3 tools)
- API service uptime
- Last analysis timestamp

**Check Health:**
```bash
curl http://localhost:8000/health

# Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "tools_registered": 3,
  "uptime_seconds": 3600,
  "last_analysis": "2026-01-31T10:30:00",
  "timestamp": "2026-01-31T10:40:00"
}
```

---

### 4.3 Logging

**Framework:** loguru

**Log Levels:**
- DEBUG: Detailed execution traces
- INFO: Standard operations
- SUCCESS: Successful completions
- WARNING: Non-critical issues
- ERROR: Critical failures

**Example:**
```python
from loguru import logger

logger.info("Starting analysis for {product}", product="iPhone 15 Pro")
logger.success("Analysis complete in {time:.2f}s", time=2.3)
logger.error("Failed to connect to API: {error}", error=str(e))
```

---

## 🚀 Part 5: Production Features

### 5.1 Async Processing

**Background Jobs:**
- Start async analysis with `/api/v1/analyze/async`
- Check job status with `/api/v1/job/{job_id}`
- Cancel running jobs with DELETE request
- List all jobs with `/api/v1/jobs`

**Example:**
```bash
# Start async job
curl -X POST http://localhost:8000/api/v1/analyze/async \
  -H "Content-Type: application/json" \
  -d '{"product_query": "iPhone 15 Pro"}'

# Response:
{"job_id": "abc123", "status": "pending"}

# Check status
curl http://localhost:8000/api/v1/job/abc123
```

---

### 5.2 Error Handling

**Features:**
- Global exception handlers
- Pydantic validation errors
- Custom error responses with details
- Retry logic for transient failures

---

### 5.3 CORS Support

**Configuration:**
```python
# CORS middleware enabled for cross-origin requests
origins = ["*"]  # Configure for production
```

---

## 📚 Documentation

- **API Documentation**: [API.md](./API.md) - Complete API reference with examples
- **Root Quick Start**: [../QUICKSTART.md](../QUICKSTART.md) - Multiple ways to run the project
- **Architecture**: [../question_1/README.md](../question_1/README.md) - Agent orchestration details
- **Tools**: [../question_2/README.md](../question_2/README.md) - Tool implementation details

---

## ✅ Production Readiness Checklist

- [x] FastAPI with 8 production endpoints
- [x] Interactive API documentation (/docs, /redoc)
- [x] Request validation with Pydantic
- [x] Health checks and metrics
- [x] Docker multi-stage builds
- [x] Docker Compose orchestration
- [x] Unit tests with >85% coverage
- [x] Integration test strategies
- [x] Logging with loguru
- [x] CORS middleware
- [x] Error handling
- [x] Async job processing
- [x] Auto-save reports to files
- [x] Mock mode for testing without APIs

---

## 🔗 Quick Links

- **API Documentation**: [API.md](./API.md)
- **Root QUICKSTART**: [../QUICKSTART.md](../QUICKSTART.md)
- **Dockerfile**: [Dockerfile](./Dockerfile)
- **docker-compose.yml**: [docker-compose.yml](./docker-compose.yml)
- **API Server**: [api.py](./api.py)

---

## 📝 Next Steps

1. **Deploy to Production**: Use Docker Compose with environment variables
2. **Add Redis**: Replace in-memory job storage with Redis
3. **Add Database**: Store analysis history in PostgreSQL
4. **Add Load Balancer**: Use nginx for multiple API instances
5. **Add Monitoring**: Integrate Prometheus + Grafana
6. **Add CI/CD**: GitHub Actions for automated testing and deployment

---

*See [API.md](./API.md) for complete API documentation with examples.*
