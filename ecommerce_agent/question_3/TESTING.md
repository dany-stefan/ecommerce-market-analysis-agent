# Quick Test Guide

## Easy Ways to Test the 7 Core Categories

### Option 1: Use the Test Runner Script (Recommended)

```bash
# Show all test categories
python3 run_tests.py --category

# Run quick representative tests (5 tests)
python3 run_tests.py --quick

# Run all tests (16 tests)
python3 run_tests.py
```

### Option 2: Direct pytest Commands

```bash
# Run all tests
python3 -m pytest tests/test_agent.py -v

# Run specific test category
python3 -m pytest tests/test_agent.py::TestConfiguration -v
python3 -m pytest tests/test_agent.py::TestIndividualTools -v 
python3 -m pytest tests/test_agent.py::TestOrchestration -v
python3 -m pytest tests/test_agent.py::TestErrorHandling -v
python3 -m pytest tests/test_agent.py::TestOutputValidation -v

# Run single test
python3 -m pytest tests/test_agent.py::TestConfiguration::test_orchestrator_config_creation -v
```

### The 7 Test Categories

1. **Configuration Tests** (TestConfiguration)
   - Agent setup and configuration validation
   - 2 tests

2. **Individual Tool Tests** (TestIndividualTools)  
   - Core tool functionality testing
   - 4 tests (sentiment, trends, product collection, reporting)

3. **Orchestration Tests** (TestOrchestration)
   - Agent workflow coordination
   - 5 tests (registration, sequential, parallel, metrics, health)

4. **Error Handling Tests** (TestErrorHandling)
   - Retry logic and validation
   - 3 tests

5. **Output Validation Tests** (TestOutputValidation)
   - Result structure verification  
   - 2 tests

**Total: 16 tests across 5 categories**

### Expected Results

✅ All tests should pass with only Pydantic deprecation warnings (which are harmless)

🔬 Test execution time: ~3 seconds for full suite, ~0.5 seconds for quick tests