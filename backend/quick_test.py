"""Quick test to see what's happening"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logic import RiskEngine

engine = RiskEngine()

# Safe email
safe_text = """
Hi team,

Just a reminder that we have our weekly standup meeting tomorrow at 10am 
in Conference Room B. Please bring your status updates.

Looking forward to seeing everyone!

Best regards,
Sarah
"""

result = engine.analyze(safe_text, [], [])

print(f"\nSAFE EMAIL TEST:")
print(f"NLP Score: {result['nlp_score']:.1f}/100")
print(f"URL Score: {result['url_score']:.1f}/100")
print(f"Unified Risk: {result['risk_score']:.1f}/100")
print(f"Verdict: {result['verdict']}")
print(f"\nFactors detected:")
for f in result['factors']:
    print(f"  - {f}")
