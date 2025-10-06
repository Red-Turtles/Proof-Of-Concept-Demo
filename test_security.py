#!/usr/bin/env python3
"""
Simple test script for the security features
Run this to test the CAPTCHA and rate limiting functionality
"""

import requests
import json
import time
import sys

def test_security_features():
    """Test the security features of the app"""
    base_url = "http://localhost:3000"
    
    print("🔒 Testing Security Features")
    print("=" * 50)
    
    # Test 1: Get security status
    print("\n1. Testing security status endpoint...")
    try:
        response = requests.get(f"{base_url}/api/security/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Security status: {status}")
        else:
            print(f"❌ Failed to get security status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting security status: {e}")
    
    # Test 2: Generate CAPTCHA
    print("\n2. Testing CAPTCHA generation...")
    try:
        response = requests.post(f"{base_url}/api/security/captcha")
        if response.status_code == 200:
            captcha_data = response.json()
            print(f"✅ CAPTCHA generated: {captcha_data['question']}")
            
            # Test 3: Verify CAPTCHA with wrong answer
            print("\n3. Testing CAPTCHA verification with wrong answer...")
            verify_data = {
                "captcha_id": captcha_data["captcha_id"],
                "answer": "999"  # Wrong answer
            }
            response = requests.post(f"{base_url}/api/security/verify", json=verify_data)
            if response.status_code == 400:
                result = response.json()
                print(f"✅ CAPTCHA correctly rejected wrong answer: {result}")
            else:
                print(f"❌ CAPTCHA should have rejected wrong answer: {response.status_code}")
            
            # Test 4: Verify CAPTCHA with correct answer
            print("\n4. Testing CAPTCHA verification with correct answer...")
            # Calculate correct answer (simple math)
            question = captcha_data["question"]
            try:
                # Parse the math question
                if " + " in question:
                    parts = question.split(" + ")
                    correct_answer = int(parts[0]) + int(parts[1])
                elif " - " in question:
                    parts = question.split(" - ")
                    correct_answer = int(parts[0]) - int(parts[1])
                elif " × " in question:
                    parts = question.split(" × ")
                    correct_answer = int(parts[0]) * int(parts[1])
                else:
                    print(f"❌ Could not parse CAPTCHA question: {question}")
                    return
                
                verify_data["answer"] = str(correct_answer)
                response = requests.post(f"{base_url}/api/security/verify", json=verify_data)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ CAPTCHA correctly accepted correct answer: {result}")
                else:
                    print(f"❌ CAPTCHA should have accepted correct answer: {response.status_code}")
            except Exception as e:
                print(f"❌ Error calculating CAPTCHA answer: {e}")
                
        else:
            print(f"❌ Failed to generate CAPTCHA: {response.status_code}")
    except Exception as e:
        print(f"❌ Error generating CAPTCHA: {e}")
    
    # Test 5: Test main page loads
    print("\n5. Testing main page loads...")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ Main page loads successfully")
        else:
            print(f"❌ Main page failed to load: {response.status_code}")
    except Exception as e:
        print(f"❌ Error loading main page: {e}")
    
    print("\n" + "=" * 50)
    print("🔒 Security Feature Tests Complete")
    print("\nNote: To test rate limiting, you would need to make multiple")
    print("requests to trigger the CAPTCHA requirement.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:3000"
    
    print(f"Testing security features at: {base_url}")
    print("Make sure the Flask app is running first!")
    print()
    
    try:
        test_security_features()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
