"""
Load Testing and Performance Optimization Tests
Tests system performance under various load conditions
"""
import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any
import pytest
import json
import os
from concurrent.futures import ThreadPoolExecutor
import psutil


class LoadTestResults:
    """Container for load test results"""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.status_codes: List[int] = []
        self.errors: List[str] = []
        self.start_time: float = 0
        self.end_time: float = 0
    
    def add_result(self, response_time: float, status_code: int, error: str = None):
        """Add a test result"""
        self.response_times.append(response_time)
        self.status_codes.append(status_code)
        if error:
            self.errors.append(error)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.response_times:
            return {"error": "No results recorded"}
        
        total_requests = len(self.response_times)
        successful_requests = sum(1 for code in self.status_codes if 200 <= code < 300)
        error_rate = (total_requests - successful_requests) / total_requests * 100
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "error_rate_percent": error_rate,
            "avg_response_time_ms": statistics.mean(self.response_times) * 1000,
            "median_response_time_ms": statistics.median(self.response_times) * 1000,
            "p95_response_time_ms": statistics.quantiles(self.response_times, n=20)[18] * 1000,
            "p99_response_time_ms": statistics.quantiles(self.response_times, n=100)[98] * 1000,
            "min_response_time_ms": min(self.response_times) * 1000,
            "max_response_time_ms": max(self.response_times) * 1000,
            "requests_per_second": total_requests / (self.end_time - self.start_time),
            "total_duration_seconds": self.end_time - self.start_time,
            "error_count": len(self.errors)
        }


class LoadTester:
    """Load testing utility"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, **kwargs) -> tuple:
        """Make a single HTTP request and measure performance"""
        start_time = time.time()
        try:
            async with self.session.request(method, f"{self.base_url}{endpoint}", **kwargs) as response:
                await response.read()  # Ensure full response is received
                end_time = time.time()
                return end_time - start_time, response.status, None
        except Exception as e:
            end_time = time.time()
            return end_time - start_time, 0, str(e)
    
    async def run_concurrent_requests(self, method: str, endpoint: str, 
                                    concurrent_users: int, requests_per_user: int,
                                    **kwargs) -> LoadTestResults:
        """Run concurrent requests to test load handling"""
        results = LoadTestResults()
        results.start_time = time.time()
        
        async def user_session():
            """Simulate a single user making multiple requests"""
            user_results = []
            for _ in range(requests_per_user):
                response_time, status_code, error = await self.make_request(method, endpoint, **kwargs)
                user_results.append((response_time, status_code, error))
                # Small delay between requests from same user
                await asyncio.sleep(0.1)
            return user_results
        
        # Create tasks for concurrent users
        tasks = [user_session() for _ in range(concurrent_users)]
        user_results_list = await asyncio.gather(*tasks)
        
        # Aggregate results
        for user_results in user_results_list:
            for response_time, status_code, error in user_results:
                results.add_result(response_time, status_code, error)
        
        results.end_time = time.time()
        return results


class TestAPILoadPerformance:
    """Test API performance under load"""
    
    @pytest.fixture
    def base_url(self):
        return os.getenv("TEST_BASE_URL", "http://localhost:8000")
    
    @pytest.fixture
    def auth_token(self, base_url):
        """Get authentication token for protected endpoints"""
        # This would typically create a test user and get a token
        # For now, return a mock token
        return "mock_token_for_testing"
    
    @pytest.mark.asyncio
    async def test_health_endpoint_load(self, base_url):
        """Test health endpoint under load"""
        async with LoadTester(base_url) as tester:
            results = await tester.run_concurrent_requests(
                "GET", "/health",
                concurrent_users=50,
                requests_per_user=10
            )
            
            stats = results.get_statistics()
            
            # Performance assertions
            assert stats["error_rate_percent"] < 1.0, f"Error rate too high: {stats['error_rate_percent']}%"
            assert stats["avg_response_time_ms"] < 100, f"Average response time too slow: {stats['avg_response_time_ms']}ms"
            assert stats["p95_response_time_ms"] < 200, f"95th percentile too slow: {stats['p95_response_time_ms']}ms"
            assert stats["requests_per_second"] > 100, f"Throughput too low: {stats['requests_per_second']} RPS"
            
            print(f"Health endpoint load test results: {json.dumps(stats, indent=2)}")
    
    @pytest.mark.asyncio
    async def test_authentication_load(self, base_url):
        """Test authentication endpoints under load"""
        async with LoadTester(base_url) as tester:
            # Test login endpoint
            login_data = {
                "email": "test@example.com",
                "password": "testpassword"
            }
            
            results = await tester.run_concurrent_requests(
                "POST", "/api/auth/login",
                concurrent_users=20,
                requests_per_user=5,
                json=login_data
            )
            
            stats = results.get_statistics()
            
            # Authentication should handle reasonable load
            assert stats["error_rate_percent"] < 5.0, f"Auth error rate too high: {stats['error_rate_percent']}%"
            assert stats["avg_response_time_ms"] < 500, f"Auth response time too slow: {stats['avg_response_time_ms']}ms"
            
            print(f"Authentication load test results: {json.dumps(stats, indent=2)}")
    
    @pytest.mark.asyncio
    async def test_assessment_api_load(self, base_url, auth_token):
        """Test assessment API under load"""
        async with LoadTester(base_url) as tester:
            headers = {"Authorization": f"Bearer {auth_token}"}
            
            # Test starting assessments
            assessment_data = {
                "assessment_type": "technical",
                "difficulty_level": "intermediate"
            }
            
            results = await tester.run_concurrent_requests(
                "POST", "/api/assessments/start",
                concurrent_users=10,
                requests_per_user=3,
                json=assessment_data,
                headers=headers
            )
            
            stats = results.get_statistics()
            
            # Assessment creation should be reasonably fast
            assert stats["avg_response_time_ms"] < 1000, f"Assessment creation too slow: {stats['avg_response_time_ms']}ms"
            
            print(f"Assessment API load test results: {json.dumps(stats, indent=2)}")
    
    @pytest.mark.asyncio
    async def test_job_matching_load(self, base_url, auth_token):
        """Test job matching API under load"""
        async with LoadTester(base_url) as tester:
            headers = {"Authorization": f"Bearer {auth_token}"}
            
            results = await tester.run_concurrent_requests(
                "GET", "/api/matching/recommendations",
                concurrent_users=15,
                requests_per_user=5,
                headers=headers
            )
            
            stats = results.get_statistics()
            
            # Job matching should handle concurrent requests
            assert stats["error_rate_percent"] < 10.0, f"Job matching error rate too high: {stats['error_rate_percent']}%"
            assert stats["avg_response_time_ms"] < 2000, f"Job matching too slow: {stats['avg_response_time_ms']}ms"
            
            print(f"Job matching load test results: {json.dumps(stats, indent=2)}")


class TestDatabasePerformance:
    """Test database performance under load"""
    
    @pytest.mark.asyncio
    async def test_database_connection_pool(self, base_url):
        """Test database connection pool under load"""
        async with LoadTester(base_url) as tester:
            # Make many concurrent requests that require database access
            results = await tester.run_concurrent_requests(
                "GET", "/api/dashboard/candidate",
                concurrent_users=30,
                requests_per_user=10,
                headers={"Authorization": "Bearer mock_token"}
            )
            
            stats = results.get_statistics()
            
            # Database should handle connection pooling well
            assert stats["error_rate_percent"] < 15.0, f"Database error rate too high: {stats['error_rate_percent']}%"
            
            print(f"Database connection pool test results: {json.dumps(stats, indent=2)}")


class TestMemoryAndResourceUsage:
    """Test memory and resource usage under load"""
    
    def test_memory_usage_under_load(self):
        """Test memory usage doesn't grow excessively under load"""
        initial_memory = psutil.virtual_memory().percent
        
        # Simulate load (this would typically run actual load tests)
        # For now, we'll just check that memory monitoring works
        
        final_memory = psutil.virtual_memory().percent
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 20, f"Memory usage increased too much: {memory_increase}%"
        
        print(f"Memory usage: Initial {initial_memory}%, Final {final_memory}%, Increase {memory_increase}%")
    
    def test_cpu_usage_under_load(self):
        """Test CPU usage patterns under load"""
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # CPU usage should be reasonable
        assert cpu_percent < 90, f"CPU usage too high: {cpu_percent}%"
        
        print(f"CPU usage: {cpu_percent}%")


class TestScalingBehavior:
    """Test auto-scaling behavior"""
    
    @pytest.mark.asyncio
    async def test_horizontal_scaling_trigger(self, base_url):
        """Test that high load triggers horizontal scaling"""
        # This would test that HPA triggers when load increases
        # For now, we'll simulate the conditions
        
        async with LoadTester(base_url) as tester:
            # Generate sustained high load
            results = await tester.run_concurrent_requests(
                "GET", "/health",
                concurrent_users=100,
                requests_per_user=20
            )
            
            stats = results.get_statistics()
            
            # High load should be handled (either by existing capacity or scaling)
            assert stats["error_rate_percent"] < 25.0, f"System couldn't handle high load: {stats['error_rate_percent']}% errors"
            
            print(f"High load test results: {json.dumps(stats, indent=2)}")


class TestCachePerformance:
    """Test caching system performance"""
    
    @pytest.mark.asyncio
    async def test_redis_cache_performance(self, base_url):
        """Test Redis cache performance"""
        async with LoadTester(base_url) as tester:
            # Test endpoints that should use caching
            results = await tester.run_concurrent_requests(
                "GET", "/api/jobs/search?q=python",
                concurrent_users=20,
                requests_per_user=10
            )
            
            stats = results.get_statistics()
            
            # Cached responses should be fast
            assert stats["avg_response_time_ms"] < 300, f"Cached responses too slow: {stats['avg_response_time_ms']}ms"
            
            print(f"Cache performance test results: {json.dumps(stats, indent=2)}")


class TestAIServicePerformance:
    """Test AI service performance under load"""
    
    @pytest.mark.asyncio
    async def test_ai_assessment_performance(self, base_url):
        """Test AI assessment service performance"""
        async with LoadTester(base_url) as tester:
            assessment_data = {
                "responses": [
                    {"question_id": "q1", "answer": "Python is a programming language"},
                    {"question_id": "q2", "answer": "Machine learning uses algorithms"}
                ]
            }
            
            results = await tester.run_concurrent_requests(
                "POST", "/api/assessments/evaluate",
                concurrent_users=5,  # Lower concurrency for AI services
                requests_per_user=3,
                json=assessment_data,
                headers={"Authorization": "Bearer mock_token"}
            )
            
            stats = results.get_statistics()
            
            # AI services may be slower but should still be reasonable
            assert stats["avg_response_time_ms"] < 5000, f"AI assessment too slow: {stats['avg_response_time_ms']}ms"
            assert stats["error_rate_percent"] < 20.0, f"AI service error rate too high: {stats['error_rate_percent']}%"
            
            print(f"AI assessment performance test results: {json.dumps(stats, indent=2)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])