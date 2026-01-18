"""
Test script for Phishing Detection API

Tests all endpoints with example requests
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_root():
    """Test root endpoint"""
    print("\n" + "="*50)
    print("Testing Root Endpoint")
    print("="*50)
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_predict_email():
    """Test email prediction endpoint"""
    print("\n" + "="*50)
    print("Testing Email Prediction")
    print("="*50)
    
    test_cases = [
        {
            "name": "Spam email",
            "text": "You have won $1000000! Click here now to claim your prize! URGENT!"
        },
        {
            "name": "Normal email",
            "text": "Hi, I wanted to follow up on our meeting scheduled for tomorrow at 3pm. Thanks!"
        },
        {
            "name": "Suspicious email",
            "text": "URGENT: Verify your account immediately or it will be suspended. Click here: http://verify-account.com"
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print(f"Text: {test_case['text'][:50]}...")
        
        response = requests.post(
            f"{BASE_URL}/predict-email",
            json={"text": test_case["text"]}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  Prediction: {'SPAM' if result['prediction'] == 1 else 'NOT SPAM'}")
            print(f"  Probability: {result['probability']:.4f}")
            print(f"  Confidence: {result['confidence']:.4f}")
        else:
            print(f"  Error: {response.status_code} - {response.text}")


def test_predict_url():
    """Test URL prediction endpoint"""
    print("\n" + "="*50)
    print("Testing URL Prediction")
    print("="*50)
    
    test_cases = [
        {
            "name": "Phishing URL",
            "url": "http://paypal-security-verify.com/login"
        },
        {
            "name": "Safe URL",
            "url": "https://www.paypal.com/login"
        },
        {
            "name": "Suspicious URL",
            "url": "http://bank-verify-now.com/secure"
        },
        {
            "name": "Wikipedia URL",
            "url": "https://en.wikipedia.org/wiki/Phishing"
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print(f"URL: {test_case['url']}")
        
        response = requests.post(
            f"{BASE_URL}/predict-url",
            json={"url": test_case["url"]}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  Prediction: {'PHISHING' if result['prediction'] == 1 else 'SAFE'}")
            print(f"  Probability: {result['probability']:.4f}")
            print(f"  Confidence: {result['confidence']:.4f}")
        else:
            print(f"  Error: {response.status_code} - {response.text}")


def test_analyze_email():
    """Test comprehensive analysis endpoint"""
    print("\n" + "="*50)
    print("Testing Comprehensive Analysis")
    print("="*50)
    
    test_cases = [
        {
            "name": "Suspicious email with URLs",
            "text": "URGENT: Your account will be suspended. Verify now at http://verify-account-now.com",
            "urls": ["http://verify-account-now.com"],
            "images_b64": []
        },
        {
            "name": "Normal email",
            "text": "Hi John, thanks for the meeting today. Let's schedule a follow-up next week.",
            "urls": [],
            "images_b64": []
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print(f"Text: {test_case['text'][:60]}...")
        
        response = requests.post(
            f"{BASE_URL}/analyze_email",
            json={
                "text": test_case["text"],
                "urls": test_case["urls"],
                "images_b64": test_case["images_b64"]
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  Risk Score: {result['risk_score']:.4f}")
            print(f"  NLP Score: {result['nlp_score']:.4f}")
            print(f"  URL Score: {result['url_score']:.4f}")
            print(f"  Vision Score: {result['vision_score']:.4f}")
            print(f"  Factors: {result['explainability']['factors']}")
            if result['explainability']['warnings']:
                print(f"  Warnings: {result['explainability']['warnings']}")
        else:
            print(f"  Error: {response.status_code} - {response.text}")


def main():
    """Run all tests"""
    print("="*50)
    print("Phishing Detection API Test Suite")
    print("="*50)
    print("\nMake sure the API server is running on http://localhost:8000")
    print("Press Enter to continue...")
    input()
    
    try:
        # Test root endpoint
        test_root()
        
        # Test email prediction
        test_predict_email()
        
        # Test URL prediction
        test_predict_url()
        
        # Test comprehensive analysis
        test_analyze_email()
        
        print("\n" + "="*50)
        print("All tests completed!")
        print("="*50)
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
        print("Start it with: python app.py")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
