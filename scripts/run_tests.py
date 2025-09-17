#!/usr/bin/env python3
"""
Test runner script for the Turtle Species Identification App
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔧 {description}...")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Run tests for Turtle Species ID App')
    parser.add_argument('--type', choices=['unit', 'integration', 'backend', 'all', 'ci'], 
                       default='all', help='Type of tests to run')
    parser.add_argument('--coverage', action='store_true', 
                       help='Run with coverage reporting')
    parser.add_argument('--lint', action='store_true', 
                       help='Run linting checks')
    parser.add_argument('--security', action='store_true', 
                       help='Run security checks')
    parser.add_argument('--fast', action='store_true', 
                       help='Run only fast tests')
    
    args = parser.parse_args()
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("🐢 Turtle Species ID App - Test Runner")
    print("=" * 50)
    
    success = True
    
    # Install dependencies if needed
    if not Path("venv").exists():
        print("📦 Creating virtual environment...")
        if not run_command("python3 -m venv venv", "Creating virtual environment"):
            return 1
        
        print("📦 Installing dependencies...")
        if not run_command("venv/bin/pip install -r requirements.txt", "Installing dependencies"):
            return 1
    
    # Activate virtual environment
    if sys.platform == "win32":
        activate_cmd = "venv\\Scripts\\activate"
    else:
        activate_cmd = "source venv/bin/activate"
    
    # Run linting
    if args.lint or args.type == 'ci':
        success &= run_command(f"{activate_cmd} && flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics", 
                             "Linting check")
        success &= run_command(f"{activate_cmd} && flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics", 
                             "Style check")
    
    # Run security checks
    if args.security or args.type == 'ci':
        success &= run_command(f"{activate_cmd} && pip install bandit safety", 
                             "Installing security tools")
        success &= run_command(f"{activate_cmd} && bandit -r . -f txt", 
                             "Security scan with Bandit")
        success &= run_command(f"{activate_cmd} && safety check", 
                             "Dependency security check")
    
    # Run tests
    if args.type in ['unit', 'integration', 'all']:
        test_cmd = f"{activate_cmd} && pytest tests/ -v"
        
        if args.fast:
            test_cmd += " -m 'not slow'"
        
        if args.coverage or args.type == 'ci':
            test_cmd += " --cov=app --cov-report=html --cov-report=term-missing --cov-report=xml"
        
        if args.type == 'unit':
            test_cmd += " -m unit"
        elif args.type == 'integration':
            test_cmd += " -m integration"
        el        if args.type == 'backend':
            test_cmd += " tests/unit/test_app.py tests/unit/test_utils.py"
        
        success &= run_command(test_cmd, "Running tests")
    
    # Run CI pipeline
    if args.type == 'ci':
        success &= run_command(f"{activate_cmd} && python -c 'from app import app; print(\"✅ App imports successfully\")'", 
                             "App import test")
        
        # Test app startup (in background)
        print("\n🚀 Testing app startup...")
        try:
            # Start app in background
            process = subprocess.Popen([sys.executable, "app.py"], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
            
            # Wait a bit for app to start
            import time
            time.sleep(5)
            
            # Test health endpoint
            import requests
            try:
                response = requests.get("http://localhost:8080/health", timeout=5)
                if response.status_code == 200:
                    print("✅ App starts and responds to health check")
                else:
                    print(f"❌ Health check failed: {response.status_code}")
                    success = False
            except Exception as e:
                print(f"❌ Health check failed: {e}")
                success = False
            finally:
                # Kill the app
                process.terminate()
                process.wait()
                
        except Exception as e:
            print(f"❌ App startup test failed: {e}")
            success = False
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed successfully!")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
