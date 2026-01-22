"""
Quick manual test for the refactored backend
Tests the new unified_risk and verdict fields
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_phishing_email():
    """Test a clear phishing attempt"""
    print("\n" + "="*60)
    print("TEST 1: Clear Phishing Email")
    print("="*60)
    
    payload = {
        "text": "URGENT: We noticed unusual login attempts on your account. Your account will be suspended unless you verify immediately by clicking here: http://paypal-secure.tk/verify",
        "urls": ["http://paypal-secure.tk/verify"],
        "images_b64": []
    }
    
    print(f"\nInput: {payload['text'][:80]}...")
    print(f"URLs: {payload['urls']}")
    
    try:
        response = requests.post(f"{BASE_URL}/analyze", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS - Response:")
            print(f"  Unified Risk: {result['unified_risk']:.2f}%")
            print(f"  NLP Score: {result['nlp_score']:.2f}%")
            print(f"  URL Score: {result['url_score']:.2f}%")
            print(f"  Vision Score: {result['vision_score']:.2f}%")
            print(f"  Verdict: {result['verdict']}")
            print(f"\n  Explanations:")
            for reason in result['explainable_reasons']:
                print(f"    - {reason}")
            
            # Validate expectations
            print("\n  Validation:")
            if result['unified_risk'] > 70:
                print("    ✅ Unified risk is HIGH (>70)")
            else:
                print(f"    ⚠️  Expected unified_risk > 70, got {result['unified_risk']:.2f}")
            
            if result['verdict'] == "High Risk":
                print("    ✅ Verdict is 'High Risk'")
            else:
                print(f"    ⚠️  Expected 'High Risk', got '{result['verdict']}'")
                
            if result['unified_risk'] <= 100:
                print("    ✅ Unified risk is ≤ 100 (valid)")
            else:
                print(f"    ❌ INVALID: unified_risk > 100 ({result['unified_risk']:.2f})")
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend")
        print("Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


def test_safe_email():
    """Test a legitimate email"""
    print("\n" + "="*60)
    print("TEST 2: Safe/Legitimate Email")
    print("="*60)
    
    payload = {
        "text": "Hi team, just a reminder that our weekly standup is scheduled for tomorrow at 10am. Looking forward to seeing everyone there!",
        "urls": [],
        "images_b64": []
    }
    
    print(f"\nInput: {payload['text']}")
    
    try:
        response = requests.post(f"{BASE_URL}/analyze", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS - Response:")
            print(f"  Unified Risk: {result['unified_risk']:.2f}%")
            print(f"  NLP Score: {result['nlp_score']:.2f}%")
            print(f"  URL Score: {result['url_score']:.2f}%")
            print(f"  Vision Score: {result['vision_score']:.2f}%")
            print(f"  Verdict: {result['verdict']}")
            
            if result['explainable_reasons']:
                print(f"\n  Explanations:")
                for reason in result['explainable_reasons']:
                    print(f"    - {reason}")
            else:
                print("\n  No threats detected")
            
            # Validate expectations
            print("\n  Validation:")
            if result['unified_risk'] < 40:
                print("    ✅ Unified risk is LOW (<40)")
            else:
                print(f"    ⚠️  Expected unified_risk < 40, got {result['unified_risk']:.2f}")
            
            if result['verdict'] == "Safe":
                print("    ✅ Verdict is 'Safe'")
            else:
                print(f"    ⚠️  Expected 'Safe', got '{result['verdict']}'")
                
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


def test_suspicious_email():
    """Test a moderately suspicious email"""
    print("\n" + "="*60)
    print("TEST 3: Suspicious Email")
    print("="*60)
    
    payload = {
        "text": "Limited time offer! Act now to claim your exclusive discount. Click here before it expires!",
        "urls": [],
        "images_b64": []
    }
    
    print(f"\nInput: {payload['text']}")
    
    try:
        response = requests.post(f"{BASE_URL}/analyze", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS - Response:")
            print(f"  Unified Risk: {result['unified_risk']:.2f}%")
            print(f"  NLP Score: {result['nlp_score']:.2f}%")
            print(f"  URL Score: {result['url_score']:.2f}%")
            print(f"  Vision Score: {result['vision_score']:.2f}%")
            print(f"  Verdict: {result['verdict']}")
            
            if result['explainable_reasons']:
                print(f"\n  Explanations:")
                for reason in result['explainable_reasons']:
                    print(f"    - {reason}")
            
            # Validate expectations
            print("\n  Validation:")
            if 40 <= result['unified_risk'] < 70:
                print("    ✅ Unified risk is MODERATE (40-70)")
            else:
                print(f"    ℹ️  Got unified_risk = {result['unified_risk']:.2f}")
                
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    print("="*60)
    print("Backend Refactor Validation Tests")
    print("="*60)
    print("\nTesting the new backend with:")
    print("  - Correct NLP scoring (ML model + rule boosts)")
    print("  - Correct unified risk calculation (0-100 range)")
    print("  - Verdict logic (Safe/Suspicious/High Risk)")
    print("\nMake sure backend is running on http://localhost:8000")
    
    test_phishing_email()
    test_safe_email()
    test_suspicious_email()
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)
