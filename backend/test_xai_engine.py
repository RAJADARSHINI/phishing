import requests
import json

BASE_URL = "http://localhost:8000"

def test_explainable_ai():
    print("\n" + "="*60)
    print("TESTING EXPLAINABLE AI THREAT ANALYSIS ENGINE")
    print("="*60)
    
    # Test case: Phishing email with urgency, fear, authority, and malicious URL
    payload = {
        "text": "Dear account holder, we noticed unusual activity on your security department account. Your access will be suspended immediately unless you verify your identity within 24 hours. Click here to secure your account: http://192.168.1.50/login",
        "urls": ["http://192.168.1.50/login"],
        "images_b64": []
    }
    
    print(f"\nScanning Input...")
    
    try:
        response = requests.post(f"{BASE_URL}/analyze", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("\nSUCCESS - ANALYSIS COMPLETE")
            print(f"Risk Level: {result['risk_level']}")
            print(f"Unified Risk Score: {result['risk_score']:.2f}")
            print(f"Verdict: {result['verdict']}")
            print(f"\nSummary: {result['analysis_summary']}")
            
            print("\nINDICATOR DETAILS:")
            print("-" * 30)
            for item in result['explainable_ai']:
                print(f"Indicator: {item['indicator']}")
                print(f"Evidence:  {item['evidence']}")
                print(f"Reason:    {item['reason']}")
                print(f"Weight:    {item['weight']}")
                print("-" * 30)
                
            # Internal consistency check
            nlp_score = result['nlp_score']
            url_score = result['url_score']
            expected_unified = (nlp_score * 0.6) + (url_score * 0.4)
            print(f"\nMath Validation:")
            print(f"  NLP ({nlp_score:.2f} * 0.6) + URL ({url_score:.2f} * 0.4) = {expected_unified:.2f}")
            if abs(result['risk_score'] - expected_unified) < 0.01:
                print("  [PASS] Unified Score Calculation is mathematically correct")
            else:
                print(f"  [FAIL] Unified Score Calculation Mismatch (Expected: {expected_unified}, Got: {result['risk_score']})")
                
        else:
            print(f"\n[ERROR] Status: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n[ERROR] API Connection Failed: {e}")

if __name__ == "__main__":
    test_explainable_ai()
