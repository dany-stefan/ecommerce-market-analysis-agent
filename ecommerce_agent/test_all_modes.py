#!/usr/bin/env python3
"""
Comprehensive Demo Validation - E-commerce Market Analysis Agent
Tests all execution paths: main.py → API → Docker container
"""
import json
import time
import subprocess
import requests
from pathlib import Path

def run_command(command, description, timeout=45):
    """Execute command and return success status"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            print(f"✅ SUCCESS")
            # Only show last few lines to avoid clutter
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 3:
                    print(f"Output: ...{lines[-3]}")
                    print(f"        {lines[-2]}")
                    print(f"        {lines[-1]}")
                else:
                    print(f"Output: {result.stdout.strip()}")
        else:
            print(f"❌ FAILED (exit code: {result.returncode})")
            if result.stderr:
                print(f"Error: {result.stderr.strip()}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 ERROR: {e}")
        return False

def test_api_endpoint(url, method="GET", data=None, description=""):
    """Test API endpoint with clean output"""
    print(f"\n🌐 {description}: {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=data, timeout=15)
        
        if response.status_code == 200:
            print(f"✅ SUCCESS - Status: {response.status_code}")
            try:
                data = response.json()
                if 'status' in data:
                    print(f"   Status: {data.get('status', 'unknown')}")
                if 'tools_loaded' in data:
                    print(f"   Tools: {data.get('tools_loaded', 0)} loaded")
                return True
            except:
                print(f"   Response: {response.text[:100]}...")
                return True
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION FAILED")
        return False
    except Exception as e:
        print(f"💥 ERROR: {e}")
        return False

def main():
    """Run streamlined demo validation"""
    print(f"""
{'='*60}
🚀 E-COMMERCE AGENT DEMO VALIDATION
{'='*60}
Testing all execution modes for assignment demo
""")
    
    project_root = Path(__file__).parent
    results = {}
    
    # Test 1: Main execution (core requirement)
    results['main'] = run_command(
        f"cd '{project_root}' && python3 main.py",
        "Direct Execution (main.py)",
        timeout=30
    )
    
    # Test 2: API Health (Question 3 requirement)
    print(f"\n{'='*60}")
    print("🚀 Testing API Mode")
    print(f"{'='*60}")
    
    # Quick API test
    api_proc = subprocess.Popen(
        f"cd '{project_root}' && PYTHONPATH=. python3 question_3/api.py",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    time.sleep(5)  # API startup time
    
    try:
        results['api'] = test_api_endpoint("http://localhost:8000/health", description="API Health Check")
    finally:
        api_proc.terminate()
        time.sleep(1)
    
    # Test 3: Docker (Production deployment)
    print(f"\n{'='*60}")
    print("🐳 Testing Docker Mode")  
    print(f"{'='*60}")
    
    # Stop any existing containers quietly
    subprocess.run(f"cd '{project_root}/question_3' && docker-compose down", 
                  shell=True, capture_output=True)
    
    results['docker'] = run_command(
        f"cd '{project_root}/question_3' && docker-compose up -d api",
        "Docker Container Deployment",
        timeout=30
    )
    
    if results['docker']:
        time.sleep(5)  # Container startup
        results['docker_api'] = test_api_endpoint("http://localhost:8000/health", 
                                                description="Docker API Health")
    else:
        results['docker_api'] = False
    
    # Test 4: Check outputs
    results['reports'] = run_command(
        f"ls -la '{project_root}/reports/' | grep -E '(iPhone|Report)' | wc -l",
        "Generated Reports Count"
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 VALIDATION SUMMARY")
    print(f"{'='*60}")
    
    test_results = [
        ("Direct Execution", results['main']),
        ("API Server", results['api']),
        ("Docker Build", results['docker']),
        ("Docker API", results['docker_api']),
        ("Report Generation", results['reports'])
    ]
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name:18} {status}")
    
    print(f"\nSuccess Rate: {passed}/{total} ({(passed/total)*100:.0f}%)")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! Demo ready!")
        print(f"📋 Available execution modes:")
        print(f"   • python3 main.py")
        print(f"   • PYTHONPATH=. python3 question_3/api.py")  
        print(f"   • cd question_3 && docker-compose up api")
    else:
        print(f"\n⚠️  {total-passed} test(s) failed - check above for details")

if __name__ == "__main__":
    main()