# Quick Start Guide

## Running the Agent

### Option 1: Direct Python (Fastest)

```bash
# Install dependencies
pip install -r requirements.txt

# Run demo
python main.py
```

### Option 2: Docker (Recommended for evaluation)

```bash
# Build and run
docker-compose up

# Run tests
docker-compose --profile test run agent-interactive
```

### Option 3: Jupyter Notebooks (Interactive)

```bash
# Start Jupyter
jupyter notebook

# Open:
# - notebooks/01_architecture_demo.ipynb
# - notebooks/02_tools_demo.ipynb
# - notebooks/03_testing_demo.ipynb
```

## Running Tests

```bash
# All tests
pytest tests/test_agent.py -v

# With coverage
pytest tests/test_agent.py --cov=src
```

## Example Output

Check `reports/EXAMPLE_iPhone_15_Pro_Report.md` for sample output.

## Project Structure

```
ecommerce_agent/
├── src/
│   ├── agent/          # Agent orchestrator
│   ├── tools/          # 3 specialized tools
│   └── utils/          # Models and helpers
├── tests/              # Simple test suite
├── notebooks/          # 3 demo notebooks
├── reports/            # Generated reports
├── main.py             # Entry point
└── Dockerfile          # Container setup
```

## Time to Complete: ~5 hours

- Architecture: 1h
- Tools: 2h  
- Testing: 1h
- Documentation: 1h
