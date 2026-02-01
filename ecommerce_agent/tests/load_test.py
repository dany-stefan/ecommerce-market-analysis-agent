"""
Load Testing for E-commerce Market Analysis API

Tests API performance under concurrent load and validates response times.
Run with: python -m tests.load_test
"""

import asyncio
import time
import statistics
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"  # Update for container testing
NUM_CONCURRENT_USERS = 10
NUM_REQUESTS_PER_USER = 3
TEST_PRODUCTS = [
    "iPhone 15 Pro Max",
    "Samsung Galaxy S24 Ultra", 
    "MacBook Pro M3",
    "Dell XPS 13",
    "iPad Air",
    "Surface Laptop Studio",
    "AirPods Pro",
    "Sony WH-1000XM5",
    "Tesla Model 3",
    "Apple Watch Series 9"
]


class LoadTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results: List[Dict] = []
        
    def check_api_availability(self) -> bool:
        """Check if API is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def single_request_test(self, user_id: int, request_id: int) -> Dict:
        """Execute a single API request and measure performance"""
        product = TEST_PRODUCTS[request_id % len(TEST_PRODUCTS)]
        
        payload = {
            "product_query": f"{product} Load Test {user_id}-{request_id}",
            "analysis_depth": "standard",
            "include_competitors": True,
            "include_sentiment": True,
            "execution_strategy": "parallel"
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/analyze",
                json=payload,
                timeout=60,  # 1-minute timeout for load testing
                headers={"Content-Type": "application/json"}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            result = {
                "user_id": user_id,
                "request_id": request_id,
                "product": product,
                "status_code": response.status_code,
                "response_time": response_time,
                "success": response.status_code == 200,
                "timestamp": datetime.now().isoformat(),
                "error": None
            }
            
            if response.status_code == 200:
                data = response.json()
                result["execution_time"] = data.get("execution_time")
                result["response_size"] = len(response.content)
            else:
                result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                
        except requests.exceptions.Timeout:
            result = {
                "user_id": user_id,
                "request_id": request_id,
                "product": product,
                "status_code": 0,
                "response_time": 60.0,  # Timeout duration
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "error": "Request timeout (60s)"
            }
        except Exception as e:
            end_time = time.time()
            result = {
                "user_id": user_id,
                "request_id": request_id,
                "product": product,
                "status_code": 0,
                "response_time": end_time - start_time,
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        
        return result
    
    def user_simulation(self, user_id: int) -> List[Dict]:
        """Simulate a single user making multiple requests"""
        user_results = []
        
        print(f"👤 User {user_id}: Starting {NUM_REQUESTS_PER_USER} requests...")
        
        for request_id in range(NUM_REQUESTS_PER_USER):
            result = self.single_request_test(user_id, request_id)
            user_results.append(result)
            
            status_icon = "✅" if result["success"] else "❌"
            print(f"👤 User {user_id}, Request {request_id}: {status_icon} {result['response_time']:.2f}s")
            
            # Small delay between requests from same user
            time.sleep(0.5)
        
        print(f"👤 User {user_id}: Completed all requests")
        return user_results
    
    def run_load_test(self) -> Dict:
        """Execute the complete load test"""
        print(f"🚀 Starting load test with {NUM_CONCURRENT_USERS} concurrent users")
        print(f"📊 Each user will make {NUM_REQUESTS_PER_USER} requests")
        print(f"🎯 Total requests: {NUM_CONCURRENT_USERS * NUM_REQUESTS_PER_USER}")
        print(f"🌐 API endpoint: {self.base_url}")
        print("\n" + "="*60 + "\n")
        
        # Check API availability
        if not self.check_api_availability():
            print("❌ API not available. Please start the server first.")
            print("💡 Run: cd question_3 && docker-compose up")
            return {"error": "API not available"}
        
        print("✅ API is available. Starting load test...\n")
        
        start_time = time.time()
        
        # Execute concurrent user simulations
        with ThreadPoolExecutor(max_workers=NUM_CONCURRENT_USERS) as executor:
            # Submit all user simulations
            futures = {
                executor.submit(self.user_simulation, user_id): user_id 
                for user_id in range(NUM_CONCURRENT_USERS)
            }
            
            # Collect results as they complete
            all_results = []
            for future in as_completed(futures):
                user_id = futures[future]
                try:
                    user_results = future.result()
                    all_results.extend(user_results)
                except Exception as e:
                    print(f"❌ User {user_id} failed: {str(e)}")
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Analyze results
        return self.analyze_results(all_results, total_duration)
    
    def analyze_results(self, results: List[Dict], total_duration: float) -> Dict:
        """Analyze load test results and generate report"""
        if not results:
            return {"error": "No results to analyze"}
        
        # Basic statistics
        total_requests = len(results)
        successful_requests = len([r for r in results if r["success"]])
        failed_requests = total_requests - successful_requests
        success_rate = (successful_requests / total_requests) * 100
        
        # Response time statistics
        response_times = [r["response_time"] for r in results if r["success"]]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        else:
            avg_response_time = median_response_time = min_response_time = max_response_time = p95_response_time = 0
        
        # Throughput calculation
        requests_per_second = successful_requests / total_duration if total_duration > 0 else 0
        
        # Error analysis
        error_types = {}
        for result in results:
            if not result["success"] and result["error"]:
                error_type = result["error"][:50]  # First 50 chars
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Generate report
        report = {
            "test_summary": {
                "total_duration": total_duration,
                "concurrent_users": NUM_CONCURRENT_USERS,
                "requests_per_user": NUM_REQUESTS_PER_USER,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate_percent": success_rate
            },
            "performance_metrics": {
                "requests_per_second": requests_per_second,
                "avg_response_time": avg_response_time,
                "median_response_time": median_response_time,
                "min_response_time": min_response_time,
                "max_response_time": max_response_time,
                "p95_response_time": p95_response_time
            },
            "error_analysis": {
                "error_types": error_types,
                "timeout_count": len([r for r in results if "timeout" in str(r.get("error", "")).lower()])
            },
            "detailed_results": results
        }
        
        # Print summary
        self.print_summary(report)
        
        return report
    
    def print_summary(self, report: Dict):
        """Print load test summary"""
        summary = report["test_summary"]
        metrics = report["performance_metrics"]
        errors = report["error_analysis"]
        
        print("\n" + "="*60)
        print("📈 LOAD TEST RESULTS SUMMARY")
        print("="*60)
        
        print(f"⏱️  Total Duration: {summary['total_duration']:.2f}s")
        print(f"👥 Concurrent Users: {summary['concurrent_users']}")
        print(f"📊 Total Requests: {summary['total_requests']}")
        print(f"✅ Successful: {summary['successful_requests']}")
        print(f"❌ Failed: {summary['failed_requests']}")
        print(f"📈 Success Rate: {summary['success_rate_percent']:.1f}%")
        
        print("\n🚀 PERFORMANCE METRICS:")
        print(f"⚡ Throughput: {metrics['requests_per_second']:.2f} req/s")
        print(f"📊 Average Response Time: {metrics['avg_response_time']:.2f}s")
        print(f"📊 Median Response Time: {metrics['median_response_time']:.2f}s")
        print(f"📊 95th Percentile: {metrics['p95_response_time']:.2f}s")
        print(f"📊 Min Response Time: {metrics['min_response_time']:.2f}s")
        print(f"📊 Max Response Time: {metrics['max_response_time']:.2f}s")
        
        if errors["error_types"]:
            print("\n❌ ERROR ANALYSIS:")
            for error_type, count in errors["error_types"].items():
                print(f"   {count}x: {error_type}")
        
        # Performance assessment
        print("\n🎯 PERFORMANCE ASSESSMENT:")
        
        if metrics["avg_response_time"] < 5.0:
            print("✅ Excellent: Average response time under 5 seconds")
        elif metrics["avg_response_time"] < 10.0:
            print("⚠️  Good: Average response time under 10 seconds")
        else:
            print("❌ Poor: Average response time over 10 seconds")
        
        if summary["success_rate_percent"] >= 95:
            print("✅ Excellent: Success rate 95% or higher")
        elif summary["success_rate_percent"] >= 90:
            print("⚠️  Good: Success rate 90% or higher")
        else:
            print("❌ Poor: Success rate below 90%")
        
        if metrics["requests_per_second"] >= 1.0:
            print("✅ Good: Throughput 1+ requests per second")
        else:
            print("⚠️  Low: Throughput below 1 request per second")
        
        print("\n" + "="*60)


def main():
    """Main load test execution"""
    # Use environment variable for container testing
    import os
    api_url = os.getenv("API_BASE_URL", API_BASE_URL)
    
    tester = LoadTester(api_url)
    
    try:
        results = tester.run_load_test()
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"load_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        # Return exit code based on success
        if "error" in results:
            return 1
        
        success_rate = results["test_summary"]["success_rate_percent"]
        avg_response_time = results["performance_metrics"]["avg_response_time"]
        
        # Exit with error if performance is poor
        if success_rate < 90 or avg_response_time > 15:
            print("\n❌ Load test FAILED: Performance below acceptable thresholds")
            return 1
        
        print("\n✅ Load test PASSED: Performance meets requirements")
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️  Load test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Load test failed with error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
