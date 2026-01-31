# Question 2: Specialized Tools Implementation

## Overview
Implementation of 3 production-quality tools for e-commerce market analysis using **native Python orchestration**. This demonstrates modular architecture, REST API design, and sophisticated tool coordination.

## 🎯 Key Requirements

✅ **Native Python Approach**: Custom orchestration system without external frameworks  
✅ **Main Orchestrator Agent**: Coordinates tools for complex analysis  
✅ **REST API Interface**: Receives and processes analysis requests  
✅ **Modular Structure**: Independent, reusable tools with clear interfaces  

---

## 🛠️ The Three Specialized Tools

### 1. Sentiment Analyzer Tool
**File:** [`src/tools/sentiment_analyzer.py`](../src/tools/sentiment_analyzer.py)

**Purpose:** Analyzes customer reviews to extract sentiment insights and themes

**Key Features:**
- LLM-powered analy- LLM-powered analy- LLM-powered analy- LLM-powered analy- LLM-powered analy- LLM-powered analy- LLM-powered analy- LLM-powered analy-eful fallback to rule-based analysis
- Extracts ke- Extractsnd- Extracts ke- Extractsnd- Extracts ke- Extractsnd- Extracts ke- Extractsnd- Extracts ke- Extractsnd- Extracts ke- Extractsnd- Extracts ke- Extractsnd- Extracts ke- Extractsnd- Extracts ke-with OpenAI key
resulresulresulresulresulntAnalyzerInput(
    product_name="iPhone 15 Pro",
    reviews=["Great camera!", "Battery life e    reviews=["Great camera!", "Battery life e    reviews=["Great camerathemes, sample_reviews
```

---

### 2. Market Trend Analyzer Tool ⭐ NEW### 2. Market Trend Analyzer Tool ⭐ NEW### 2. Market Trend Analyzer Tool �nalyzer.py)

**Purpose:** Analyzes price and pop**Purpose:** A over time for ma**Purpose:** Analyzes price and pop**Purpose:** A over time for ma**Pnalyzer import MarketTrendAnalyzerTool, MarketTrendInput

tool = MarketTrendAnalyzerTool(use_mock_data=True)
resuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresuresu

---

### 3. Report Generator Tool
**File:** [`src/tools/report_generator.py`](../src/tools/report_generator.py)

**Purpose:** Synthesizes analysis data into comprehensive reports with visualizations

For full documentation, see [README_new.md](README_new.md) or the [PreseFor full documentation, see [REATATION_GUIDE.md).
