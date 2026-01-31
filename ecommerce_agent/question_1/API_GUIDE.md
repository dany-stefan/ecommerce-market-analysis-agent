# API Usage Guide

## Question 1: REST API Interface

This guide demonstrates how to interact with the Market Analysis Agent via its REST API.

---

## Quick Start

### 1. Start the API Server

#### Option A: Direct Python
```bash
python api.py
```

#### Option B: Docker (Recommended)
```bash
docker-compose up api
```

#### Option C: Docker with rebuild
```bash
docker-compose up --build api
```

The API will be available at: **http://localhost:8000**

---

## API Endpoints

### 1. Root Endpoint - Service Info

**GET** `/`

Returns service information and available endpoints.

```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "service": "E-commerce Market Analysis API",
  "version": "1.0.0",
  "status": "operational",
  "approach": "Native Python Orchestration",
  "comparison_framework": "CrewAI (commented in code)",
  "endpoints": {
    "POST /analyze": "Submit market analysis request",
    "GET /analyze/{job_id}": "Get analysis results",
    "GET /health": "Service health status",
    "GET /tools": "List available tools"
  }
}
```

---

### 2. Health Check

**GET** `/health`

Check service health and readiness.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-31T10:30:00.123456",
  "agent_ready": true,
  "tools_loaded": 3,
  "active_jobs": 0
}
```

---

### 3. List Available Tools

**GET** `/tools`

List all registered analysis tools.

```bash
curl http://localhost:8000/tools
```

**Response:**
```json
{
  "approach": "native",
  "tools": [
    "ProductCollectorTool",
    "SentimentAnalyzerTool",
    "ReportGeneratorTool"
  ],
  "count": 3
}
```

---

### 4. Analyze Product (Synchronous)

**POST** `/analyze`

Submit a market analysis request and wait for results.

#### Basic Request

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

#### Request Body Schema

```json
{
  "product_query": "string (required)",
  "analysis_depth": "quick | standard | comprehensive",
  "include_competitors": "boolean",
  "include_sentiment": "boolean"
}
```

#### Response

```json
{
  "status": "completed",
  "timestamp": "2026-01-31T10:30:15.789",
  "approach": "native_orchestration",
  "result": {
    "request": {
      "product_query": "iPhone 15 Pro",
      "analysis_depth": "comprehensive",
      "include_competitors": true,
      "include_sentiment": true
    },
    "product_data": {
      "name": "iPhone 15 Pro",
      "price": 999.99,
      "category": "Smartphones",
      "brand": "Apple",
      "availability": "In Stock",
      "specifications": {
        "display": "6.1-inch Super Retina XDR",
        "processor": "A17 Pro",
        "camera": "48MP Main Camera"
      }
    },
    "sentiment": {
      "overall_sentiment": "positive",
      "sentiment_score": 0.78,
      "positive_percentage": 68.0,
      "negative_percentage": 15.0,
      "neutral_percentage": 17.0,
      "key_themes": [
        "camera quality",
        "performance",
        "battery life"
      ],
      "review_count": 8
    },
    "competitors": [
      {
        "competitor_name": "Samsung Galaxy S24 Ultra",
        "price": 1199.99,
        "key_differentiator": "S Pen integration"
      },
      {
        "competitor_name": "Google Pixel 8 Pro",
        "price": 999.0,
        "key_differentiator": "AI photography"
      }
    ],
    "recommendations": [
      "Strong market position with premium pricing strategy",
      "Customer sentiment is predominantly positive",
      "Competitive pressure from Samsung at higher price point"
    ],
    "metadata": {
      "product_collection": "success",
      "sentiment_analysis": "success",
      "competitor_analysis": "success",
      "report_generation": "success"
    }
  }
}
```

---

### 5. Analyze Product (Asynchronous)

**POST** `/analyze/async`

Submit analysis for background processing. Returns job ID immediately.

```bash
curl -X POST http://localhost:8000/analyze/async \
  -H "Content-Type: application/json" \
  -d '{
    "product_query": "MacBook Pro M3",
    "analysis_depth": "comprehensive",
    "include_competitors": true,
    "include_sentiment": true
  }'
```

**Response:**
```json
{
  "job_id": "job_20260131_103000_123456",
  "status": "pending",
  "message": "Analysis job submitted. Check /analyze/{job_id} for results."
}
```

---

### 6. Check Job Status

**GET** `/analyze/{job_id}`

Retrieve results of an async analysis job.

```bash
curl http://localhost:8000/analyze/job_20260131_103000_123456
```

**Response (Pending):**
```json
{
  "job_id": "job_20260131_103000_123456",
  "status": "processing",
  "created_at": "2026-01-31T10:30:00.123",
  "result": null,
  "error": null
}
```

**Response (Completed):**
```json
{
  "job_id": "job_20260131_103000_123456",
  "status": "completed",
  "created_at": "2026-01-31T10:30:00.123",
  "result": { /* Full analysis result */ },
  "error": null
}
```

---

## Example Use Cases

### 1. Quick Analysis (Minimal Options)

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product_query": "AirPods Pro",
    "analysis_depth": "quick",
    "include_competitors": false,
    "include_sentiment": false
  }'
```

### 2. Full Competitive Analysis

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product_query": "Tesla Model 3",
    "analysis_depth": "comprehensive",
    "include_competitors": true,
    "include_sentiment": true
  }'
```

### 3. Sentiment-Only Analysis

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product_query": "PlayStation 5",
    "analysis_depth": "standard",
    "include_competitors": false,
    "include_sentiment": true
  }'
```

---

## Python Client Example

```python
import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000"

def analyze_product(product_query: str, comprehensive: bool = True):
    """Analyze a product via the API"""
    
    # Prepare request
    payload = {
        "product_query": product_query,
        "analysis_depth": "comprehensive" if comprehensive else "quick",
        "include_competitors": True,
        "include_sentiment": True
    }
    
    # Submit analysis
    response = requests.post(
        f"{API_BASE_URL}/analyze",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    # Check response
    if response.status_code == 200:
        result = response.json()
        return result["result"]
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

# Usage
if __name__ == "__main__":
    result = analyze_product("iPhone 15 Pro")
    
    # Access results
    print(f"Product: {result['product_data']['name']}")
    print(f"Price: ${result['product_data']['price']}")
    print(f"Sentiment: {result['sentiment']['overall_sentiment']}")
    print(f"Competitors: {len(result['competitors'])}")
    print(f"\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  - {rec}")
```

---

## JavaScript Client Example

```javascript
// Async/await example
async function analyzeProduct(productQuery, comprehensive = true) {
  const API_BASE_URL = "http://localhost:8000";
  
  const payload = {
    product_query: productQuery,
    analysis_depth: comprehensive ? "comprehensive" : "quick",
    include_competitors: true,
    include_sentiment: true
  };
  
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  
  const data = await response.json();
  return data.result;
}

// Usage
analyzeProduct("iPhone 15 Pro")
  .then(result => {
    console.log(`Product: ${result.product_data.name}`);
    console.log(`Price: $${result.product_data.price}`);
    console.log(`Sentiment: ${result.sentiment.overall_sentiment}`);
    console.log(`Competitors: ${result.competitors.length}`);
  })
  .catch(error => console.error(error));
```

---

## Interactive Documentation

The API includes interactive Swagger documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Explore all endpoints
- Test API calls directly in the browser
- View request/response schemas
- See example payloads

---

## Framework Comparison Note

### Current Implementation (Native)
```python
# Direct FastAPI endpoint
@app.post("/analyze")
async def analyze_product(request: AnalysisRequest):
    result = agent.analyze(request)
    return result
```

### CrewAI Alternative
```python
# CrewAI with built-in API
from crewai import Crew

crew = Crew(agents=[...], tasks=[...])

@app.post("/analyze")
async def analyze_product(request: dict):
    result = crew.kickoff(inputs=request)
    return result

# CrewAI benefits:
# - Automatic agent coordination
# - Built-in memory management
# - Role-based task execution
# - Less boilerplate code
```

See [FRAMEWORK_COMPARISON.md](FRAMEWORK_COMPARISON.md) for detailed comparison.

---

## Deployment Options

### Local Development
```bash
python api.py
```

### Docker (Single Container)
```bash
docker build -t market-analysis-api .
docker run -p 8000:8000 market-analysis-api
```

### Docker Compose (Recommended)
```bash
# Start API server
docker-compose up api

# Start in detached mode
docker-compose up -d api

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Production Deployment
```bash
# With Nginx reverse proxy and Redis
docker-compose --profile production up -d

# Scale API instances
docker-compose up --scale api=3
```

---

## Troubleshooting

### Port Already in Use
```bash
# Change port in docker-compose.yml
ports:
  - "8080:8000"  # Map to different host port
```

### Container Won't Start
```bash
# Check logs
docker-compose logs api

# Rebuild without cache
docker-compose build --no-cache api
```

### API Not Responding
```bash
# Check health endpoint
curl http://localhost:8000/health

# Check if container is running
docker-compose ps
```

---

## Next Steps

1. **Test the API**: Try example requests above
2. **Explore Docs**: Visit http://localhost:8000/docs
3. **Customize**: Modify analysis parameters for your use case
4. **Scale**: Use async endpoints for batch processing
5. **Deploy**: Use docker-compose for production deployment

For more information:
- [FRAMEWORK_COMPARISON.md](FRAMEWORK_COMPARISON.md) - Native vs CrewAI comparison
- [README.md](README.md) - Project overview
- [IMPLEMENTATION_STRATEGY.md](IMPLEMENTATION_STRATEGY.md) - Technical decisions
