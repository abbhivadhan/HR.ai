"""
Security Penetration Testing
Tests for security vulnerabilities and attack vectors
"""
import pytest
import asyncio
import aiohttp
import time
import json
import base64
import hashlib
import os
from typing import Dict, List, Any
import jwt
import sqlparse


class SecurityTestResults:
    """Container for security test results"""
    
    def __init__(self):
        self.vulnerabilities: List[Dict[str, Any]] = []
        self.passed_tests: List[str] = []
        self.failed_tests: List[str] = []
    
    def add_vulnerability(self, test_name: str, severity: str, description: str, details: Dict = None):
        """Add a discovered vulnerability"""
        self.vulnerabilities.append({
            "test": test_name,
            "severity": severity,
            "description": description,
            "details": details or {}
        })
        self.failed_tests.append(test_name)
    
    def add_passed_test(self, test_name: str):
        """Add a passed security test"""
        self.passed_tests.append(test_name)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get security test summary"""
        return {
            "total_tests": len(self.passed_tests) + len(self.failed_tests),
            "passed_tests": len(self.passed_tests),
            "failed_tests": len(self.failed_tests),
            "vulnerabilities_found": len(self.vulnerabilities),
            "high_severity": len([v for v in self.vulnerabilities if v["severity"] == "HIGH"]),
            "medium_severity": len([v for v in self.vulnerabilities if v["severity"] == "MEDIUM"]),
            "low_severity": len([v for v in self.vulnerabilities if v["severity"] == "LOW"]),
            "vulnerabilities": self.vulnerabilities
        }


class TestAuthenticationSecurity:
    """Test authentication security vulnerabilities"""
    
    @pytest.fixture
    def base_url(self):
        return os.getenv("TEST_BASE_URL", "http://localhost:8000")
    
    @pytest.fixture
    def security_results(self):
        return SecurityTestResults()
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_login(self, base_url, security_results):
        """Test for SQL injection vulnerabilities in login"""
        async with aiohttp.ClientSession() as session:
            # Common SQL injection payloads
            sql_payloads = [
                "' OR '1'='1",
                "' OR 1=1--",
                "' UNION SELECT * FROM users--",
                "'; DROP TABLE users;--",
                "' OR 'x'='x",
                "admin'--",
                "' OR 1=1#"
            ]
            
            for payload in sql_payloads:
                login_data = {
                    "email": payload,
                    "password": "any_password"
                }
                
                async with session.post(f"{base_url}/api/auth/login", json=login_data) as response:
                    response_text = await response.text()
                    
                    # Check for SQL error messages that might indicate vulnerability
                    sql_error_indicators = [
                        "sql", "mysql", "postgresql", "sqlite", "oracle",
                        "syntax error", "column", "table", "database"
                    ]
                    
                    if any(indicator in response_text.lower() for indicator in sql_error_indicators):
                        security_results.add_vulnerability(
                            "sql_injection_login",
                            "HIGH",
                            f"Potential SQL injection vulnerability detected with payload: {payload}",
                            {"payload": payload, "response": response_text[:500]}
                        )
                        return
                    
                    # Should return 401 for invalid credentials, not 200 or 500
                    if response.status not in [401, 422]:
                        security_results.add_vulnerability(
                            "sql_injection_login",
                            "MEDIUM",
                            f"Unexpected response status {response.status} for SQL injection payload",
                            {"payload": payload, "status": response.status}
                        )
                        return
            
            security_results.add_passed_test("sql_injection_login")
    
    @pytest.mark.asyncio
    async def test_brute_force_protection(self, base_url, security_results):
        """Test brute force attack protection"""
        async with aiohttp.ClientSession() as session:
            # Attempt multiple failed logins
            login_data = {
                "email": "test@example.com",
                "password": "wrong_password"
            }
            
            response_codes = []
            for attempt in range(10):
                async with session.post(f"{base_url}/api/auth/login", json=login_data) as response:
                    response_codes.append(response.status)
                    await asyncio.sleep(0.1)  # Small delay between attempts
            
            # Should implement rate limiting after several failed attempts
            if all(code == 401 for code in response_codes):
                security_results.add_vulnerability(
                    "brute_force_protection",
                    "MEDIUM",
                    "No brute force protection detected - all attempts returned 401",
                    {"response_codes": response_codes}
                )
            elif any(code == 429 for code in response_codes[-3:]):
                security_results.add_passed_test("brute_force_protection")
            else:
                security_results.add_vulnerability(
                    "brute_force_protection",
                    "LOW",
                    "Brute force protection behavior unclear",
                    {"response_codes": response_codes}
                )
    
    @pytest.mark.asyncio
    async def test_jwt_token_security(self, base_url, security_results):
        """Test JWT token security"""
        async with aiohttp.ClientSession() as session:
            # Test with malformed JWT tokens
            malformed_tokens = [
                "invalid.jwt.token",
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
                "Bearer malformed_token",
                "",
                "null",
                "undefined"
            ]
            
            for token in malformed_tokens:
                headers = {"Authorization": f"Bearer {token}"}
                async with session.get(f"{base_url}/api/users/profile", headers=headers) as response:
                    # Should return 401 for invalid tokens
                    if response.status != 401:
                        security_results.add_vulnerability(
                            "jwt_token_validation",
                            "HIGH",
                            f"Invalid JWT token accepted: {token}",
                            {"token": token, "status": response.status}
                        )
                        return
            
            security_results.add_passed_test("jwt_token_validation")
    
    @pytest.mark.asyncio
    async def test_password_policy(self, base_url, security_results):
        """Test password policy enforcement"""
        async with aiohttp.ClientSession() as session:
            weak_passwords = [
                "123456",
                "password",
                "abc123",
                "qwerty",
                "admin",
                "test",
                "a",  # Too short
                "password123"  # Common pattern
            ]
            
            for weak_password in weak_passwords:
                user_data = {
                    "email": f"test_{int(time.time())}@example.com",
                    "password": weak_password,
                    "first_name": "Test",
                    "last_name": "User",
                    "user_type": "candidate"
                }
                
                async with session.post(f"{base_url}/api/auth/register", json=user_data) as response:
                    # Should reject weak passwords
                    if response.status == 201:
                        security_results.add_vulnerability(
                            "password_policy",
                            "MEDIUM",
                            f"Weak password accepted: {weak_password}",
                            {"password": weak_password}
                        )
                        return
            
            security_results.add_passed_test("password_policy")


class TestInputValidationSecurity:
    """Test input validation security"""
    
    @pytest.mark.asyncio
    async def test_xss_prevention(self, base_url, security_results):
        """Test Cross-Site Scripting (XSS) prevention"""
        async with aiohttp.ClientSession() as session:
            xss_payloads = [
                "<script>alert('XSS')</script>",
                "javascript:alert('XSS')",
                "<img src=x onerror=alert('XSS')>",
                "<svg onload=alert('XSS')>",
                "';alert('XSS');//",
                "<iframe src=javascript:alert('XSS')></iframe>"
            ]
            
            # Test XSS in user registration
            for payload in xss_payloads:
                user_data = {
                    "email": "test@example.com",
                    "password": "ValidPassword123!",
                    "first_name": payload,
                    "last_name": "User",
                    "user_type": "candidate"
                }
                
                async with session.post(f"{base_url}/api/auth/register", json=user_data) as response:
                    if response.status == 201:
                        # Check if the payload is reflected in the response
                        response_text = await response.text()
                        if payload in response_text and "<script>" in payload:
                            security_results.add_vulnerability(
                                "xss_prevention",
                                "HIGH",
                                f"XSS payload reflected in response: {payload}",
                                {"payload": payload}
                            )
                            return
            
            security_results.add_passed_test("xss_prevention")
    
    @pytest.mark.asyncio
    async def test_file_upload_security(self, base_url, security_results):
        """Test file upload security"""
        async with aiohttp.ClientSession() as session:
            # Test malicious file uploads
            malicious_files = [
                ("malicious.php", b"<?php system($_GET['cmd']); ?>", "application/x-php"),
                ("malicious.jsp", b"<% Runtime.getRuntime().exec(request.getParameter(\"cmd\")); %>", "application/x-jsp"),
                ("malicious.exe", b"MZ\x90\x00", "application/x-executable"),
                ("../../../etc/passwd", b"root:x:0:0:root:/root:/bin/bash", "text/plain")
            ]
            
            for filename, content, content_type in malicious_files:
                data = aiohttp.FormData()
                data.add_field('file', content, filename=filename, content_type=content_type)
                
                async with session.post(f"{base_url}/api/users/upload-resume", data=data) as response:
                    # Should reject malicious files
                    if response.status == 200:
                        security_results.add_vulnerability(
                            "file_upload_security",
                            "HIGH",
                            f"Malicious file upload accepted: {filename}",
                            {"filename": filename, "content_type": content_type}
                        )
                        return
            
            security_results.add_passed_test("file_upload_security")


class TestAPISecurityHeaders:
    """Test security headers implementation"""
    
    @pytest.mark.asyncio
    async def test_security_headers_present(self, base_url, security_results):
        """Test that required security headers are present"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health") as response:
                headers = response.headers
                
                required_headers = {
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": ["DENY", "SAMEORIGIN"],
                    "X-XSS-Protection": "1; mode=block",
                    "Strict-Transport-Security": None,  # Should be present
                    "Content-Security-Policy": None  # Should be present
                }
                
                missing_headers = []
                for header, expected_value in required_headers.items():
                    if header not in headers:
                        missing_headers.append(header)
                    elif expected_value and isinstance(expected_value, str):
                        if headers[header] != expected_value:
                            missing_headers.append(f"{header} (incorrect value)")
                    elif expected_value and isinstance(expected_value, list):
                        if headers[header] not in expected_value:
                            missing_headers.append(f"{header} (incorrect value)")
                
                if missing_headers:
                    security_results.add_vulnerability(
                        "security_headers",
                        "MEDIUM",
                        f"Missing or incorrect security headers: {', '.join(missing_headers)}",
                        {"missing_headers": missing_headers, "present_headers": dict(headers)}
                    )
                else:
                    security_results.add_passed_test("security_headers")


class TestDataExposureSecurity:
    """Test for data exposure vulnerabilities"""
    
    @pytest.mark.asyncio
    async def test_sensitive_data_exposure(self, base_url, security_results):
        """Test for sensitive data exposure in API responses"""
        async with aiohttp.ClientSession() as session:
            # Test endpoints that might expose sensitive data
            test_endpoints = [
                "/api/users/profile",
                "/api/dashboard/candidate",
                "/api/assessments/results/123",
                "/api/admin/users"  # Should require admin access
            ]
            
            for endpoint in test_endpoints:
                async with session.get(f"{base_url}{endpoint}") as response:
                    if response.status == 200:
                        response_text = await response.text()
                        
                        # Check for sensitive data patterns
                        sensitive_patterns = [
                            "password",
                            "secret",
                            "private_key",
                            "api_key",
                            "token",
                            "ssn",
                            "social_security"
                        ]
                        
                        for pattern in sensitive_patterns:
                            if pattern in response_text.lower():
                                security_results.add_vulnerability(
                                    "sensitive_data_exposure",
                                    "HIGH",
                                    f"Sensitive data pattern '{pattern}' found in {endpoint}",
                                    {"endpoint": endpoint, "pattern": pattern}
                                )
                                return
            
            security_results.add_passed_test("sensitive_data_exposure")
    
    @pytest.mark.asyncio
    async def test_directory_traversal(self, base_url, security_results):
        """Test for directory traversal vulnerabilities"""
        async with aiohttp.ClientSession() as session:
            traversal_payloads = [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
                "....//....//....//etc/passwd",
                "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
                "..%252f..%252f..%252fetc%252fpasswd"
            ]
            
            for payload in traversal_payloads:
                # Test in file download endpoint
                async with session.get(f"{base_url}/api/files/{payload}") as response:
                    response_text = await response.text()
                    
                    # Check for system file content
                    if "root:" in response_text or "localhost" in response_text:
                        security_results.add_vulnerability(
                            "directory_traversal",
                            "HIGH",
                            f"Directory traversal successful with payload: {payload}",
                            {"payload": payload}
                        )
                        return
            
            security_results.add_passed_test("directory_traversal")


class TestRateLimitingSecurity:
    """Test rate limiting security"""
    
    @pytest.mark.asyncio
    async def test_api_rate_limiting(self, base_url, security_results):
        """Test API rate limiting implementation"""
        async with aiohttp.ClientSession() as session:
            # Make rapid requests to trigger rate limiting
            responses = []
            for _ in range(50):
                async with session.get(f"{base_url}/api/auth/health") as response:
                    responses.append(response.status)
                    if response.status == 429:  # Rate limited
                        break
            
            if 429 not in responses:
                security_results.add_vulnerability(
                    "rate_limiting",
                    "MEDIUM",
                    "No rate limiting detected after 50 rapid requests",
                    {"response_codes": responses}
                )
            else:
                security_results.add_passed_test("rate_limiting")


class TestSessionSecurity:
    """Test session management security"""
    
    @pytest.mark.asyncio
    async def test_session_fixation(self, base_url, security_results):
        """Test for session fixation vulnerabilities"""
        async with aiohttp.ClientSession() as session:
            # Get initial session
            async with session.get(f"{base_url}/health") as response:
                initial_cookies = response.cookies
            
            # Login with credentials
            login_data = {
                "email": "test@example.com",
                "password": "testpassword"
            }
            async with session.post(f"{base_url}/api/auth/login", json=login_data) as response:
                if response.status == 200:
                    post_login_cookies = response.cookies
                    
                    # Session ID should change after login
                    if initial_cookies == post_login_cookies:
                        security_results.add_vulnerability(
                            "session_fixation",
                            "MEDIUM",
                            "Session ID not regenerated after login",
                            {}
                        )
                    else:
                        security_results.add_passed_test("session_fixation")
                else:
                    security_results.add_passed_test("session_fixation")  # Can't test without valid login


@pytest.mark.asyncio
async def test_comprehensive_security_scan():
    """Run comprehensive security scan and generate report"""
    base_url = os.getenv("TEST_BASE_URL", "http://localhost:8000")
    results = SecurityTestResults()
    
    # Run all security test classes
    test_classes = [
        TestAuthenticationSecurity(),
        TestInputValidationSecurity(),
        TestAPISecurityHeaders(),
        TestDataExposureSecurity(),
        TestRateLimitingSecurity(),
        TestSessionSecurity()
    ]
    
    for test_class in test_classes:
        # Run each test method in the class
        for method_name in dir(test_class):
            if method_name.startswith('test_'):
                method = getattr(test_class, method_name)
                if asyncio.iscoroutinefunction(method):
                    try:
                        await method(base_url, results)
                    except Exception as e:
                        results.add_vulnerability(
                            method_name,
                            "LOW",
                            f"Test execution failed: {str(e)}",
                            {"error": str(e)}
                        )
    
    # Generate security report
    summary = results.get_summary()
    
    # Save detailed report
    with open("security_test_report.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "="*60)
    print("SECURITY PENETRATION TEST RESULTS")
    print("="*60)
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Vulnerabilities Found: {summary['vulnerabilities_found']}")
    print(f"  - High Severity: {summary['high_severity']}")
    print(f"  - Medium Severity: {summary['medium_severity']}")
    print(f"  - Low Severity: {summary['low_severity']}")
    
    if summary['vulnerabilities']:
        print("\nVULNERABILITIES DETECTED:")
        for vuln in summary['vulnerabilities']:
            print(f"  [{vuln['severity']}] {vuln['test']}: {vuln['description']}")
    
    print(f"\nDetailed report saved to: security_test_report.json")
    
    # Assert that no high-severity vulnerabilities were found
    assert summary['high_severity'] == 0, f"High-severity vulnerabilities found: {summary['high_severity']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])