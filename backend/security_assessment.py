#!/usr/bin/env python3
"""
Security Vulnerability Assessment Script
Runs various security checks on the AI-HR Platform
"""
import subprocess
import sys
import os
import json
from pathlib import Path


def run_command(command, description):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*60)
    
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            print("✅ PASSED")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ FAILED")
            if result.stderr:
                print(f"Error: {result.stderr}")
            if result.stdout:
                print(f"Output: {result.stdout}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT - Command took too long to execute")
        return False
    except FileNotFoundError:
        print(f"❌ TOOL NOT FOUND - Please install the required tool")
        return False
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")
        return False


def check_dependencies():
    """Check if required security tools are installed"""
    tools = {
        'bandit': 'pip install bandit',
        'safety': 'pip install safety',
        'semgrep': 'pip install semgrep'
    }
    
    missing_tools = []
    
    for tool, install_cmd in tools.items():
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True)
            print(f"✅ {tool} is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {tool} is not installed. Install with: {install_cmd}")
            missing_tools.append(tool)
    
    return len(missing_tools) == 0


def run_bandit_scan():
    """Run Bandit security linter for Python code"""
    return run_command(
        "bandit -r app/ -f json -o bandit_report.json",
        "Bandit Security Scan - Python security issues"
    )


def run_safety_check():
    """Run Safety check for known security vulnerabilities in dependencies"""
    return run_command(
        "safety check --json --output safety_report.json",
        "Safety Check - Known vulnerabilities in dependencies"
    )


def run_semgrep_scan():
    """Run Semgrep for additional security patterns"""
    return run_command(
        "semgrep --config=auto app/ --json --output=semgrep_report.json",
        "Semgrep Security Scan - Advanced security patterns"
    )


def check_file_permissions():
    """Check file permissions for sensitive files"""
    print(f"\n{'='*60}")
    print("Checking File Permissions")
    print('='*60)
    
    sensitive_files = [
        '.env',
        'app/config.py',
        'requirements.txt'
    ]
    
    issues = []
    
    for file_path in sensitive_files:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            permissions = oct(stat.st_mode)[-3:]
            
            if file_path == '.env' and permissions != '600':
                issues.append(f"{file_path} has permissions {permissions}, should be 600")
            elif permissions.endswith('7'):  # World writable
                issues.append(f"{file_path} is world writable ({permissions})")
            
            print(f"{file_path}: {permissions}")
        else:
            print(f"{file_path}: Not found")
    
    if issues:
        print("\n❌ Permission Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("\n✅ File permissions look good")
        return True


def check_secrets_in_code():
    """Check for hardcoded secrets in code"""
    print(f"\n{'='*60}")
    print("Checking for Hardcoded Secrets")
    print('='*60)
    
    secret_patterns = [
        'password.*=.*["\'][^"\']{8,}["\']',
        'secret.*=.*["\'][^"\']{16,}["\']',
        'api_key.*=.*["\'][^"\']{16,}["\']',
        'token.*=.*["\'][^"\']{16,}["\']'
    ]
    
    issues = []
    
    for root, dirs, files in os.walk('app'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        for i, line in enumerate(content.split('\n'), 1):
                            for pattern in secret_patterns:
                                import re
                                if re.search(pattern, line, re.IGNORECASE):
                                    # Skip if it's a placeholder or example
                                    if any(placeholder in line.lower() for placeholder in 
                                          ['your-secret', 'change-in-production', 'example', 'placeholder']):
                                        continue
                                    issues.append(f"{file_path}:{i} - Potential hardcoded secret")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    if issues:
        print("❌ Potential hardcoded secrets found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ No hardcoded secrets detected")
        return True


def check_security_headers():
    """Check if security headers are implemented"""
    print(f"\n{'='*60}")
    print("Checking Security Headers Implementation")
    print('='*60)
    
    main_py_path = 'app/main.py'
    
    if not os.path.exists(main_py_path):
        print("❌ main.py not found")
        return False
    
    with open(main_py_path, 'r') as f:
        content = f.read()
    
    required_headers = [
        'X-Content-Type-Options',
        'X-Frame-Options',
        'X-XSS-Protection',
        'Strict-Transport-Security',
        'Content-Security-Policy'
    ]
    
    missing_headers = []
    
    for header in required_headers:
        if header not in content:
            missing_headers.append(header)
    
    if missing_headers:
        print("❌ Missing security headers:")
        for header in missing_headers:
            print(f"  - {header}")
        return False
    else:
        print("✅ All required security headers are implemented")
        return True


def check_authentication_security():
    """Check authentication security implementation"""
    print(f"\n{'='*60}")
    print("Checking Authentication Security")
    print('='*60)
    
    auth_files = [
        'app/auth/utils.py',
        'app/services/auth_service.py',
        'app/services/mfa_service.py'
    ]
    
    security_features = {
        'password hashing': ['bcrypt', 'get_password_hash'],
        'JWT tokens': ['jwt.encode', 'create_access_token'],
        'MFA support': ['pyotp', 'TOTP'],
        'rate limiting': ['rate_limit', 'check_rate_limit'],
        'account locking': ['locked_until', 'failed_login_attempts']
    }
    
    implemented_features = []
    missing_features = []
    
    for file_path in auth_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                
                for feature, keywords in security_features.items():
                    if any(keyword in content for keyword in keywords):
                        if feature not in implemented_features:
                            implemented_features.append(feature)
    
    for feature in security_features.keys():
        if feature not in implemented_features:
            missing_features.append(feature)
    
    print("✅ Implemented security features:")
    for feature in implemented_features:
        print(f"  - {feature}")
    
    if missing_features:
        print("\n❌ Missing security features:")
        for feature in missing_features:
            print(f"  - {feature}")
        return False
    else:
        print("\n✅ All authentication security features are implemented")
        return True


def generate_security_report():
    """Generate a comprehensive security report"""
    print(f"\n{'='*60}")
    print("SECURITY ASSESSMENT SUMMARY")
    print('='*60)
    
    # Read generated reports
    reports = {}
    
    report_files = {
        'bandit': 'bandit_report.json',
        'safety': 'safety_report.json',
        'semgrep': 'semgrep_report.json'
    }
    
    for tool, filename in report_files.items():
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    reports[tool] = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {filename}")
    
    # Generate summary
    summary = {
        'timestamp': subprocess.run(['date'], capture_output=True, text=True).stdout.strip(),
        'total_issues': 0,
        'high_severity': 0,
        'medium_severity': 0,
        'low_severity': 0,
        'tools_run': list(reports.keys()),
        'recommendations': []
    }
    
    # Analyze Bandit results
    if 'bandit' in reports:
        bandit_results = reports['bandit']
        if 'results' in bandit_results:
            for issue in bandit_results['results']:
                summary['total_issues'] += 1
                severity = issue.get('issue_severity', 'LOW').upper()
                if severity == 'HIGH':
                    summary['high_severity'] += 1
                elif severity == 'MEDIUM':
                    summary['medium_severity'] += 1
                else:
                    summary['low_severity'] += 1
    
    # Analyze Safety results
    if 'safety' in reports:
        safety_results = reports['safety']
        if isinstance(safety_results, list):
            summary['total_issues'] += len(safety_results)
            summary['high_severity'] += len(safety_results)  # All vulnerabilities are high
    
    # Generate recommendations
    if summary['high_severity'] > 0:
        summary['recommendations'].append("Address high-severity security issues immediately")
    
    if summary['total_issues'] == 0:
        summary['recommendations'].append("Great! No security issues detected")
    else:
        summary['recommendations'].append("Review and fix identified security issues")
    
    summary['recommendations'].extend([
        "Regularly update dependencies to patch security vulnerabilities",
        "Implement security monitoring and alerting",
        "Conduct regular security assessments",
        "Train developers on secure coding practices"
    ])
    
    # Save summary report
    with open('security_assessment_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Total Issues Found: {summary['total_issues']}")
    print(f"High Severity: {summary['high_severity']}")
    print(f"Medium Severity: {summary['medium_severity']}")
    print(f"Low Severity: {summary['low_severity']}")
    print(f"\nRecommendations:")
    for rec in summary['recommendations']:
        print(f"  - {rec}")
    
    print(f"\nDetailed reports saved:")
    for tool in summary['tools_run']:
        print(f"  - {report_files[tool]}")
    print(f"  - security_assessment_summary.json")


def main():
    """Main function to run security assessment"""
    print("🔒 AI-HR Platform Security Assessment")
    print("="*60)
    
    # Change to backend directory if not already there
    if os.path.exists('backend'):
        os.chdir('backend')
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Missing required tools. Please install them and run again.")
        sys.exit(1)
    
    # Run security checks
    checks = [
        check_file_permissions,
        check_secrets_in_code,
        check_security_headers,
        check_authentication_security,
        run_bandit_scan,
        run_safety_check,
        # run_semgrep_scan,  # Optional, might not be available
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"Error running check: {e}")
            results.append(False)
    
    # Generate final report
    generate_security_report()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n{'='*60}")
    print(f"FINAL RESULTS: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All security checks passed!")
        sys.exit(0)
    else:
        print("⚠️  Some security issues need attention")
        sys.exit(1)


if __name__ == "__main__":
    main()