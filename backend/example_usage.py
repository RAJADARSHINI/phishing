"""
Simple example demonstrating how to use the Phishing Detection API

This script shows how to:
1. Make predictions for emails
2. Make predictions for URLs
3. Perform comprehensive analysis
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"


def example_email_prediction():
    """Example: Predict if an email is spam"""
    print("\n" + "="*60)
    print("Example 1: Email Spam Prediction")
    print("="*60)
    
    email_text = "You have won $1,000,000! Click here now to claim your prize!"
    
    response = requests.post(
        f"{BASE_URL}/predict-email",
        json={"text": email_text}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nEmail Text: {email_text}")
        print(f"\nResult:")
        print(f"  Prediction: {'SPAM' if result['prediction'] == 1 else 'NOT SPAM'}")
        print(f"  Probability: {result['probability']:.2%}")
        print(f"  Confidence: {result['confidence']:.2%}")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def example_url_prediction():
    """Example: Predict if a URL is phishing"""
    print("\n" + "="*60)
    print("Example 2: URL Phishing Prediction")
    print("="*60)
    
    test_urls = [
        "http://paypal-security-verify.com/login",
        "https://www.paypal.com/login",
        "http://bank-verify-now.com/secure"
    ]
    
    for url in test_urls:
        response = requests.post(
            f"{BASE_URL}/predict-url",
            json={"url": url}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nURL: {url}")
            print(f"  Prediction: {'PHISHING' if result['prediction'] == 1 else 'SAFE'}")
            print(f"  Probability: {result['probability']:.2%}")
            print(f"  Confidence: {result['confidence']:.2%}")
        else:
            print(f"Error: {response.status_code} - {response.text}")


def example_comprehensive_analysis():
    """Example: Comprehensive phishing analysis"""
    print("\n" + "="*60)
    print("Example 3: Comprehensive Analysis")
    print("="*60)
    
    # Example suspicious email
    email_data = {
        "text": "URGENT: Your account will be suspended. Verify immediately at http://verify-account-now.com",
        "urls": ["http://verify-account-now.com"],
        "images_b64": []
    }
    
    response = requests.post(
        f"{BASE_URL}/analyze_email",
        json=email_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nEmail Text: {email_data['text']}")
        print(f"\nAnalysis Results:")
        print(f"  Overall Risk Score: {result['risk_score']:.2%}")
        print(f"  NLP Score (email text): {result['nlp_score']:.2%}")
        print(f"  URL Score: {result['url_score']:.2%}")
        print(f"  Vision Score: {result['vision_score']:.2%}")
        print(f"\n  Explainability Factors:")
        for factor in result['explainability']['factors']:
            print(f"    - {factor}")
        if result['explainability']['warnings']:
            print(f"\n  Warnings:")
            for warning in result['explainability']['warnings']:
                print(f"    ⚠ {warning}")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✓ API is running")
            return True
        else:
            print(f"✗ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Make sure the server is running on http://localhost:8000")
        print("  Start it with: python app.py")
        return False


def main():
    """Run all examples"""
    print("="*60)
    print("Phishing Detection API - Usage Examples")
    print("="*60)
    
    # Check if API is running
    if not check_api_health():
        return
    
    # Run examples
    example_email_prediction()
    example_url_prediction()
    example_comprehensive_analysis()
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)


if __name__ == "__main__":
    main()
