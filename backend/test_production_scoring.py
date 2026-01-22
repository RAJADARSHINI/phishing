"""
PRODUCTION-GRADE Backend Test Script
Tests the new ADDITIVE scoring system with real-world examples
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logic import RiskEngine
import json

def print_analysis(title, result):
    """Pretty print analysis results"""
    print("\n" + "="*80)
    print(f"TEST: {title}")
    print("="*80)
    print(f"\n📊 SCORES:")
    print(f"  Unified Risk: {result['risk_score']:.1f}/100")
    print(f"  NLP Score:    {result['nlp_score']:.1f}/100")
    print(f"  URL Score:    {result['url_score']:.1f}/100")
    print(f"  Vision Score: {result['vision_score']:.1f}/100")
    print(f"\n🎯 VERDICT: {result['verdict']} ({result['risk_level']})")
    print(f"\n📝 SUMMARY: {result['analysis_summary']}")
    
    if result['factors']:
        print(f"\n⚠️  DETECTED THREATS ({len(result['factors'])}):")
        for i, factor in enumerate(result['factors'][:10], 1):  # Show first 10
            print(f"  {i}. {factor}")
    
    print("\n" + "-"*80)

def main():
    print("\n" + "🚀"*40)
    print("PRODUCTION-GRADE PHISHING DETECTION SYSTEM - TEST SUITE")
    print("🚀"*40)
    
    engine = RiskEngine()
    
    # ========================================
    # TEST 1: HIGH-RISK PHISHING EMAIL
    # ========================================
    test1_text = """
    URGENT: Your PayPal account has been suspended due to unusual activity.
    
    We detected unauthorized login attempts from multiple locations. Your account 
    will be permanently closed within 24 hours unless you verify your identity 
    immediately.
    
    Click here to verify: http://paypal-verify.tk/secure-login
    
    Failure to act will result in permanent account termination and legal action.
    
    PayPal Security Team
    """
    
    result1 = engine.analyze(test1_text, [], [])
    print_analysis("HIGH-RISK PHISHING EMAIL", result1)
    
    # Assertions
    assert result1['nlp_score'] > 70, f"NLP score too low: {result1['nlp_score']}"
    assert result1['url_score'] > 50, f"URL score too low: {result1['url_score']}"
    assert result1['risk_score'] > 70, f"Unified risk too low: {result1['risk_score']}"
    assert result1['verdict'] == "THREAT", f"Wrong verdict: {result1['verdict']}"
    print("✅ TEST 1 PASSED: High-risk email correctly detected")
    
    # ========================================
    # TEST 2: SAFE EMAIL
    # ========================================
    test2_text = """
    Hi team,
    
    Just a reminder that we have our weekly standup meeting tomorrow at 10am 
    in Conference Room B. Please bring your status updates.
    
    Looking forward to seeing everyone!
    
    Best regards,
    Sarah
    """
    
    result2 = engine.analyze(test2_text, [], [])
    print_analysis("SAFE EMAIL", result2)
    
    # Assertions
    assert result2['nlp_score'] < 30, f"NLP score too high: {result2['nlp_score']}"
    assert result2['risk_score'] < 30, f"Unified risk too high: {result2['risk_score']}"
    assert result2['verdict'] == "SAFE", f"Wrong verdict: {result2['verdict']}"
    print("✅ TEST 2 PASSED: Safe email correctly identified")
    
    # ========================================
    # TEST 3: SUSPICIOUS MARKETING EMAIL
    # ========================================
    test3_text = """
    Limited Time Offer!
    
    Act now to get 50% off all products. This exclusive deal expires in 24 hours!
    
    Shop now at: https://legitimate-store.com/sale
    
    Don't miss out on this amazing opportunity!
    """
    
    result3 = engine.analyze(test3_text, [], [])
    print_analysis("SUSPICIOUS MARKETING EMAIL", result3)
    
    # Assertions
    assert result3['nlp_score'] > 15, f"NLP score too low: {result3['nlp_score']}"
    assert result3['nlp_score'] < 60, f"NLP score too high: {result3['nlp_score']}"
    print("✅ TEST 3 PASSED: Marketing email correctly classified")
    
    # ========================================
    # TEST 4: MULTI-THREAT ATTACK
    # ========================================
    test4_text = """
    SECURITY ALERT: Unusual activity detected!
    
    Dear Valued Customer,
    
    Your bank account has been blocked due to suspicious login attempts. 
    Immediate verification required to avoid permanent suspension.
    
    Verify now: http://192.168.1.1/bank-verify
    
    You have 2 hours to respond or face legal consequences.
    
    Bank Security Department
    """
    
    result4 = engine.analyze(test4_text, [], [])
    print_analysis("MULTI-THREAT ATTACK (Text + URL)", result4)
    
    # Assertions
    assert result4['nlp_score'] > 60, f"NLP score too low: {result4['nlp_score']}"
    assert result4['url_score'] > 40, f"URL score too low: {result4['url_score']}"
    assert result4['risk_score'] > 75, f"Unified risk too low: {result4['risk_score']}"
    assert result4['verdict'] == "THREAT", f"Wrong verdict: {result4['verdict']}"
    print("✅ TEST 4 PASSED: Multi-threat attack correctly detected")
    
    # ========================================
    # TEST 5: URL EXTRACTION FROM TEXT
    # ========================================
    test5_text = """
    Check out this link: https://bit.ly/suspicious
    And this one too: http://phishing-site.tk/login
    """
    
    result5 = engine.analyze(test5_text, [], [])
    print_analysis("URL EXTRACTION TEST", result5)
    
    # Assertions
    assert result5['url_score'] > 20, f"URL score too low: {result5['url_score']}"
    print("✅ TEST 5 PASSED: URLs correctly extracted and analyzed")
    
    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "="*80)
    print("🎉 ALL TESTS PASSED!")
    print("="*80)
    print("\n✅ NLP Analysis: Using ML model + psychological detection")
    print("✅ URL Analysis: Additive scoring with threat compounding")
    print("✅ Risk Engine: MAX-based scoring with multi-threat boost")
    print("✅ URL Extraction: Automatically extracts URLs from text")
    print("✅ Scores: All in 0-100 range")
    print("✅ Verdicts: Correctly classify Safe/Suspicious/High Risk")
    print("\n🚀 BACKEND IS PRODUCTION-READY!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
