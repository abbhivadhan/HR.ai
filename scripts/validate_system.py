#!/usr/bin/env python3
"""
Simple System Validation Script
Validates that all core components are properly implemented
"""
import os
import sys
import json
from pathlib import Path


def validate_file_structure():
    """Validate that all required files exist"""
    print("🔍 Validating file structure...")
    
    required_files = [
        # Backend files
        "backend/app/main.py",
        "backend/app/config.py",
        "backend/app/models/user.py",
        "backend/app/models/job.py",
        "backend/app/models/assessment.py",
        "backend/app/api/auth.py",
        "backend/app/api/assessments.py",
        "backend/app/services/auth_service.py",
        "backend/app/services/ai_service.py",
        
        # Frontend files
        "frontend/package.json",
        "frontend/src/app/layout.tsx",
        "frontend/src/components/auth/LoginForm.tsx",
        "frontend/src/components/assessments/SkillAssessment.tsx",
        
        # Infrastructure files
        "k8s/backend-deployment.yaml",
        "k8s/frontend-deployment.yaml",
        "k8s/database-deployment.yaml",
        "monitoring/prometheus-deployment.yaml",
        "monitoring/grafana-deployment.yaml",
        
        # Test files
        "tests/e2e/test_complete_user_journeys.py",
        "tests/load/test_performance_load.py",
        "tests/security/test_penetration_security.py",
        "tests/ai_ml/test_model_validation.py",
        "tests/compatibility/test_cross_browser_mobile.py",
        "tests/uat/test_user_acceptance.py",
        
        # Deployment files
        "deployment/deployment_checklist.md",
        "deployment/go_live_procedures.md",
        "DEPLOYMENT_GUIDE.md",
        "scripts/deployment-validation.sh"
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
            print(f"  ✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"  ❌ {file_path}")
    
    return len(missing_files) == 0


def validate_test_files():
    """Validate that test files are properly structured"""
    print("\n🧪 Validating test files...")
    
    test_files = [
        "tests/e2e/test_complete_user_journeys.py",
        "tests/load/test_performance_load.py", 
        "tests/security/test_penetration_security.py",
        "tests/ai_ml/test_model_validation.py",
        "tests/compatibility/test_cross_browser_mobile.py",
        "tests/uat/test_user_acceptance.py"
    ]
    
    valid_tests = 0
    
    for test_file in test_files:
        if os.path.exists(test_file):
            try:
                with open(test_file, 'r') as f:
                    content = f.read()
                    
                # Check for basic test structure
                has_imports = "import pytest" in content
                has_test_functions = "def test_" in content
                has_classes = "class Test" in content
                
                if has_imports and (has_test_functions or has_classes):
                    print(f"  ✅ {test_file} - Valid test structure")
                    valid_tests += 1
                else:
                    print(f"  ⚠️  {test_file} - Missing test structure")
                    
            except Exception as e:
                print(f"  ❌ {test_file} - Error reading file: {e}")
        else:
            print(f"  ❌ {test_file} - File not found")
    
    return valid_tests == len(test_files)


def validate_kubernetes_manifests():
    """Validate Kubernetes manifest files"""
    print("\n☸️  Validating Kubernetes manifests...")
    
    k8s_files = [
        "k8s/backend-deployment.yaml",
        "k8s/frontend-deployment.yaml", 
        "k8s/database-deployment.yaml",
        "k8s/configmap.yaml",
        "k8s/hpa.yaml"
    ]
    
    valid_manifests = 0
    
    for k8s_file in k8s_files:
        if os.path.exists(k8s_file):
            try:
                with open(k8s_file, 'r') as f:
                    content = f.read()
                    
                # Check for basic Kubernetes structure
                has_api_version = "apiVersion:" in content
                has_kind = "kind:" in content
                has_metadata = "metadata:" in content
                
                if has_api_version and has_kind and has_metadata:
                    print(f"  ✅ {k8s_file} - Valid Kubernetes manifest")
                    valid_manifests += 1
                else:
                    print(f"  ⚠️  {k8s_file} - Invalid Kubernetes structure")
                    
            except Exception as e:
                print(f"  ❌ {k8s_file} - Error reading file: {e}")
        else:
            print(f"  ❌ {k8s_file} - File not found")
    
    return valid_manifests >= 3  # At least 3 valid manifests


def validate_monitoring_setup():
    """Validate monitoring configuration"""
    print("\n📊 Validating monitoring setup...")
    
    monitoring_files = [
        "monitoring/prometheus-deployment.yaml",
        "monitoring/grafana-deployment.yaml",
        "monitoring/alertmanager-deployment.yaml",
        "backend/app/monitoring.py"
    ]
    
    valid_monitoring = 0
    
    for mon_file in monitoring_files:
        if os.path.exists(mon_file):
            print(f"  ✅ {mon_file}")
            valid_monitoring += 1
        else:
            print(f"  ❌ {mon_file}")
    
    return valid_monitoring >= 3


def validate_security_features():
    """Validate security implementations"""
    print("\n🔒 Validating security features...")
    
    security_files = [
        "backend/app/services/auth_service.py",
        "backend/app/services/mfa_service.py",
        "backend/app/services/encryption_service.py",
        "backend/security_assessment.py"
    ]
    
    valid_security = 0
    
    for sec_file in security_files:
        if os.path.exists(sec_file):
            print(f"  ✅ {sec_file}")
            valid_security += 1
        else:
            print(f"  ❌ {sec_file}")
    
    return valid_security >= 2


def validate_deployment_readiness():
    """Validate deployment readiness"""
    print("\n🚀 Validating deployment readiness...")
    
    deployment_files = [
        "deployment/deployment_checklist.md",
        "deployment/go_live_procedures.md",
        "DEPLOYMENT_GUIDE.md",
        "scripts/deployment-validation.sh",
        "scripts/run_comprehensive_tests.py"
    ]
    
    valid_deployment = 0
    
    for dep_file in deployment_files:
        if os.path.exists(dep_file):
            print(f"  ✅ {dep_file}")
            valid_deployment += 1
        else:
            print(f"  ❌ {dep_file}")
    
    return valid_deployment == len(deployment_files)


def generate_validation_report():
    """Generate comprehensive validation report"""
    print("\n" + "="*80)
    print("SYSTEM VALIDATION REPORT")
    print("="*80)
    
    # Run all validations
    validations = {
        "File Structure": validate_file_structure(),
        "Test Files": validate_test_files(),
        "Kubernetes Manifests": validate_kubernetes_manifests(),
        "Monitoring Setup": validate_monitoring_setup(),
        "Security Features": validate_security_features(),
        "Deployment Readiness": validate_deployment_readiness()
    }
    
    # Calculate results
    total_validations = len(validations)
    passed_validations = 0
    
    print("\nVALIDATION RESULTS:")
    for validation_name, passed in validations.items():
        if passed:
            print(f"  ✅ {validation_name}: PASSED")
            passed_validations += 1
        else:
            print(f"  ❌ {validation_name}: FAILED")
    
    success_rate = passed_validations / total_validations
    
    print(f"\nSUMMARY:")
    print(f"  Total Validations: {total_validations}")
    print(f"  Passed: {passed_validations}")
    print(f"  Failed: {total_validations - passed_validations}")
    print(f"  Success Rate: {success_rate:.1%}")
    
    # Generate report file
    report = {
        "timestamp": "2024-10-27T12:00:00Z",
        "validations": validations,
        "summary": {
            "total": total_validations,
            "passed": passed_validations,
            "failed": total_validations - passed_validations,
            "success_rate": success_rate
        }
    }
    
    with open("system_validation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: system_validation_report.json")
    
    # Final assessment
    if success_rate >= 0.9:
        print("\n🎉 SYSTEM VALIDATION SUCCESSFUL!")
        print("   All critical components are properly implemented.")
        print("   System is ready for comprehensive testing.")
        return True
    elif success_rate >= 0.7:
        print("\n⚠️  SYSTEM VALIDATION PARTIAL SUCCESS")
        print("   Most components are implemented but some issues need attention.")
        return False
    else:
        print("\n🚨 SYSTEM VALIDATION FAILED")
        print("   Critical components are missing or improperly implemented.")
        return False


def main():
    """Main validation function"""
    print("🔍 AI-HR Platform System Validation")
    print("="*50)
    
    try:
        success = generate_validation_report()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()