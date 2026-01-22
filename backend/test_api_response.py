import requests
import json

# Test the API
url = "http://localhost:8000/analyze"
data = {
    "text": "URGENT: Your account suspended. Verify now!",
    "urls": [],
    "images_b64": []
}

response = requests.post(url, json=data)
result = response.json()

print("\n" + "="*60)
print("API RESPONSE TEST")
print("="*60)
print(f"\nRisk Score: {result['risk_score']}")
print(f"NLP Score: {result['nlp_score']}")
print(f"URL Score: {result['url_score']}")
print(f"Vision Score: {result['vision_score']}")
print(f"Verdict: {result['verdict']}")
print(f"Risk Level: {result['risk_level']}")

print(f"\n✅ Scores are in 0-1 range: {0 <= result['risk_score'] <= 1}")
print(f"✅ Frontend will display as: {result['risk_score'] * 100:.2f}%")
print("="*60 + "\n")
