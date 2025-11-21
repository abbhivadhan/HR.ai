"""
Cross-Browser and Mobile Compatibility Tests
Tests for browser compatibility and mobile responsiveness
"""
import pytest
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import json
import os
from typing import Dict, List, Any


class CompatibilityTestResults:
    """Container for compatibility test results"""
    
    def __init__(self):
        self.browser_results: Dict[str, Dict[str, Any]] = {}
        self.mobile_results: Dict[str, Dict[str, Any]] = {}
        self.performance_results: Dict[str, Dict[str, float]] = {}
        self.errors: List[str] = []
    
    def add_browser_result(self, browser: str, test_name: str, passed: bool, details: Dict = None):
        """Add browser test result"""
        if browser not in self.browser_results:
            self.browser_results[browser] = {}
        self.browser_results[browser][test_name] = {
            "passed": passed,
            "details": details or {}
        }
    
    def add_mobile_result(self, device: str, test_name: str, passed: bool, details: Dict = None):
        """Add mobile test result"""
        if device not in self.mobile_results:
            self.mobile_results[device] = {}
        self.mobile_results[device][test_name] = {
            "passed": passed,
            "details": details or {}
        }
    
    def add_performance_result(self, browser: str, metric: str, value: float):
        """Add performance result"""
        if browser not in self.performance_results:
            self.performance_results[browser] = {}
        self.performance_results[browser][metric] = value
    
    def add_error(self, error: str):
        """Add error message"""
        self.errors.append(error)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get compatibility test summary"""
        total_browser_tests = sum(len(tests) for tests in self.browser_results.values())
        passed_browser_tests = sum(
            sum(1 for test in tests.values() if test["passed"]) 
            for tests in self.browser_results.values()
        )
        
        total_mobile_tests = sum(len(tests) for tests in self.mobile_results.values())
        passed_mobile_tests = sum(
            sum(1 for test in tests.values() if test["passed"]) 
            for tests in self.mobile_results.values()
        )
        
        return {
            "browser_results": self.browser_results,
            "mobile_results": self.mobile_results,
            "performance_results": self.performance_results,
            "errors": self.errors,
            "summary": {
                "total_browser_tests": total_browser_tests,
                "passed_browser_tests": passed_browser_tests,
                "browser_success_rate": passed_browser_tests / total_browser_tests if total_browser_tests > 0 else 0,
                "total_mobile_tests": total_mobile_tests,
                "passed_mobile_tests": passed_mobile_tests,
                "mobile_success_rate": passed_mobile_tests / total_mobile_tests if total_mobile_tests > 0 else 0
            }
        }


class BrowserTestBase:
    """Base class for browser testing"""
    
    def __init__(self):
        self.base_url = os.getenv("TEST_BASE_URL", "http://localhost:3000")
        self.timeout = 10
    
    def get_chrome_driver(self, mobile_emulation=None):
        """Get Chrome WebDriver"""
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        if mobile_emulation:
            options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        try:
            return webdriver.Chrome(options=options)
        except WebDriverException as e:
            raise pytest.skip(f"Chrome driver not available: {e}")
    
    def get_firefox_driver(self):
        """Get Firefox WebDriver"""
        options = FirefoxOptions()
        options.add_argument("--headless")
        
        try:
            return webdriver.Firefox(options=options)
        except WebDriverException as e:
            raise pytest.skip(f"Firefox driver not available: {e}")
    
    def get_edge_driver(self):
        """Get Edge WebDriver"""
        options = EdgeOptions()
        options.add_argument("--headless")
        
        try:
            return webdriver.Edge(options=options)
        except WebDriverException as e:
            raise pytest.skip(f"Edge driver not available: {e}")


class TestCrossBrowserCompatibility(BrowserTestBase):
    """Test cross-browser compatibility"""
    
    @pytest.fixture
    def compatibility_results(self):
        return CompatibilityTestResults()
    
    def test_homepage_loading_all_browsers(self, compatibility_results):
        """Test homepage loading across different browsers"""
        browsers = [
            ("chrome", self.get_chrome_driver),
            ("firefox", self.get_firefox_driver),
            ("edge", self.get_edge_driver)
        ]
        
        for browser_name, driver_func in browsers:
            try:
                driver = driver_func()
                
                # Navigate to homepage
                start_time = time.time()
                driver.get(self.base_url)
                load_time = time.time() - start_time
                
                # Check if page loaded successfully
                try:
                    WebDriverWait(driver, self.timeout).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Check for basic elements
                    title = driver.title
                    body_text = driver.find_element(By.TAG_NAME, "body").text
                    
                    success = len(title) > 0 and len(body_text) > 0
                    
                    compatibility_results.add_browser_result(
                        browser_name, 
                        "homepage_loading", 
                        success,
                        {"load_time": load_time, "title": title}
                    )
                    compatibility_results.add_performance_result(browser_name, "homepage_load_time", load_time)
                    
                except TimeoutException:
                    compatibility_results.add_browser_result(
                        browser_name, 
                        "homepage_loading", 
                        False,
                        {"error": "Page load timeout"}
                    )
                
                driver.quit()
                
            except Exception as e:
                compatibility_results.add_error(f"Browser {browser_name} test failed: {str(e)}")
                compatibility_results.add_browser_result(browser_name, "homepage_loading", False, {"error": str(e)})
    
    def test_login_form_all_browsers(self, compatibility_results):
        """Test login form functionality across browsers"""
        browsers = [
            ("chrome", self.get_chrome_driver),
            ("firefox", self.get_firefox_driver)
        ]
        
        for browser_name, driver_func in browsers:
            try:
                driver = driver_func()
                driver.get(f"{self.base_url}/login")
                
                # Wait for login form
                try:
                    email_input = WebDriverWait(driver, self.timeout).until(
                        EC.presence_of_element_located((By.NAME, "email"))
                    )
                    password_input = driver.find_element(By.NAME, "password")
                    login_button = driver.find_element(By.TYPE, "submit")
                    
                    # Test form interaction
                    email_input.send_keys("test@example.com")
                    password_input.send_keys("testpassword")
                    
                    # Check if form elements are functional
                    email_value = email_input.get_attribute("value")
                    password_value = password_input.get_attribute("value")
                    
                    form_functional = (
                        email_value == "test@example.com" and 
                        len(password_value) > 0 and
                        login_button.is_enabled()
                    )
                    
                    compatibility_results.add_browser_result(
                        browser_name,
                        "login_form",
                        form_functional,
                        {"email_input": email_value, "button_enabled": login_button.is_enabled()}
                    )
                    
                except TimeoutException:
                    compatibility_results.add_browser_result(
                        browser_name,
                        "login_form",
                        False,
                        {"error": "Login form not found"}
                    )
                
                driver.quit()
                
            except Exception as e:
                compatibility_results.add_error(f"Login form test failed for {browser_name}: {str(e)}")
                compatibility_results.add_browser_result(browser_name, "login_form", False, {"error": str(e)})
    
    def test_javascript_functionality_all_browsers(self, compatibility_results):
        """Test JavaScript functionality across browsers"""
        browsers = [
            ("chrome", self.get_chrome_driver),
            ("firefox", self.get_firefox_driver)
        ]
        
        for browser_name, driver_func in browsers:
            try:
                driver = driver_func()
                driver.get(self.base_url)
                
                # Test JavaScript execution
                js_result = driver.execute_script("return typeof window.React !== 'undefined';")
                
                # Test local storage
                driver.execute_script("localStorage.setItem('test', 'value');")
                storage_result = driver.execute_script("return localStorage.getItem('test');")
                
                # Test console errors
                logs = driver.get_log('browser')
                console_errors = [log for log in logs if log['level'] == 'SEVERE']
                
                js_functional = (
                    js_result and 
                    storage_result == 'value' and 
                    len(console_errors) == 0
                )
                
                compatibility_results.add_browser_result(
                    browser_name,
                    "javascript_functionality",
                    js_functional,
                    {
                        "react_available": js_result,
                        "local_storage_works": storage_result == 'value',
                        "console_errors": len(console_errors)
                    }
                )
                
                driver.quit()
                
            except Exception as e:
                compatibility_results.add_error(f"JavaScript test failed for {browser_name}: {str(e)}")
                compatibility_results.add_browser_result(browser_name, "javascript_functionality", False, {"error": str(e)})


class TestMobileCompatibility(BrowserTestBase):
    """Test mobile device compatibility"""
    
    def test_mobile_responsive_design(self, compatibility_results):
        """Test responsive design on mobile devices"""
        mobile_devices = [
            {
                "name": "iPhone_12",
                "deviceMetrics": {
                    "width": 390,
                    "height": 844,
                    "pixelRatio": 3.0
                },
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
            },
            {
                "name": "Samsung_Galaxy_S21",
                "deviceMetrics": {
                    "width": 384,
                    "height": 854,
                    "pixelRatio": 2.0
                },
                "userAgent": "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36"
            },
            {
                "name": "iPad",
                "deviceMetrics": {
                    "width": 768,
                    "height": 1024,
                    "pixelRatio": 2.0
                },
                "userAgent": "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
            }
        ]
        
        for device in mobile_devices:
            try:
                driver = self.get_chrome_driver(mobile_emulation=device)
                driver.get(self.base_url)
                
                # Wait for page load
                WebDriverWait(driver, self.timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Check viewport
                viewport_width = driver.execute_script("return window.innerWidth;")
                viewport_height = driver.execute_script("return window.innerHeight;")
                
                # Check if navigation is mobile-friendly
                try:
                    nav_element = driver.find_element(By.TAG_NAME, "nav")
                    nav_display = nav_element.value_of_css_property("display")
                    
                    # Check for mobile menu (hamburger menu)
                    mobile_menu_elements = driver.find_elements(By.CSS_SELECTOR, ".mobile-menu, .hamburger, [data-testid='mobile-menu']")
                    has_mobile_menu = len(mobile_menu_elements) > 0
                    
                except:
                    nav_display = "none"
                    has_mobile_menu = False
                
                # Check text readability (font size should be reasonable)
                body_font_size = driver.execute_script(
                    "return window.getComputedStyle(document.body).fontSize;"
                )
                font_size_px = int(body_font_size.replace('px', '')) if 'px' in body_font_size else 16
                
                # Check for horizontal scrolling
                has_horizontal_scroll = driver.execute_script(
                    "return document.body.scrollWidth > window.innerWidth;"
                )
                
                mobile_friendly = (
                    viewport_width <= device["deviceMetrics"]["width"] + 50 and  # Allow some tolerance
                    font_size_px >= 14 and  # Minimum readable font size
                    not has_horizontal_scroll and
                    (has_mobile_menu or nav_display != "none")
                )
                
                compatibility_results.add_mobile_result(
                    device["name"],
                    "responsive_design",
                    mobile_friendly,
                    {
                        "viewport_width": viewport_width,
                        "viewport_height": viewport_height,
                        "font_size": font_size_px,
                        "has_horizontal_scroll": has_horizontal_scroll,
                        "has_mobile_menu": has_mobile_menu
                    }
                )
                
                driver.quit()
                
            except Exception as e:
                compatibility_results.add_error(f"Mobile test failed for {device['name']}: {str(e)}")
                compatibility_results.add_mobile_result(device["name"], "responsive_design", False, {"error": str(e)})
    
    def test_touch_interactions(self, compatibility_results):
        """Test touch interactions on mobile"""
        mobile_device = {
            "deviceMetrics": {
                "width": 390,
                "height": 844,
                "pixelRatio": 3.0
            },
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        }
        
        try:
            driver = self.get_chrome_driver(mobile_emulation=mobile_device)
            driver.get(f"{self.base_url}/login")
            
            # Test touch interactions
            try:
                email_input = WebDriverWait(driver, self.timeout).until(
                    EC.element_to_be_clickable((By.NAME, "email"))
                )
                
                # Test tap interaction
                email_input.click()
                email_input.send_keys("test@example.com")
                
                # Check if virtual keyboard considerations are in place
                # (viewport should adjust or inputs should be accessible)
                input_rect = email_input.rect
                viewport_height = driver.execute_script("return window.innerHeight;")
                
                input_accessible = input_rect['y'] < viewport_height * 0.7  # Input should be in upper 70% of screen
                
                compatibility_results.add_mobile_result(
                    "mobile_touch",
                    "touch_interactions",
                    input_accessible,
                    {
                        "input_position": input_rect,
                        "viewport_height": viewport_height,
                        "input_accessible": input_accessible
                    }
                )
                
            except TimeoutException:
                compatibility_results.add_mobile_result(
                    "mobile_touch",
                    "touch_interactions",
                    False,
                    {"error": "Touch elements not found"}
                )
            
            driver.quit()
            
        except Exception as e:
            compatibility_results.add_error(f"Touch interaction test failed: {str(e)}")
            compatibility_results.add_mobile_result("mobile_touch", "touch_interactions", False, {"error": str(e)})


class TestPerformanceAcrossBrowsers(BrowserTestBase):
    """Test performance across different browsers"""
    
    def test_page_load_performance(self, compatibility_results):
        """Test page load performance across browsers"""
        browsers = [
            ("chrome", self.get_chrome_driver),
            ("firefox", self.get_firefox_driver)
        ]
        
        for browser_name, driver_func in browsers:
            try:
                driver = driver_func()
                
                # Navigate and measure performance
                start_time = time.time()
                driver.get(self.base_url)
                
                # Wait for page to be fully loaded
                WebDriverWait(driver, self.timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Get performance metrics
                navigation_timing = driver.execute_script(
                    "return window.performance.timing;"
                )
                
                if navigation_timing:
                    load_time = (navigation_timing['loadEventEnd'] - navigation_timing['navigationStart']) / 1000
                    dom_ready_time = (navigation_timing['domContentLoadedEventEnd'] - navigation_timing['navigationStart']) / 1000
                    
                    compatibility_results.add_performance_result(browser_name, "page_load_time", load_time)
                    compatibility_results.add_performance_result(browser_name, "dom_ready_time", dom_ready_time)
                    
                    # Performance should be reasonable
                    performance_acceptable = load_time < 5.0 and dom_ready_time < 3.0
                    
                    compatibility_results.add_browser_result(
                        browser_name,
                        "page_load_performance",
                        performance_acceptable,
                        {
                            "load_time": load_time,
                            "dom_ready_time": dom_ready_time
                        }
                    )
                else:
                    compatibility_results.add_browser_result(
                        browser_name,
                        "page_load_performance",
                        False,
                        {"error": "Performance timing not available"}
                    )
                
                driver.quit()
                
            except Exception as e:
                compatibility_results.add_error(f"Performance test failed for {browser_name}: {str(e)}")
                compatibility_results.add_browser_result(browser_name, "page_load_performance", False, {"error": str(e)})


class TestAccessibilityCompatibility(BrowserTestBase):
    """Test accessibility across browsers"""
    
    def test_keyboard_navigation(self, compatibility_results):
        """Test keyboard navigation compatibility"""
        browsers = [
            ("chrome", self.get_chrome_driver),
            ("firefox", self.get_firefox_driver)
        ]
        
        for browser_name, driver_func in browsers:
            try:
                driver = driver_func()
                driver.get(f"{self.base_url}/login")
                
                # Test tab navigation
                try:
                    body = driver.find_element(By.TAG_NAME, "body")
                    body.click()  # Focus on page
                    
                    # Send Tab key to navigate
                    from selenium.webdriver.common.keys import Keys
                    body.send_keys(Keys.TAB)
                    
                    # Check if focus moved to a focusable element
                    active_element = driver.switch_to.active_element
                    active_tag = active_element.tag_name.lower()
                    
                    # Should focus on input, button, or link
                    keyboard_navigation_works = active_tag in ['input', 'button', 'a', 'select', 'textarea']
                    
                    compatibility_results.add_browser_result(
                        browser_name,
                        "keyboard_navigation",
                        keyboard_navigation_works,
                        {
                            "active_element_tag": active_tag,
                            "navigation_works": keyboard_navigation_works
                        }
                    )
                    
                except Exception as e:
                    compatibility_results.add_browser_result(
                        browser_name,
                        "keyboard_navigation",
                        False,
                        {"error": str(e)}
                    )
                
                driver.quit()
                
            except Exception as e:
                compatibility_results.add_error(f"Keyboard navigation test failed for {browser_name}: {str(e)}")
                compatibility_results.add_browser_result(browser_name, "keyboard_navigation", False, {"error": str(e)})


@pytest.mark.compatibility
def test_comprehensive_compatibility():
    """Run comprehensive compatibility testing"""
    results = CompatibilityTestResults()
    
    # Run all test classes
    test_classes = [
        TestCrossBrowserCompatibility(),
        TestMobileCompatibility(),
        TestPerformanceAcrossBrowsers(),
        TestAccessibilityCompatibility()
    ]
    
    for test_class in test_classes:
        for method_name in dir(test_class):
            if method_name.startswith('test_'):
                method = getattr(test_class, method_name)
                try:
                    method(results)
                except Exception as e:
                    results.add_error(f"Test {method_name} failed: {str(e)}")
    
    # Generate compatibility report
    summary = results.get_summary()
    
    # Save detailed report
    with open("compatibility_test_report.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "="*60)
    print("CROSS-BROWSER & MOBILE COMPATIBILITY RESULTS")
    print("="*60)
    print(f"Browser Tests: {summary['summary']['passed_browser_tests']}/{summary['summary']['total_browser_tests']} passed")
    print(f"Browser Success Rate: {summary['summary']['browser_success_rate']:.1%}")
    print(f"Mobile Tests: {summary['summary']['passed_mobile_tests']}/{summary['summary']['total_mobile_tests']} passed")
    print(f"Mobile Success Rate: {summary['summary']['mobile_success_rate']:.1%}")
    print(f"Errors: {len(summary['errors'])}")
    
    if summary['performance_results']:
        print("\nPERFORMANCE RESULTS:")
        for browser, metrics in summary['performance_results'].items():
            print(f"  {browser}:")
            for metric, value in metrics.items():
                print(f"    {metric}: {value:.2f}s")
    
    if summary['errors']:
        print("\nERRORS:")
        for error in summary['errors']:
            print(f"  - {error}")
    
    print(f"\nDetailed report saved to: compatibility_test_report.json")
    
    # Assert minimum compatibility requirements
    assert summary['summary']['browser_success_rate'] > 0.8, f"Browser compatibility too low: {summary['summary']['browser_success_rate']:.1%}"
    assert summary['summary']['mobile_success_rate'] > 0.7, f"Mobile compatibility too low: {summary['summary']['mobile_success_rate']:.1%}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])