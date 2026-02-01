"""
API Integration Tests for E-commerce Market Analysis API

Tests REST API endpoints, request/response validation, and error handling.
Run with: pytest tests/test_api.py -v
"""

import pytest
import requests
import json
import time
from unittest.mock import patch
from pathlib import Path

# Assuming the API server is running on localhost:8000
API_BASE_URL = "http://localhost:8000"


class TestAPIHealth:
    """Test API health and basic functionality"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns service information"""
        try:
            response = requests.get(f"{API_BASE_URL}/")
            assert response.status_code == 200
            
            data = response.json()
            assert "service" in data
            assert "version" in data
            assert "status" in data
            assert data["service"] == "E-commerce Market Analysis API"
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running. Start with: cd question_3 && docker-compose up")
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{API_BASE_URL}/health")
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert "timestamp" in data
            assert "tools_loaded" in data
            assert data["status"] == "healthy"
            assert isinstance(data["tools_loaded"], int)
            assert data["tools_loaded"] > 0
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_tools_endpoint(self):
        """Test tools listing endpoint"""
        try:
            response = requests.get(f"{API_BASE_URL}/tools")
            assert response.status_code == 200
            
            data = response.json()
            assert "tools" in data
            assert "approach" in data
            assert isinstance(data["tools"], list)
            assert len(data["tools"]) > 0
            
            # Verify expected tools are present
            tools = data["tools"]
            expected_tools = ["SentimentAnalyzerTool", "MarketTrendAnalyzerTool", "ReportGeneratorTool"]
            for expected_tool in expected_tools:
                assert expected_tool in tools
                
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")


class TestAPIAnalysis:
    """Test analysis endpoints"""
    
    def test_analyze_endpoint_minimal(self):
        """Test synchronous analysis with minimal request"""
        try:
            payload = {
                "product_query": "iPhone 15 Pro Test"
            }
            
            response = requests.post(
                f"{API_BASE_URL}/analyze",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate response structure
            assert "status" in data
            assert "result" in data
            assert data["status"] == "completed"
            
            result = data["result"]
            assert "request" in result
            assert "metadata" in result
            assert result["request"]["product_query"] == "iPhone 15 Pro Test"
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_analyze_endpoint_comprehensive(self):
        """Test comprehensive analysis request"""
        try:
            payload = {
                "product_query": "MacBook Pro M3",
                "analysis_depth": "comprehensive",
                "include_competitors": True,
                "include_sentiment": True
            }
            
            response = requests.post(
                f"{API_BASE_URL}/analyze",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "completed"
            result = data["result"]
            
            # Validate comprehensive analysis includes all requested components
            assert "product_data" in result
            assert "sentiment" in result
            assert "competitors" in result
            assert "recommendations" in result
            
            # Validate sentiment data structure
            if result["sentiment"]:
                sentiment = result["sentiment"]
                assert "overall_sentiment" in sentiment
                assert "sentiment_score" in sentiment
                
            # Validate competitors data
            if result["competitors"]:
                assert isinstance(result["competitors"], list)
                
            # Validate recommendations
            assert isinstance(result["recommendations"], list)
            assert len(result["recommendations"]) > 0
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_analyze_invalid_request(self):
        """Test API error handling with invalid request"""
        try:
            # Test with empty product query
            payload = {
                "product_query": ""  # Invalid empty query
            }
            
            response = requests.post(
                f"{API_BASE_URL}/analyze",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Should return validation error
            assert response.status_code in [400, 422]  # Bad request or validation error
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_analyze_malformed_json(self):
        """Test API with malformed JSON"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/analyze",
                data="{invalid json}",  # Malformed JSON
                headers={"Content-Type": "application/json"}
            )
            
            # Should return JSON parse error
            assert response.status_code == 422  # Unprocessable entity
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")


class TestAPIMetrics:
    """Test metrics and monitoring endpoints"""
    
    def test_metrics_endpoint(self):
        """Test metrics collection endpoint"""
        try:
            response = requests.get(f"{API_BASE_URL}/metrics")
            assert response.status_code == 200
            
            data = response.json()
            assert "total_analyses" in data
            assert "successful_analyses" in data
            assert "success_rate" in data
            assert isinstance(data["total_analyses"], int)
            assert isinstance(data["success_rate"], (int, float))
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_metrics_after_analysis(self):
        """Test metrics are updated after running analysis"""
        try:
            # Get initial metrics
            initial_response = requests.get(f"{API_BASE_URL}/metrics")
            initial_data = initial_response.json()
            initial_count = initial_data["total_analyses"]
            
            # Run an analysis
            analysis_payload = {"product_query": "Metrics Test Product"}
            requests.post(
                f"{API_BASE_URL}/analyze",
                json=analysis_payload
            )
            
            # Check updated metrics
            updated_response = requests.get(f"{API_BASE_URL}/metrics")
            updated_data = updated_response.json()
            
            assert updated_data["total_analyses"] > initial_count
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")


class TestAPIAsync:
    """Test asynchronous analysis endpoints"""
    
    def test_async_analysis_submission(self):
        """Test async analysis job submission"""
        try:
            payload = {
                "product_query": "Async Test Product",
                "analysis_depth": "standard"
            }
            
            response = requests.post(
                f"{API_BASE_URL}/analyze/async",
                json=payload
            )
            
            assert response.status_code == 202  # Accepted
            data = response.json()
            
            assert "job_id" in data
            assert "status" in data
            assert "message" in data
            assert data["status"] == "accepted"
            
            job_id = data["job_id"]
            assert isinstance(job_id, str)
            assert len(job_id) > 0
            
            return job_id
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_async_job_status_check(self):
        """Test checking async job status"""
        try:
            # Submit job first
            job_id = self.test_async_analysis_submission()
            if not job_id:
                pytest.skip("Could not submit async job")
            
            # Wait a moment for processing
            time.sleep(2)
            
            # Check job status
            response = requests.get(f"{API_BASE_URL}/analyze/{job_id}")
            
            assert response.status_code in [200, 202]  # OK or Still processing
            data = response.json()
            
            assert "job_id" in data
            assert "status" in data
            assert data["job_id"] == job_id
            assert data["status"] in ["pending", "processing", "completed", "failed"]
            
            if data["status"] == "completed":
                assert "result" in data
                
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_async_job_invalid_id(self):
        """Test checking status of non-existent job"""
        try:
            fake_job_id = "non-existent-job-id-12345"
            response = requests.get(f"{API_BASE_URL}/analyze/{fake_job_id}")
            
            assert response.status_code == 404  # Not found
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")


class TestAPIPerformance:
    """Test API performance and limits"""
    
    def test_response_time(self):
        """Test API response time is reasonable"""
        try:
            payload = {"product_query": "Performance Test Product"}
            
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/analyze",
                json=payload
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 30.0  # Should complete within 30 seconds
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")
    
    def test_concurrent_requests(self):
        """Test API can handle multiple concurrent requests"""
        try:
            import concurrent.futures
            
            def make_request(product_id):
                payload = {"product_query": f"Concurrent Test Product {product_id}"}
                response = requests.post(
                    f"{API_BASE_URL}/analyze",
                    json=payload
                )
                return response.status_code
            
            # Submit 3 concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(make_request, i) for i in range(3)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            # All requests should succeed
            assert all(status == 200 for status in results)
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running")


# Helper function to check if API is running
def is_api_running():
    """Check if the API server is accessible"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


# Test configuration for pytest
if __name__ == "__main__":
    if is_api_running():
        print(f"✅ API server detected at {API_BASE_URL}")
    else:
        print(f"⚠️  API server not detected at {API_BASE_URL}")
        print("Start the API with: cd question_3 && docker-compose up")
    
    pytest.main([__file__, "-v"])
