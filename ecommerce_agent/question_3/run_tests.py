#!/usr/bin/env python3
"""
Easy Test Runner for E-commerce Agent System

This script makes it easy to run the 7 core test categories that validate
all components of the e-commerce market analysis agent system.

Test Categories:
1. Configuration Tests - Agent setup and configuration validation
2. Individual Tool Tests - Core tool functionality (sentiment, trends, data collection, reporting)
3. Orchestration Tests - Agent coordination and workflow management
4. Error Handling Tests - Retry logic and input validation
5. Output Validation Tests - Result structure and report generation

Usage:
    python run_tests.py              # Run all 16 tests (7 categories)
    python run_tests.py --category   # Show test categories
    python run_tests.py --quick      # Run key representative tests only
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description=""):
    """Run a command and display results"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print("-" * 60)
    
    try:
        # Use python3 explicitly since python might not be available
        command = command.replace("python -m pytest", "python3 -m pytest")
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✅ SUCCESS")
        else:
            print(f"❌ FAILED (exit code: {result.returncode})")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def show_categories():
    """Show the 7 test categories"""
    categories = [
        ("1. Configuration Tests", "Agent setup and configuration validation", "TestConfiguration"),
        ("2. Individual Tool Tests", "Core tool functionality testing", "TestIndividualTools"), 
        ("3. Orchestration Tests", "Agent workflow coordination", "TestOrchestration"),
        ("4. Error Handling Tests", "Retry logic and validation", "TestErrorHandling"),
        ("5. Output Validation Tests", "Result structure verification", "TestOutputValidation")
    ]
    
    print("\n🧪 E-commerce Agent Test Categories")
    print("=" * 50)
    
    for name, description, test_class in categories:
        print(f"\n{name}")
        print(f"   Description: {description}")
        print(f"   Test Class: {test_class}")
        
        # Show individual tests in this category
        result = subprocess.run(
            f"python3 -m pytest tests/test_agent.py::{test_class} --collect-only -q",
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        if result.returncode == 0:
            test_count = len([line for line in result.stdout.split('\n') if '::test_' in line])
            print(f"   Test Count: {test_count} tests")

def run_quick_tests():
    """Run a representative subset of key tests"""
    quick_tests = [
        ("tests/test_agent.py::TestConfiguration::test_orchestrator_config_creation", 
         "Configuration - Agent setup"),
        ("tests/test_agent.py::TestIndividualTools::test_sentiment_analyzer_tool", 
         "Tools - Sentiment analysis"),
        ("tests/test_agent.py::TestOrchestration::test_sequential_orchestration", 
         "Orchestration - Workflow"),
        ("tests/test_agent.py::TestErrorHandling::test_retry_logic_with_failing_tool", 
         "Error handling - Retry logic"),
        ("tests/test_agent.py::TestOutputValidation::test_analysis_result_structure", 
         "Output - Result validation")
    ]
    
    print("🚀 Running Quick Test Suite (5 representative tests)")
    success_count = 0
    
    for test_path, description in quick_tests:
        success = run_command(
            f"python3 -m pytest {test_path} -v",
            f"Quick Test: {description}"
        )
        if success:
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Quick Test Summary: {success_count}/{len(quick_tests)} tests passed")
    print(f"{'='*60}")
    
    return success_count == len(quick_tests)

def run_all_tests():
    """Run all tests in the 7 categories"""
    return run_command(
        "python3 -m pytest tests/test_agent.py -v",
        "Full Test Suite - All 7 Categories (16 tests)"
    )

def main():
    parser = argparse.ArgumentParser(
        description="Easy test runner for E-commerce Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                # Run all tests
  python run_tests.py --category     # Show test categories
  python run_tests.py --quick        # Run quick representative tests
        """
    )
    
    parser.add_argument(
        "--category", 
        action="store_true", 
        help="Show test categories and exit"
    )
    parser.add_argument(
        "--quick", 
        action="store_true", 
        help="Run quick representative tests only (5 tests)"
    )
    
    args = parser.parse_args()
    
    print("🔬 E-commerce Agent Test Runner")
    print("=" * 40)
    
    if args.category:
        show_categories()
        return
    
    if args.quick:
        success = run_quick_tests()
    else:
        success = run_all_tests()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()