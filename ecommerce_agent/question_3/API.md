# Market Analysis API - Quick Start Guide

> **REST API for E-commerce Market Analysis Agent**

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# From the question_3 directory
cd question_3

# Build and start the API
docker-compose up --build

# API will be available at http://localhost:8000
```

### Option 2: Local Python

```bash
# From the question_3 directory
cd question_3

# Install dependencies (if not already done)
pip install -r ../requirements.txt

# Start the API server
python api.py
```

**API Documentation:** http://localhost:8000/docs (Interactive Swagger UI)  
**Alternative Docs:** http://localhost:8000/redoc (ReDoc format)

---

## 📡 API Endpoints

### 1. Root / Health Check
```bash
GET http://localhost:8000/
```

**Response:**
```json
{
  "service": "E-commerce Market Analysis API",
  "version": "1.0.0",
  "status": "operational",
  "approach": "Native Python Orchestration (Enhanced)",
  "features": {
    "retry_logic": "Exponential backoff with configurable retries",
    "execution_strategies": ["sequential", "parallel", "adaptive"],
    "metrics_tracking": "Built-in performance monitoring",
    "health_checks": "Orchestrator and tool-level monitoring",
    "event_hooks": "Extensible callback system"
  }
}
```

### 2. Health Check with Metrics
```bash
GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-31T15:30:00.000Z",
  "agent_ready": true,
  "tools_loaded": 3,
  "tools_health": {
    "SentimentAnalyzerTool": "healthy",
    "MarketTrendAnalyzerTool": "healthy",
    "ReportGeneratorTool": "healthy"
  },
  "active_jobs": 0,
  "metrics": {
    "total_analyses": 42,
    "success_rate": 100.0,
    "last_analysis_time": 1.234
  }
}
```

### 3. List Available Tools
```bash
GET http://localhost:8000/tools
```

**Response:**
```json
{
  "approach": "native",
  "tools": [
    "SentimentAnalyzerTool",
    "MarketTrendAnalyzerTool",
    "ReportGeneratorTool"
  ],
  "tools_health": {
    "SentimentAnalyzerTool": "healthy",
    "MarketTrendAnalyzerTool": "healthy",
    "ReportGeneratorTool": "healthy"
  },
  "count": 3
}
```

### 4. Get Performance Metrics
```bash
GET http://localhost:8000/metrics
```

**Response:**
```json
{
  "timestamp": "2026-01-31T15:30:00.000Z",
  "metrics": {
    "total_analyses": 42,
    "successful_analyses": 42,
    "failed_analyses": 0,
    "success_rate": 100.0,
    "total_tools_executed": 126,
    "tool_execution_times": {
      "SentimentAnalyzerTool": [0.123, 0.145, 0.132],
      "MarketTrendAnalyzerTool": [0.089, 0.095, 0.091],
      "ReportGeneratorTool": [0.234, 0.256, 0.241]
    },
    "average_tool_times": {
      "SentimentAnalyzerTool": 0.133,
      "MarketTrendAnalyzerTool": 0.092,
      "ReportGeneratorTool": 0.244
    },
    "last_analysis_time": 1.234
  },
  "approach": "native_orchestration"
}
```

### 5. Reset Metrics
```bash
POST http://localhost:8000/metrics/reset
```

**Response:**
```json
{
  "status": "success",
  "message": "Metrics reset successfully",
  "timestamp": "2026-01-31T15:30:00.000Z"
}
```

---

## 🔍 Market Analysis Endpoints

### 6. Analyze Product (Synchronous)

**Request:**
```bash
POST http://localhost:8000/analyze
Content-Type: application/json

{
  "product_query": "iPhone 15 Pro",
  "analysis_depth": "comprehensive",
  "include_competitors": true,
  "include_sentiment": true
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product_query": "iPhone 15 Pro",
    "analysis_depth": "comprehensive",
    "include_competitors": true,
    "include_sentiment": true
  }'
```

**Python Example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "product_query": "iPhone 15 Pro",
        "analysis_depth": "comprehensive",
        "include_competitors": True,
        "include_sentiment": True
    }
)

result = response.json()
print(f"Status: {result['status']}")
print(f"Recommendations: {len(result['result']['recommendations'])}")
```

**Response:**
```json
{
  "status": "completed",
  "result": {
    "product_data": {
      "name": "iPhone 15 Pro",
      "price": 999,
      "currency": "USD"
    },
    "sentiment": {
      "overall_sentiment": "positive",
      "sentiment_score": 0.75,
      "total_reviews": 1523,
      "key_themes": ["camera quality", "battery life", "performance"]
    },
    "competitors": [
      {
        "competitor_name": "Samsung Galaxy S24 Ultra",
        "price": 1199,
        "market_position": "premium"
      },
      {
        "competitor_name": "Google Pixel 8 Pro",
        "price": 999,
        "market_position": "premium"
      }
    ],
    "recommendations": [
      "📈 Leverage positive customer sentiment in marketing campaigns",
      "🎯 Emphasize improvements in camera quality",
      "💰 Competitive pricing advantage vs Samsung"
    ],
    "status": "success",
    "metadata": {
      "execution_time": 1.234,
      "tools_executed": 3
    }
  },
  "timestamp": "2026-01-31T15:30:00.000Z",
  "approach": "native_orchestration"
}
```

### 7. Analyze Product (Asynchronous)

For long-running analyses, submit a job and check status later:

**Submit Job:**
```bash
POST http://localhost:8000/analyze/async
Content-Type: application/json

{
  "product_query": "MacBook Pro M3",
  "analysis_depth": "comprehensive",
  "include_competitors": true,
  "include_sentiment": true
}
```

**Response:**
```json
{
  "job_id": "job_20260131_153000_123456",
  "status": "pending",
  "message": "Analysis job submitted. Check /analyze/{job_id} for results."
}
```

**Check Job Status:**
```bash
GET http://localhost:8000/analyze/job_20260131_153000_123456
```

**Response (pending):**
```json
{
  "job_id": "job_20260131_153000_123456",
  "status": "processing",
  "created_at": "2026-01-31T15:30:00.000Z",
  "result": null,
  "error": null
}
```

**Response (completed):**
```json
{
  "job_id": "job_20260131_153000_123456",
  "status": "completed",
  "created_at": "2026-01-31T15:30:00.000Z",
  "result": {
    "product_data": { ... },
    "sentiment": { ... },
    "competitors": [ ... ],
    "recommendations": [ ... ]
  },
  "error": null
}
```

---

## 📝 Request Parameters

### AnalysisRequest Schema

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `product_query` | string | ✅ Yes | - | Product name to analyze (e.g., "iPhone 15 Pro") |
| `analysis_depth` | string | ❌ No | "standard" | Analysis detail level: "quick", "standard", "comprehensive" |
| `include_competitors` | boolean | ❌ No | true | Include competitor analysis |
| `include_sentiment` | boolean | ❌ No | true | Include customer sentiment analysis |

**Example - Minimal Request:**
```json
{
  "product_query": "Sony WH-1000XM5"
}
```

**Example - Full Request:**
```json
{
  "product_query": "Sony WH-1000XM5 Headphones",
  "analysis_depth": "comprehensive",
  "include_competitors": true,
  "include_sentiment": true
}
```

---

## 🧪 Testing the API

### Using cURL

**1. Health Check:**
```bash
curl http://localhost:8000/health
```

**2. List Tools:**
```bash
curl http://localhost:8000/tools
```

**3. Analyze Product:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"product_query": "iPhone 15 Pro"}'
```

### Using Python

**test_api.py:**
```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# Test 1: Health Check
print("Testing health check...")
response = requests.get(f"{BASE_URL}/health")
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

# Test 2: Analyze Product
print("\nTesting product analysis...")
response = requests.post(
    f"{BASE_URL}/analyze",
    json={
        "product_query": "iPhone 15 Pro",
        "analysis_depth": "comprehensive",
        "include_competitors": True,
        "include_sentiment": True
    }
)
result = response.json()
print(f"Status: {result['status']}")
print(f"Product: {result['result']['product_data']['name']}")
print(f"Sentiment: {result['result']['sentiment']['overall_sentiment']}")
print(f"Recommendations: {len(result['result']['recommendations'])}")

# Test 3: Get Metrics
print("\nTesting metrics...")
response = requests.get(f"{BASE_URL}/metrics")
metrics = response.json()
print(f"Total Analyses: {metrics['metrics']['total_analyses']}")
print(f"Success Rate: {metrics['metrics']['success_rate']}%")
```

**Run tests:**
```bash
python test_api.py
```

### Using HTTPie

```bash
# Install HTTPie
pip install httpie

# Health check
http GET localhost:8000/health

# Analyze product
http POST localhost:8000/analyze \
  product_query="iPhone 15 Pro" \
  analysis_depth="comprehensive" \
  include_competitors:=true \
  include_sentiment:=true
```

---

## 🐳 Docker Commands

### Start API Server
```bash
cd question_3
docker-compose up --build
```

### Stop API Server
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f api
```

### Rebuild After Code Changes
```bash
docker-compose up --build --force-recreate
```

### Run in Background (Detached)
```bash
docker-compose up -d
```

---

## 🔧 Configuration

### Environment Variables

Set these in `docker-compose.yml` or `.env` file:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging
VERBOSE_LOGGING=true

# Orchestrator Configuration
MAX_RETRIES=3
EXECUTION_STRATEGY=parallel

# Optional: OpenAI API Key (for real LLM calls)
OPENAI_API_KEY=sk-your-key-here
```

### Custom Port

To run on a different port:

```bash
# In docker-compose.yml, change:
ports:
  - "9000:8000"  # Host port 9000 -> Container port 8000
```

---

## 📊 Performance

**Typical Response Times:**
- Health Check: ~5ms
- List Tools: ~10ms
- Product Analysis (parallel): ~1.2s
- Product Analysis (sequential): ~1.8s

**Throughput:**
- ~50 requests/second (sync endpoint)
- Limited by tool execution time, not API overhead

**Resource Usage:**
- Memory: ~150MB per container
- CPU: <5% idle, ~30% during analysis

---

## 🐛 Troubleshooting

### API Won't Start

**Error:** `Address already in use`
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process or change port in docker-compose.yml
```

**Error:** `Agent not initialized`
```bash
# Check logs for errors during startup
docker-compose logs api

# Common causes:
# - Missing dependencies
# - Import errors in src/ folder
# - Configuration issues
```

### Analysis Fails

**Check health endpoint:**
```bash
curl http://localhost:8000/health
```

**Check tool health:**
```bash
curl http://localhost:8000/tools
```

**Enable verbose logging:**
```bash
# In docker-compose.yml:
environment:
  - VERBOSE_LOGGING=true
  - LOG_LEVEL=DEBUG
```

### Docker Build Issues

```bash
# Clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

---

## 📚 Additional Resources

- **Interactive API Docs:** http://localhost:8000/docs
- **ReDoc Documentation:** http://localhost:8000/redoc
- **Question 3 README:** [README.md](./README.md)
- **Architecture Guide:** [QUESTION_3_IMPLEMENTATION_SUMMARY.md](./QUESTION_3_IMPLEMENTATION_SUMMARY.md)
- **Main Project README:** [../README.md](../README.md)

---

## 🎯 Next Steps

1. **Explore the Interactive Docs:** Visit http://localhost:8000/docs to try all endpoints
2. **Run Test Script:** Create and run test_api.py examples above
3. **Check Metrics:** Monitor performance via `/metrics` endpoint
4. **Scale Up:** Use async endpoint for high-volume processing
5. **Integrate:** Use the API in your application via REST calls

---

**Questions?** Check the troubleshooting section or review the API code in `api.py`.
