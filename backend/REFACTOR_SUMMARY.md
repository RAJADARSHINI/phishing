# Backend Refactoring Summary - Phishing Detection System

## Issues Fixed

### 1. ❌ NLP Score Calculation (CRITICAL FIX)
**Problem:**
- Used `max(scores)` approach where rule-based detections (urgency: 85, fear: 90, etc.) replaced the ML model score
- If text had "urgent" keyword, score jumped to 85 regardless of actual ML prediction
- NLP score of 96.34 was likely coming from a single rule match, not meaningful AI analysis

**Solution:**
- Changed to **additive model**: `base_score + rule_boost`
- ML model provides base score (0-100) from `predict_proba()`
- Rule detections add incremental risk:
  - Urgency: +15
  - Fear/Threats: +20
  - Authority: +10
  - Action requests: +10
- Final score clamped to 0-100 range

**File:** `backend/logic/nlp.py`

---

### 2. ❌ Unified Risk Score Overflow (CRITICAL FIX)
**Problem:**
- Backend was dividing all scores by 100 (converting 0-100 to 0-1)
- Comment claimed "Frontend expects scores in 0-1 decimal range" which was INCORRECT
- This caused values over 100% in the frontend or incorrect display

**Solution:**
- Removed division by 100
- All scores now returned in **0-100 range**
- Formula correctly applied: `(NLP * 0.5) + (URL * 0.3) + (Vision * 0.2)`
- Result is clamped to 0-100

**File:** `backend/logic/risk_engine.py`

---

### 3. ❌ Missing Verdict Logic
**Problem:**
- API response didn't include `verdict` field
- Frontend expected: "Safe" | "Suspicious" | "High Risk"

**Solution:**
- Added verdict calculation based on unified risk:
  - Safe: < 40
  - Suspicious: 40-69
  - High Risk: ≥ 70

**File:** `backend/logic/risk_engine.py`

---

### 4. ❌ API Response Format Mismatch
**Problem:**
- Backend returned `risk_score` but frontend expected `unified_risk`
- Missing `verdict` in response model

**Solution:**
- Updated `PhishingAnalysisResponse` model
- Changed `risk_score` → `unified_risk`
- Added `verdict: str` field

**File:** `backend/app.py`

---

## How NLP Analysis Now Works

### Step 1: ML Model Base Score
```python
# Vectorize email text
features = vectorizer.transform([text])

# Get phishing probability (0-1) from pretrained model
nlp_prob = model.predict_proba(features)[0][1]

# Convert to 0-100 scale
base_score = nlp_prob * 100
```

### Step 2: Rule-Based Signals (Explainable AI)
If psychological manipulation patterns detected:
- **Urgency** ("urgent", "immediately", "act now") → +15
- **Fear/Threats** ("suspended", "blocked", "legal action") → +20
- **Authority** ("admin", "bank", "IRS") → +10
- **Action** ("click here", "verify", "confirm") → +10

### Step 3: Final NLP Score
```python
final_score = base_score + rule_boost
final_score = clamp(final_score, 0, 100)
```

### Example Calculation:
**Input:** "We noticed unusual login attempts on your account. Please verify immediately."

1. **ML Model:** Detects suspicious patterns → 45% probability → `base_score = 45`
2. **Rule Detection:**
   - Fear/Threat ("unusual") → +20
   - Action ("verify") → +10
   - Urgency ("immediately") → +15
   - `rule_boost = 45`
3. **Final NLP Score:** 45 + 45 = **90** ✅

---

## Unified Risk Score Formula

```
Unified Risk = (NLP × 0.5) + (URL × 0.3) + (Vision × 0.2)
```

### Example:
- NLP Score: 90
- URL Score: 75 (suspicious domain detected)
- Vision Score: 0 (no image)

```
Unified Risk = (90 × 0.5) + (75 × 0.3) + (0 × 0.2)
             = 45 + 22.5 + 0
             = 67.5
```

**Verdict:** Suspicious (40 ≤ 67.5 < 70)

---

## API Response Format (Final)

```json
{
  "unified_risk": 67.5,
  "nlp_score": 90.0,
  "url_score": 75.0,
  "vision_score": 0.0,
  "verdict": "Suspicious",
  "explainability": {
    "factors": [
      "Fear/Threat language detected (account suspended/legal)",
      "High-risk action request detected (click/verify)",
      "Urgency language detected (pressure to act)",
      "Suspicious sensitive keywords in URL: verify, account"
    ],
    "warnings": [
      "Fear/Threat language detected (account suspended/legal)",
      "High-risk action request detected (click/verify)",
      "Urgency language detected (pressure to act)"
    ]
  },
  "explainable_reasons": [...]
}
```

---

## Testing Expectations

### Test Case 1: Legitimate Email
**Input:** "Your order has been shipped. Track it here: https://amazon.com/track"

**Expected:**
- NLP Score: 5-15 (low base score, no rule triggers)
- URL Score: 0 (amazon.com is trusted)
- Unified Risk: 2-7
- Verdict: Safe

### Test Case 2: Phishing Email
**Input:** "Your account has been suspended due to unusual activity. Click here to verify: http://paypal-secure.tk/login"

**Expected:**
- NLP Score: 75-95 (high base + fear + urgency + action)
- URL Score: 80+ (suspicious TLD .tk, brand mismatch)
- Unified Risk: 75-90
- Verdict: High Risk

### Test Case 3: Moderate Threat
**Input:** "Limited time offer! Act now to claim your prize."

**Expected:**
- NLP Score: 25-40 (moderate base + urgency)
- URL Score: 0
- Unified Risk: 12-20
- Verdict: Safe

---

## Files Modified

1. ✅ `backend/logic/nlp.py` - Fixed score calculation
2. ✅ `backend/logic/risk_engine.py` - Fixed unified risk formula and added verdict
3. ✅ `backend/app.py` - Updated API response format

## No Changes Made To:
- ✅ Frontend UI
- ✅ Frontend routes
- ✅ Request payloads
- ✅ URL analyzer
- ✅ Vision analyzer
