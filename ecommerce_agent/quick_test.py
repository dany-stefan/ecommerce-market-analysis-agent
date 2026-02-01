#!/usr/bin/env python3
"""
Quick Demo Validation - E-commerce Market Analysis Agent  
Fast validation of key components
"""
import subprocess
import requests
import time
import sys

def check_files():
    """Check that key files exist"""
    print("📁 Checking key files...")
    try:
        from pathlib import Path
        script_dir = Path(__file__).parent  # Get directory where script is located
        files = ['main.py', 'src/agent/orchestrator.py', 'question_3/api.py', 'question_3/Dockerfile']
        missing = [f for f in files if not (script_dir / f).exists()]
        
        if missing:
            print(f"❌ Missing files: {missing}")
            return False
        else:
            print("✅ All key files present")
            return True
    except:
        print("❌ File check failed")
        return False

def check_imports():
    """Check that main imports work"""
    print("🔧 Checking imports...")
    try:
        from pathlib import Path
        script_dir = Path(__file__).parent
        result = subprocess.run(
            f"cd '{script_dir}' && PYTHONPATH=. python3 -c 'import src.agent.orchestrator; print(\"Imports OK\")'",
            shell=True, capture_output=True, text=True, timeout=8
        )
        if result.returncode == 0 and "Imports OK" in result.stdout:
            print("✅ Core imports working")
            return True
        else:
            print("❌ Import errors detected")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Import check timed out")
        return False
    except:
        print("❌ Import check failed")
        return False

def check_api_startup():
    """Quick API startup test"""
    print("🌐 Testing API startup...")
    api_proc = None
    try:
        from pathlib import Path
        script_dir = Path(__file__).parent
        api_proc = subprocess.Popen(
            f"cd '{script_dir}' && PYTHONPATH=. python3 question_3/api.py",
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        # Give API more time and try multiple times
        for attempt in range(3):
            time.sleep(2)  # Wait 2 seconds per attempt
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    print("✅ API server working")
                    return True
            except:
                continue
        
        print("❌ API server failed")
        return False
    except:
        print("❌ API test failed")
        return False
    finally:
        if api_proc:
            api_proc.terminate()
            time.sleep(1)

def check_docker():
    """Check Docker container status"""
    print("🐳 Checking Docker...")
    try:
        result = subprocess.run(
            "docker ps -q -f name=market_analysis_api",
            shell=True, capture_output=True, text=True, timeout=3
        )
        
        if result.stdout.strip():
            print("✅ Docker container running")
            return True
        else:
            print("❌ Docker container not running")
            return False
    except:
        print("❌ Docker check failed")
        return False

def main():
    """Run quick validation"""
    print(f"""
{'='*40}
🚀 QUICK VALIDATION
{'='*40}
""")
    
    tests = [
        ("Files", check_files()),
        ("Imports", check_imports()),  
        ("API", check_api_startup()),
        ("Docker", check_docker())
    ]
    
    print(f"\n{'='*40}")
    print("📊 RESULTS")
    print(f"{'='*40}")
    
    passed = 0
    for name, result in tests:
        status = "✅" if result else "❌"
        print(f"{name:12} {status}")
        if result:
            passed += 1
    
    total = len(tests)
    print(f"\nStatus: {passed}/{total} checks passed")
    
    if passed >= 3:  # Allow Docker to be optional
        print("🎉 DEMO READY!")
        if passed == total:
            print("🌟 ALL SYSTEMS PERFECT!")
        print("Run: python3 test_all_modes.py for full validation")
    else:
        print("⚠️  Issues detected")
    
    print(f"{'='*40}")

if __name__ == "__main__":
    main()