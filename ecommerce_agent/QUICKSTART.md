# Quick Start Guide

> **Get the E-Commerce Market Analysis Agent running in under 5 minutes.**

---

## � **LLM Configuration (Optional - Real AI Analysis)**

**By default, the system runs in MOCK MODE with simulated data - no API keys required.**

### To Use Real OpenAI GPT Models:

#### 1. **Get Your OpenAI API Key**
- Visit [OpenAI Platform](https://platform.openai.com/api-keys)  
- Create an API key (format: `sk-...`)

#### 2. **Set Your API Key**
Choose ONE of these methods:

**Method A: Environment Variable (Recommended)**
```bash
export OPENAI_API_KEY="sk-your-actual-api-key-here"
```

**Method B: Create .env File**
```bash
# Create .env file in project root
echo "OPENAI_API_KEY=sk-your-actual-api-key-here" > .env
```

#### 3. **Enable LLM Mode in main.py**
Edit `main.py` and change these lines:

**BEFORE (Mock Mode - Default):**
```python
# Line 41 - Sentiment Analysis (Mock Mode)
agent.register_tool(SentimentAnalyzerTool(use_llm=False))
# Line 42 - Market Trends (Mock Data - Keep as is)
agent.register_tool(MarketTrendAnalyzerTool(use_mock_data=True))
# Line 43 - Report Generator (Mock Mode)
agent.register_tool(ReportGeneratorTool(use_llm=False))

# Line 124 - Individual tool demos
sentiment_tool = SentimentAnalyzerTool(use_llm=False)
# Line 152
trend_tool = MarketTrendAnalyzerTool(use_mock_data=True)
# Line 177
report_tool = ReportGeneratorTool(use_llm=False)
```

**AFTER (LLM Mode - Real OpenAI Analysis):**
```python
# Line 41 - Sentiment Analysis (Real GPT-3.5)
agent.register_tool(SentimentAnalyzerTool(use_llm=True))
# Line 42 - Market Trends (Keep mock data - no API needed)
agent.register_tool(MarketTrendAnalyzerTool(use_mock_data=True))
# Line 43 - Report Generator (Real GPT-4)
agent.register_tool(ReportGeneratorTool(use_llm=True))

# Line 124 - Individual tool demos  
sentiment_tool = SentimentAnalyzerTool(use_llm=True)
# Line 152 - Keep as mock (no market data APIs configured)
trend_tool = MarketTrendAnalyzerTool(use_mock_data=True)
# Line 177
report_tool = ReportGeneratorTool(use_llm=True)
```

**⚡ Quick Find & Replace:**
1. Search: `SentimentAnalyzerTool(use_llm=False)`
2. Replace: `SentimentAnalyzerTool(use_llm=True)`
3. Search: `ReportGeneratorTool(use_llm=False)`  
4. Replace: `ReportGeneratorTool(use_llm=True)`
5. Save file

**Note:** Keep `MarketTrendAnalyzerTool(use_mock_data=True)` unchanged - it uses realistic simulated data and doesn't need API keys.

#### 4. **Run Analysis with Real AI**
```bash
python main.py
```

**✅ Success Indicators:**
- No "mock mode" messages in output
- Analysis takes longer (5-15 seconds vs <1 second)
- More sophisticated sentiment analysis results  
- Strategic recommendations use business language
- Report generation shows "Using OpenAI GPT-4" in logs

### 📝 **Summary: 3 Steps to Real AI**
```bash
# 1. Set API key
export OPENAI_API_KEY="sk-your-key-here"

# 2. Edit main.py: change use_llm=False → use_llm=True (4 occurrences)

# 3. Run
python main.py
```

### � **Helpful Tips**

**Verify API Key is Set:**
```bash
echo $OPENAI_API_KEY
# Should show: sk-your-key-here
```

**Check Configuration:**
```bash
grep "use_llm=" main.py
# Should show: use_llm=True (if changed)
```

**Test Without Making Changes:**
```bash
# Temporarily set for one run
OPENAI_API_KEY="sk-your-key" python main.py
```

### �🔄 **Switch Back to Mock Mode**
Simply change all `use_llm=True` back to `use_llm=False` in `main.py` - no API calls, instant results!

### 💰 **Cost Estimation**
- **Typical analysis**: ~$0.02-0.05 per product
- **GPT-4** (recommendations): ~$0.03 per analysis
- **GPT-3.5-turbo** (sentiment): ~$0.001 per analysis

---

## �📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start Options](#quick-start-options)
  - [Option 1: Docker](#option-1-docker-recommended-)
  - [Option 2: Local Python](#option-2-local-python-execution-)
  - [Option 3: REST API](#option-3-rest-api-server-)
  - [Option 4: Interactive Notebooks](#option-4-interactive-notebooks-)
- [Running Tests](#running-tests)
- [API Usage](#api-usage)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

**Required:**
- Python 3.11+ (or Docker)
- 4GB RAM minimum
- Git (to clone repository)

**Optional:**
- OpenAI API key (for real LLM calls, works without for demos)
- Docker & Docker Compose (recommended for easiest setup)
- Jupyter (for interactive notebooks)

---

## Installation

### Clone Repository

```bash
git clone <your-repo-url>
cd ecommerce_agent
```

### Option A: Using Docker (No Local Setup Required)

```bash
# Just ensure Docker is installed
docker --version
docker-compose --version
```

### Option B: Local Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import src.agent.orchestrator; print('✅ Installation successful')"
```

---

## Quick Start Options

## Option 1: Docker (Recommended) 🐳

**Fastest way to run everything:**

```bash
# 1. Clone repository
git clone <your-repo-url>
cd ecommerce_agent

# 2. Build and run with Docker Compose
docker-compose up

# Output: Generates example reports automatically
# Check: reports/DEMO_iPhone_15_Pro_Report.md
```

**Run tests in Docker:**
```bash
docker-compose --profile test run agent-interactive pytest tests/test_agent.py -v
```

**Interactive shell:**
```bash
docker-compose --profile test run agent-interactive bash
```

---

## Option 2: Local Python Execution 🐍

**For development and customization:**

### Step 1: Setup Environment (if not done in Installation)

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run Main Demo

```bash
# Run both questions (Question 1 & 2)
python main.py

# Output shows:
# - Agent orchestration demo (Question 1)
# - Individual tool demos (Question 2)
# - Performance metrics
# - Strategic recommendations
```

**Expected output:**
```
================================================================================
QUESTION 1: AGENT ORCHESTRATION & ARCHITECTURE
================================================================================

✅ Agent initialized with 3 tools
   - Execution Strategy: parallel
   - Max Retries: 3
   - Metrics Enabled: True

📊 Running analysis: iPhone 15 Pro
--------------------------------------------------------------------------------
[Analysis results...]

✅ Question 1 Demo Complete!

================================================================================
QUESTION 2: SPECIALIZED TOOLS IMPLEMENTATION
================================================================================
[Tool demonstrations...]
```

### Step 3: Optional LLM Integration

**To use real OpenAI API calls:**

```bash
# Set API key
export OPENAI_API_KEY="sk-your-key-here"

# Edit main.py to enable LLM
# Change: use_llm=False → use_llm=True
python main.py
```

**Cost per analysis:** ~$0.08 (with caching)

---

## API Usage

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and feature list |
| `/health` | GET | Health check with metrics |
| `/tools` | GET | List available analysis tools |
| `/metrics` | GET | Performance metrics |
| `/metrics/reset` | POST | Reset metrics counters |
| `/analyze` | POST | Run market analysis (sync) |
| `/analyze/async` | POST | Submit analysis job (async) |
| `/analyze/{job_id}` | GET | Get async job results |

### Example API Requests

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Analyze Product:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"product_query": "MacBook Pro M3"}'
```

**Get Metrics:**
```bash
curl http://localhost:8000/metrics
```

**Async Analysis:**
```bash
# Submit job
JOB_ID=$(curl -X POST http://localhost:8000/analyze/async \
  -H "Content-Type: application/json" \
  -d '{"product_query": "Sony WH-1000XM5"}' | jq -r '.job_id')

# Check status
curl http://localhost:8000/analyze/$JOB_ID
```

### Python SDK Example

**test_api.py:**
```python
import requests

BASE_URL = "http://localhost:8000"

# Health check
health = requests.get(f"{BASE_URL}/health").json()
print(f"API Status: {health['status']}")
print(f"Success Rate: {health['metrics']['success_rate']}%")

# Analyze product
response = requests.post(
    f"{BASE_URL}/analyze",
    json={
        "product_query": "iPhone 15 Pro",
        "analysis_depth": "comprehensive"
    }
)

result = response.json()
print(f"\nProduct: {result['result']['product_data']['name']}")
print(f"Sentiment: {result['result']['sentiment']['overall_sentiment']}")
print(f"Recommendations: {len(result['result']['recommendations'])}")
```

**For complete API documentation, see:** [question_3/API.md](./question_3/API.md)

---

## Docker Commands

### Basic Operations

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild after code changes
docker-compose up --build --force-recreate
```

### Service-Specific Commands

```bash
# API server only (from question_3/)
cd question_3
docker-compose up api

# Run tests in Docker
docker-compose --profile test run test

# Interactive demo
docker-compose --profile demo run demo

# Batch report generation
docker-compose --profile batch run batch
```

### Container Management

```bash
# List running containers
docker ps

# Execute command in container
docker exec -it market_analysis_api bash

# View container logs
docker logs market_analysis_api -f

# Remove all containers and volumes
docker-compose down -v
```

---

## Project Structure

**For step-by-step exploration:**

### Step 1: Start Jupyter

```bash
# Install Jupyter if not already installed
pip install jupyter

# Start Jupyter server
jupyter notebook
```

### Step 2: Open Notebooks

**Architecture Demo (Question 1):**
```
notebooks/QUESTION_1_PRESENTATION.ipynb
```
Demonstrates:
- Agent configuration
- Tool registration
- Parallel execution
- Metrics tracking
- Health checks

**Tools Demo (Question 2):**
```Question 1 & 2 demos)
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container image (root)
├── docker-compose.yml           # Service orchestration (root)
├── src/
│   ├── agent/
│   │   └── orchestrator.py      # Agent orchestration (650+ lines)
│   ├── tools/
│   │   ├── sentiment_analyzer.py    # Tool 1: Sentiment (248 lines)
│   │   ├── market_trend_analyzer.py # Tool 2: Trends (450 lines)
│   │   └── report_generator.py      # Tool 3: Reports (450 lines)
│   └── utils/
│       ├── models.py             # Pydantic data models
│       └── mock_data.py          # Simulated data generators
├── config/
│   ├── settings.py               # Configuration
│   └── __init__.py
├── tests/
│   └── test_agent.py            # ⭐ Run tests (17 tests)
├── notebooks/
│   ├── 01_architecture_demo.ipynb  # ⭐ Question 1 demo
│   ├── 02_tools_demo.ipynb         # ⭐ Question 2 demo
│   └── 03_testing_demo.ipynb       # Test demonstrations
├── reports/                     # Generated analysis reports
│   └── DEMO_iPhone_15_Pro_Report.md
├── question_1/                  # Question 1 documentation
├── question_2/                  # Question 2 documentation
├── question_3/                  # ⭐ Question 3: API & Docker
│   ├── api.py                   # ⭐ REST API server
│   ├── API.md                   # ⭐ API documentation
│   ├── Dockerfile               # ⭐ API container image
│   └── docker-compose.yml       # ⭐ API service config
├── README.md                    # Project overview
├── TECHNICAL_README.md          # Technical deep dive
└── QUICKSTART.md                # ⭐ This file

**Key files marked with ⭐**
```_market_trend_analyzer PASSED
# tests/test_agent.py::test_report_generator PASSED
# ... (14 more)
# ==================== 17 passed in 2.83s ====================
```

### With Coverage Report

```bash
pytest tests/test_agent.py --cov=src --cov-report=term-missing

# Expected coverage: ~70% of critical paths
```

### Specific Test Categories

```bash
# Tool tests only
pytest tests/test_agent.py -k "tool" -v

# Orchestration tests only
pytest tests/test_agent.py -k "orchestration" -v

# Error handling tests
pytest tests/test_agent.py -k "error" -v
```

---

## Option 3: REST API Server 🌐

**Start the API server for programmatic access:**

### Using Docker (Recommended)

```bash
# Navigate to question_3 directory
cd question_3

# Build and start API container
docker-compose up --build

# API will be available at http://localhost:8000
```

### Using Local Python

```bash
# From question_3 directory
cd question_3

# Start API server
pyCheck Docker is running
docker ps

# Rebuild containers from scratch
cd question_3  # For API
dockeJupyter kernel issues:**
```bash
# Install ipykernel
pip install ipykernel

# Register kernel
python -m ipykernel install --user --name=ecommerce_agent

# Select kernel in Jupyter: Kernel → Change Kernel → ecommerce_agent
```

**6. Module import errors:**
```bash
# Ensure you're in the project root
pwd  # Should end with /ecommerce_agent

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Reinstall in development mode
pip install -e .
```

**5. API connection refused:**
```bash
# Ensure API is running
curl http://localhost:8000/health

# Check API logs
cd question_3
docker-compose logs api

# Try with explicit host
curl http://127.0.0.1:8000/healthn http://localhost:8000
```
Try the REST API**
   - See [question_3/API.md](./question_3/API.md) for full API documentation
   - Start API: `cd question_3 && docker-compose up`
   - Test endpoint: `curl http://localhost:8000/analyze -X POST -H "Content-Type: application/json" -d '{"product_query":"iPhone 15 Pro"}'`

5. **
### Verify API is Running

```bash
# Test health endpoint
curl http://localhost:8000/health

# Or visit in browser:
# http://localhost:8000/docs (Interactive Swagger UI)
```

### Make API Requests

**Using cURL:**
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

**Using Python:**
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
**Installation** | |
| Docker setup only | 2 minutes |
| Local Python setup | 10 minutes |
| **Running** | |
| Docker demo | 5 minutes |
| Local Python demo | 3 minutes |
| Start API server | 2 minutes |
| **Testing & Exploration** | |
| Run all tests | 3 seconds |
| Test API endpoints | 5 minutes |
| Review outputs | 10 minutes |
| Explore notebooks | 30 minutes |
| Read documentation | 60 minutes |

**Total to get started:** 5-15 minutes  
**Total to understand project:** ~2 hours

---

## Common Use Cases

### 1. Quick Demo (5 minutes)
```bash
# Using Docker - fastest
docker-compose up

# Or local Python
python main.py
```

### 2. API Development (10 minutes)
```bash
# Start API server
cd question_3
docker-compose up

# Test in another terminal
curl http://localhost:8000/health
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"product_query":"iPhone 15 Pro"}'
```

### 3. Interactive Exploration (30 minutes)
```bash
# Start Jupyter
jupyter notebook

# Open: notebooks/01_architecture_demo.ipynb
# Run cells with Shift+Enter
```

### 4. Testing & Validation (5 minutes)
```bash
# Run all tests
pytest tests/test_agent.py -v --cov=src

# Or in Docker
cd question_3
docker-compose --profile test run test
```

---

<p align="center">
  <strong>🚀 Ready to analyze?</strong><br>
  <code>python main.py</code> (Local) or <code>docker-compose up</code> (Docker)<br>
  <code>cd question_3 && docker-compose up</code> (API Server)
</p>

<p align="center">
  <strong>📚 Need help?</strong><br>
  Check <a href="./question_3/API.md">API Documentation</a> | 
  <a href="./README.md">Main README</a> | 
  <a href="./TECHNICAL_README.md">Technical Guide</a
ecommerce_agent/
├── main.py                      # ⭐ Main entry point (run this)
├── src/
│   ├── agent/
│   │   └── orchestrator.py      # Agent orchestration (650+ lines)
│   ├── tools/
│   │   ├── sentiment_analyzer.py    # Tool 1 (248 lines)
│   │   ├── market_trend_analyzer.py # Tool 2 (450 lines)
│   │   └── report_generator.py      # Tool 3 (450 lines)
│   └── utils/
│       ├── models.py             # Pydantic data models
│       └── mock_data.py          # Simulated data generators
├── tests/
│   └── test_agent.py            # ⭐ Run tests (17 tests)
├── notebooks/
│   ├── QUESTION_1_PRESENTATION.ipynb  # ⭐ Architecture demo
│   └── QUESTION_2_PRESENTATION.ipynb  # ⭐ Tools demo
├── reports/
│   └── DEMO_iPhone_15_Pro_Report.md # Sample output
├── question_1/                  # Architecture docs
├── question_2/                  # Tools docs
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container image
└── docker-compose.yml           # Service orchestration
```

**Key files marked with ⭐**

---

## Example Outputs

### Console Output

After running `python main.py`, check:

**Terminal:**
- Agent orchestration metrics
- Tool execution times
- Strategic recommendations

**Files Generated:**
- `reports/DEMO_iPhone_15_Pro_Report.md`

### Sample Analysis

**Input:**
```python
AnalysisRequest(
    product_query="iPhone 15 Pro",
    include_sentiment=True,
    include_competitors=True
)
```

**Output:**
- Product details (price, specs, positioning)
- Sentiment analysis (score: 0.75/1.0, themes)
- Competitive landscape (vs Samsung, Google Pixel)
- Strategic recommendations (5 actionable insights)
- 6 visualization types

[See full example →](./reports/DEMO_iPhone_15_Pro_Report.md)

---

## Troubleshooting

### Common Issues

**1. Import errors:**
```bash
# Make sure you're in the correct directory
cd ecommerce_agent

# Reinstall dependencies
pip install -r requirements.txt
```

**2. Python version:**
```bash
# Check version
python --version  # Should be 3.11+

# If wrong version, use explicit python3.11
python3.11 main.py
```

**3. Docker issues:**
```bash
# Rebuild containers
docker-compose build --no-cache
docker-compose up
```

**4. OpenAI API errors (if using LLM mode):**
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Check key is valid at: https://platform.openai.com/api-keys
```

**5. Jupyter kernel issues:**
```bash
# Install ipykernel
pip install ipykernel

# Register kernel
python -m ipykernel install --user --name=ecommerce_agent
```

---

## Next Steps

**After running the demo:**

1. **Read Technical Documentation**
   - [Technical README](./TECHNICAL_README.md) - Deep dive into implementation
   - [Question 1 README](./question_1/README.md) - Architecture details
   - [Question 2 README](./question_2/README.md) - Tools implementation

2. **Explore Notebooks**
   - `notebooks/QUESTION_1_PRESENTATION.ipynb` - Interactive architecture demo
   - `notebooks/QUESTION_2_PRESENTATION.ipynb` - Individual tool demos

3. **Review Example Output**
   - `reports/DEMO_iPhone_15_Pro_Report.md` - Sample analysis report

4. **Run Tests**
   ```bash
   pytest tests/test_agent.py -v
   ```

---

## Performance Benchmarks

**Execution Time:**
- Sequential mode: ~2.3s
- Parallel mode: ~1.5s (33% faster)

**Test Suite:**
- 17 comprehensive tests
- Runtime: <3 seconds
- Coverage: 70% of critical paths

**Resource Usage:**
- Memory: ~100MB (without LLM)
- Memory: ~200MB (with LLM active)
- CPU: <50% single core

---

## Getting Help

**Documentation:**
- [Main README](./README.md) - Overview and skills showcase
- [Technical README](./TECHNICAL_README.md) - Implementation details
- This file - Running instructions

**Issues:**
- Check troubleshooting section above
- Review error messages carefully
- Ensure all dependencies installed

---

## Time Estimates

| Task | Time Required |
|------|---------------|
| Docker setup & run | 5 minutes |
| Local Python setup | 10 minutes |
| Run all tests | 3 seconds |
| Review outputs | 10 minutes |
| Explore notebooks | 30 minutes |
| Read documentation | 60 minutes |

**Total to understand project:** ~2 hours

---

<p align="center">
  <strong>Ready to analyze? Run: <code>python main.py</code></strong>
</p>
