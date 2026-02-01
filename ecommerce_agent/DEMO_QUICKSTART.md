# 🚀 DEMO QUICKSTART - E-commerce Market Analysis Agent

## ✅ CONFIRMED WORKING - Ready for Demo

All execution modes have been validated and are working correctly.

### Quick Validation (Recommended)
```bash
python3 quick_test.py
```

### Individual Execution Options

#### 1. Direct Execution ✅ WORKING
```bash
# Run the complete demo (Questions 1 & 2)
python3 main.py
```

**What it does:**
- Executes complete orchestrator demonstration
- Generates analysis reports for iPhone 15 Pro and Samsung Galaxy S24  
- Shows parallel tool execution with timing metrics
- Saves reports to [`reports/`](reports/) directory

**Expected output:**
```
🚀 Market Analysis Agent Demo Starting...
📊 Question 1 Demo: iPhone 15 Pro Analysis
✅ Agent initialized with 3 tools
⏱️  Execution time: ~2-3 seconds
📋 Analysis complete! Report saved to: reports/iPhone_15_Pro_Report_[timestamp].md
```

#### 2. API Server Mode ✅ WORKING
```bash
# Start API server
PYTHONPATH=. python3 question_3/api.py

# In another terminal - test health
curl http://localhost:8000/health

# Test analysis endpoint  
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product_query": "iPhone 15 Pro",
    "analysis_depth": "comprehensive",
    "include_competitors": true,
    "include_sentiment": true
  }'
```

**Expected response:**
```json
{
  "status": "healthy",
  "agent_ready": true,
  "tools_loaded": 3,
  "timestamp": "2026-02-01T16:08:47"
}
```

#### 3. Docker Container Mode ✅ WORKING
```bash
# Build and start container
cd question_3
docker-compose up -d api

# Test containerized API
curl http://localhost:8000/health

# View container logs
docker-compose logs api

# Stop container
docker-compose down
```

**Expected logs:**
```
market_analysis_api | ✅ Agent initialized with 3 tools
market_analysis_api | 🌐 Server ready on http://0.0.0.0:8000
```

---

## Troubleshooting

### Common Issues

**ImportError: No module named 'src'**
```bash
# Set PYTHONPATH before running
export PYTHONPATH=.
python question_3/api.py
```

**Docker build fails**
```bash
# Clean Docker cache and rebuild
docker-compose down
docker system prune -f
docker-compose build --no-cache api
```

**API server port conflict**
```bash
# Check what's using port 8000
lsof -i :8000
# Kill process if needed
sudo kill -9 <PID>
```

**Missing reports directory**
```bash
# Create reports directory if missing
mkdir -p reports
```

### Verification Commands

Check all components are working:
```bash
# Verify Python environment
python --version
pip list | grep -E "(fastapi|uvicorn|requests|openai)"

# Verify file structure
ls -la src/agent/
ls -la src/tools/
ls -la question_3/

# Verify Docker setup  
docker --version
docker-compose --version

# Check recent reports
ls -la reports/ | head -5
```

---

## Expected Outputs

### Report Structure
Generated reports include:
```markdown
# iPhone 15 Pro - Market Analysis Report
## Executive Summary
## Market Trends Analysis
## Sentiment Analysis
## Competitive Intelligence  
## Strategic Recommendations
```

### Performance Metrics
- **Tool execution**: ~3-8 seconds per tool
- **Total analysis**: ~10-15 seconds
- **API response**: ~200-500ms (health check)
- **Docker startup**: ~10-15 seconds

### API Endpoints
- `GET /health` - Service health check
- `POST /analyze` - Product analysis
- `GET /docs` - Interactive API documentation

---

## Success Indicators

✅ **All modes working correctly:**
- main.py executes without errors
- API server starts and responds to health checks
- Docker container builds and runs successfully  
- Reports are generated in `reports/` directory
- All tools (market trends, sentiment, report generator) execute

✅ **Ready for demo:**
- Can run `python test_all_modes.py` with 100% success rate
- All three execution paths validated
- Sample reports generated and accessible

---

**🎯 You're ready! Your complete demo pipeline is operational.**