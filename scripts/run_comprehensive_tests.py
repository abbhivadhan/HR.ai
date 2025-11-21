#!/usr/bin/env python3
"""
Comprehensive Test Runner for AI-HR Platform
Executes all testing phases for final integration and system testing
"""
import subprocess
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any
import argparse


class TestRunner:
    """Comprehensive test runner for the AI-HR Platform"""
    
    def __init__(self):
        self.results = {
            "start_time": time.time(),
            "end_time": None,
            "phases": {},
            "summary": {},
            "errors": []
        }
        self.base_dir = Path(__file__).parent.parent
        
    def run_command(self, command: str, description: str, cwd: str = None) -> Dict[str, Any]:
        """Run a command and capture results"""
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"Command: {command}")
        print('='*60)
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minutes timeout
                cwd=cwd or self.base_dir
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print("✅ PASSED")
                if result.stdout:
                    print(result.stdout)
                return {
                    "status": "passed",
                    "duration": duration,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                print("❌ FAILED")
                if result.stderr:
                    print(f"Error: {result.stderr}")
                if result.stdout:
                    print(f"Output: {result.stdout}")
                return {
                    "status": "failed",
                    "duration": duration,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode
                }
                
        except subprocess.TimeoutExpired:
            print("⏰ TIMEOUT - Command took too long to execute")
            return {
                "status": "timeout",
                "duration": time.time() - start_time,
                "error": "Command timeout"
            }
        except Exception as e:
            print(f"❌ ERROR - {str(e)}")
            return {
                "status": "error",
                "duration": time.time() - start_time,
                "error": str(e)
            }
    
    def run_phase_1_end_to_end_tests(self) -> Dict[str, Any]:
        """Phase 1: End-to-end testing of complete user journeys"""
        print("\n🚀 PHASE 1: END-TO-END USER JOURNEY TESTING")
        
        phase_results = {}
        
        # Run E2E tests
        result = self.run_command(
            "python -m pytest tests/e2e/test_complete_user_journeys.py -v --asyncio-mode=auto",
            "End-to-End User Journey Tests"
        )
        phase_results["e2e_tests"] = result
        
        return phase_results
    
    def run_phase_2_load_and_performance_tests(self) -> Dict[str, Any]:
        """Phase 2: Load testing and performance optimization"""
        print("\n⚡ PHASE 2: LOAD TESTING AND PERFORMANCE OPTIMIZATION")
        
        phase_results = {}
        
        # Run load tests
        result = self.run_command(
            "python -m pytest tests/load/test_performance_load.py -v --asyncio-mode=auto",
            "Load Testing and Performance Tests"
        )
        phase_results["load_tests"] = result
        
        # Run frontend performance tests
        frontend_result = self.run_command(
            "npm test -- --testPathPattern=performance.test.ts --watchAll=false",
            "Frontend Performance Tests",
            cwd=self.base_dir / "frontend"
        )
        phase_results["frontend_performance"] = frontend_result
        
        return phase_results
    
    def run_phase_3_security_penetration_tests(self) -> Dict[str, Any]:
        """Phase 3: Security penetration testing"""
        print("\n🔒 PHASE 3: SECURITY PENETRATION TESTING")
        
        phase_results = {}
        
        # Run security penetration tests
        result = self.run_command(
            "python -m pytest tests/security/test_penetration_security.py -v --asyncio-mode=auto",
            "Security Penetration Tests"
        )
        phase_results["penetration_tests"] = result
        
        # Run backend security assessment
        security_result = self.run_command(
            "python security_assessment.py",
            "Backend Security Assessment",
            cwd=self.base_dir / "backend"
        )
        phase_results["security_assessment"] = security_result
        
        return phase_results
    
    def run_phase_4_ai_ml_validation(self) -> Dict[str, Any]:
        """Phase 4: AI/ML model integration validation"""
        print("\n🤖 PHASE 4: AI/ML MODEL INTEGRATION VALIDATION")
        
        phase_results = {}
        
        # Run AI/ML validation tests
        result = self.run_command(
            "python -m pytest tests/ai_ml/test_model_validation.py -v --asyncio-mode=auto",
            "AI/ML Model Validation Tests"
        )
        phase_results["ai_ml_validation"] = result
        
        return phase_results
    
    def run_phase_5_cross_browser_mobile_tests(self) -> Dict[str, Any]:
        """Phase 5: Cross-browser and mobile compatibility testing"""
        print("\n📱 PHASE 5: CROSS-BROWSER AND MOBILE COMPATIBILITY TESTING")
        
        phase_results = {}
        
        # Run compatibility tests
        result = self.run_command(
            "python -m pytest tests/compatibility/test_cross_browser_mobile.py -v",
            "Cross-Browser and Mobile Compatibility Tests"
        )
        phase_results["compatibility_tests"] = result
        
        # Run frontend accessibility tests
        accessibility_result = self.run_command(
            "npm test -- --testPathPattern=accessibility.test.tsx --watchAll=false",
            "Frontend Accessibility Tests",
            cwd=self.base_dir / "frontend"
        )
        phase_results["accessibility_tests"] = accessibility_result
        
        return phase_results
    
    def run_phase_6_user_acceptance_tests(self) -> Dict[str, Any]:
        """Phase 6: User acceptance testing scenarios"""
        print("\n👥 PHASE 6: USER ACCEPTANCE TESTING")
        
        phase_results = {}
        
        # Run UAT tests
        result = self.run_command(
            "python -m pytest tests/uat/test_user_acceptance.py -v --asyncio-mode=auto",
            "User Acceptance Tests"
        )
        phase_results["uat_tests"] = result
        
        return phase_results
    
    def run_phase_7_deployment_validation(self) -> Dict[str, Any]:
        """Phase 7: Deployment validation and infrastructure tests"""
        print("\n🚀 PHASE 7: DEPLOYMENT VALIDATION")
        
        phase_results = {}
        
        # Run infrastructure tests
        infra_result = self.run_command(
            "python -m pytest tests/infrastructure/test_deployment.py -v --asyncio-mode=auto",
            "Infrastructure and Deployment Tests"
        )
        phase_results["infrastructure_tests"] = infra_result
        
        # Run deployment validation script
        deployment_result = self.run_command(
            "./scripts/deployment-validation.sh",
            "Deployment Validation Script"
        )
        phase_results["deployment_validation"] = deployment_result
        
        # Run monitoring tests
        monitoring_result = self.run_command(
            "python -m pytest tests/infrastructure/test_monitoring.py -v",
            "Monitoring System Tests"
        )
        phase_results["monitoring_tests"] = monitoring_result
        
        return phase_results
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run existing integration tests"""
        print("\n🔗 RUNNING EXISTING INTEGRATION TESTS")
        
        phase_results = {}
        
        # Backend API integration tests
        backend_result = self.run_command(
            "python -m pytest tests/test_api_integration.py -v",
            "Backend API Integration Tests",
            cwd=self.base_dir / "backend"
        )
        phase_results["backend_integration"] = backend_result
        
        # Frontend component tests
        frontend_result = self.run_command(
            "npm test -- --watchAll=false --coverage=false",
            "Frontend Component Tests",
            cwd=self.base_dir / "frontend"
        )
        phase_results["frontend_tests"] = frontend_result
        
        return phase_results
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        self.results["end_time"] = time.time()
        self.results["total_duration"] = self.results["end_time"] - self.results["start_time"]
        
        # Calculate summary statistics
        total_phases = len(self.results["phases"])
        passed_phases = 0
        failed_phases = 0
        
        for phase_name, phase_results in self.results["phases"].items():
            phase_passed = True
            for test_name, test_result in phase_results.items():
                if test_result.get("status") != "passed":
                    phase_passed = False
                    break
            
            if phase_passed:
                passed_phases += 1
            else:
                failed_phases += 1
        
        self.results["summary"] = {
            "total_phases": total_phases,
            "passed_phases": passed_phases,
            "failed_phases": failed_phases,
            "success_rate": passed_phases / total_phases if total_phases > 0 else 0,
            "total_duration_minutes": self.results["total_duration"] / 60
        }
        
        # Save detailed report
        report_file = self.base_dir / "comprehensive_test_report.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        # Generate summary report
        self.print_summary_report()
        
        return report_file
    
    def print_summary_report(self):
        """Print summary report to console"""
        print("\n" + "="*80)
        print("COMPREHENSIVE TESTING RESULTS SUMMARY")
        print("="*80)
        
        summary = self.results["summary"]
        print(f"Total Test Phases: {summary['total_phases']}")
        print(f"Passed Phases: {summary['passed_phases']}")
        print(f"Failed Phases: {summary['failed_phases']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Total Duration: {summary['total_duration_minutes']:.1f} minutes")
        
        print("\nPHASE RESULTS:")
        for phase_name, phase_results in self.results["phases"].items():
            print(f"\n📋 {phase_name.upper().replace('_', ' ')}")
            
            for test_name, test_result in phase_results.items():
                status = test_result.get("status", "unknown")
                duration = test_result.get("duration", 0)
                
                if status == "passed":
                    print(f"  ✅ {test_name}: PASSED ({duration:.1f}s)")
                elif status == "failed":
                    print(f"  ❌ {test_name}: FAILED ({duration:.1f}s)")
                    if "stderr" in test_result and test_result["stderr"]:
                        print(f"     Error: {test_result['stderr'][:200]}...")
                elif status == "timeout":
                    print(f"  ⏰ {test_name}: TIMEOUT ({duration:.1f}s)")
                else:
                    print(f"  ❓ {test_name}: {status.upper()} ({duration:.1f}s)")
        
        if self.results["errors"]:
            print("\nERRORS:")
            for error in self.results["errors"]:
                print(f"  - {error}")
        
        print(f"\nDetailed report saved to: comprehensive_test_report.json")
        
        # Final assessment
        if summary["success_rate"] >= 0.8:
            print("\n🎉 SYSTEM READY FOR PRODUCTION DEPLOYMENT!")
        elif summary["success_rate"] >= 0.6:
            print("\n⚠️  SYSTEM NEEDS ATTENTION BEFORE DEPLOYMENT")
        else:
            print("\n🚨 SYSTEM NOT READY FOR DEPLOYMENT - CRITICAL ISSUES DETECTED")
    
    def run_all_tests(self, phases: List[str] = None):
        """Run all test phases"""
        available_phases = {
            "e2e": self.run_phase_1_end_to_end_tests,
            "load": self.run_phase_2_load_and_performance_tests,
            "security": self.run_phase_3_security_penetration_tests,
            "ai_ml": self.run_phase_4_ai_ml_validation,
            "compatibility": self.run_phase_5_cross_browser_mobile_tests,
            "uat": self.run_phase_6_user_acceptance_tests,
            "deployment": self.run_phase_7_deployment_validation,
            "integration": self.run_integration_tests
        }
        
        if phases is None:
            phases = list(available_phases.keys())
        
        print(f"🚀 Starting Comprehensive Testing Suite")
        print(f"Phases to run: {', '.join(phases)}")
        print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        for phase in phases:
            if phase in available_phases:
                try:
                    phase_results = available_phases[phase]()
                    self.results["phases"][phase] = phase_results
                except Exception as e:
                    self.results["errors"].append(f"Phase {phase} failed with error: {str(e)}")
                    self.results["phases"][phase] = {"error": str(e)}
            else:
                print(f"⚠️  Unknown phase: {phase}")
                self.results["errors"].append(f"Unknown phase: {phase}")
        
        # Generate final report
        report_file = self.generate_comprehensive_report()
        
        return self.results["summary"]["success_rate"] >= 0.8


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run comprehensive tests for AI-HR Platform")
    parser.add_argument(
        "--phases",
        nargs="+",
        choices=["e2e", "load", "security", "ai_ml", "compatibility", "uat", "deployment", "integration"],
        help="Specific test phases to run (default: all)"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick validation tests only"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.quick:
        # Quick validation - essential tests only
        phases = ["integration", "security", "deployment"]
    else:
        phases = args.phases
    
    try:
        success = runner.run_all_tests(phases)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()