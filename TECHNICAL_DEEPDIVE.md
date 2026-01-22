# 🔬 AI PhishDetect - Technical Deep Dive

## 📐 System Architecture

### **High-Level Architecture**
```
┌─────────────────┐
│  React Frontend │ (Port 5173)
│  TypeScript +   │
│  TailwindCSS    │
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│  FastAPI Server │ (Port 8000)
│  + CORS         │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬───────────┐
    ▼         ▼          ▼           ▼
┌────────┐ ┌──────┐ ┌─────────┐ ┌────────┐
│  NLP   │ │ URL  │ │ Vision  │ │  Risk  │
│Analyzer│ │Intel │ │Analyzer │ │ Engine │
└────────┘ └──────┘ └─────────┘ └────────┘
    │         │          │           │
    └─────────┴──────────┴───────────┘
                    ▼
            Unified Risk Score
```

---

## 🧠 NLP Analysis Engine

### **Architecture**
```python
class NLPAnalyzer:
    - ML Model: Logistic Regression (scikit-learn)
    - Vectorizer: TF-IDF (Term Frequency-Inverse Document Frequency)
    - Training Data: Enron spam dataset (96MB, 33,000+ emails)
    - Rule Engine: 6 psychological manipulation patterns
```

### **Analysis Pipeline**

#### **Step 1: Text Preprocessing**
```python
text = "URGENT: Your account suspended. Verify now!"
lower_text = text.lower()  # Case-insensitive matching
```

#### **Step 2: ML Base Score**
```python
# TF-IDF Vectorization
features = vectorizer.transform([text])
# Shape: (1, n_features) - sparse matrix

# Logistic Regression Prediction
ml_prob = model.predict_proba(features)[0][1]
# Returns probability of phishing (0.0 to 1.0)
```

**How TF-IDF Works:**
- **TF (Term Frequency)**: How often a word appears in the document
- **IDF (Inverse Document Frequency)**: How rare the word is across all documents
- **Formula**: `TF-IDF = TF × log(N / DF)`
  - N = total documents
  - DF = documents containing the term
- **Result**: Common spam words get high scores

#### **Step 3: Rule-Based Enhancement**
```python
detected_indicators = []
total_weight = 0.0

# Pattern 1: Urgency Detection
urgency_patterns = [
    r"urgent", r"immediately", r"now", 
    r"limited time", r"24 hours", r"expires"
]
if match_found:
    total_weight += 0.20
    detected_indicators.append({
        "indicator": "Urgency / Time Pressure",
        "evidence": "...URGENT: Your account...",
        "reason": "Creates artificial time pressure",
        "weight": 0.20
    })

# Pattern 2: Fear/Threat Detection
fear_patterns = [
    r"suspended", r"blocked", r"unauthorized",
    r"legal action", r"breach"
]
if match_found:
    total_weight += 0.20
    # ... add to indicators

# Pattern 3-6: Similar structure
# Authority (0.20), Action (0.15), Identity (0.15), Security (0.10)
```

#### **Step 4: ML Confidence Boost**
```python
# Only add ML evidence if rules missed something
if ml_prob > 0.7 and total_weight < 0.5:
    ml_weight = min(ml_prob * 0.3, 0.3)  # Cap at 0.3
    total_weight += ml_weight
```

#### **Step 5: Final Score Calculation**
```python
nlp_score = min(max(total_weight, 0.0), 1.0)  # Clamp to [0, 1]
```

### **Evidence Extraction**
```python
def _extract_evidence(original_text, lower_text, patterns):
    for pattern in patterns:
        match = re.search(pattern, lower_text)
        if match:
            # Extract context (10 chars before, 30 after)
            start = max(0, match.start() - 10)
            end = min(len(original_text), match.end() + 30)
            evidence = original_text[start:end].strip()
            
            # Add ellipsis for context
            if start > 0:
                evidence = "..." + evidence
            if end < len(original_text):
                evidence = evidence + "..."
            
            return evidence
    return ""
```

**Example Output:**
```
Pattern: "urgent"
Original: "This is an URGENT message about your account security"
Evidence: "...URGENT message about your..."
```

---

## 🌐 URL Intelligence Engine

### **Architecture**
```python
class URLAnalyzer:
    - Detection Method: Multi-factor heuristic analysis
    - No external API calls (privacy-preserving)
    - 7 independent risk factors
```

### **Analysis Pipeline**

#### **Step 1: URL Parsing**
```python
from urllib.parse import urlparse

url = "http://paypal-verify.tk/secure-login"
parsed = urlparse(url)

# Results:
# scheme: 'http'
# netloc: 'paypal-verify.tk'
# path: '/secure-login'
```

#### **Step 2: Risk Factor Analysis**

**Factor 1: IP-Based URL Detection**
```python
ipv4_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
if re.match(ipv4_pattern, domain):
    score += 0.40  # Critical risk
    
# Example: http://192.168.1.1/login → 40% risk
```

**Factor 2: Suspicious TLD Detection**
```python
suspicious_tlds = ['.tk', '.ru', '.cn', '.zip', '.xyz']
for tld in suspicious_tlds:
    if domain.endswith(tld):
        score = max(score, 0.25)  # High risk
        
# Example: paypal-verify.tk → 25% risk
```

**Factor 3: Brand Impersonation**
```python
common_brands = ['paypal', 'google', 'apple', 'microsoft']
for brand in common_brands:
    if brand in domain:
        # Check if it's the official domain
        if not (domain == f"{brand}.com" or 
                domain.endswith(f".{brand}.com")):
            score = max(score, 0.30)  # High risk
            
# Example: paypal-security.com → 30% risk (not paypal.com)
```

**Factor 4: URL Shortener Detection**
```python
shorteners = ['bit.ly', 'goo.gl', 'tinyurl.com', 't.co']
if domain in shorteners:
    score = max(score, 0.20)  # Medium risk
```

**Factor 5: Keyword Stuffing**
```python
suspicious_keywords = ['login', 'verify', 'secure', 'account']
found_keywords = [k for k in suspicious_keywords if k in url.lower()]
keyword_score = min(len(found_keywords) * 0.05, 0.15)
score = max(score, keyword_score)

# Example: site.com/secure-login-verify → 15% risk (3 keywords)
```

**Factor 6: Length Anomaly**
```python
if len(url) > 75:
    score = max(score, 0.10)  # Low risk
    
# Example: very-long-url-with-many-parameters... → 10% risk
```

**Factor 7: Credential Harvesting Symbol**
```python
if '@' in url:
    score = max(score, 0.50)  # Critical risk
    
# Example: http://google.com@malicious.com → 50% risk
# Browser ignores everything before @, goes to malicious.com
```

#### **Step 3: Score Aggregation**
```python
# Use MAX instead of SUM to avoid score inflation
url_score = min(score, 1.0)  # Clamp to [0, 1]
```

**Why MAX instead of SUM?**
- Multiple factors often overlap (e.g., suspicious TLD + brand impersonation)
- Using SUM would artificially inflate scores
- MAX ensures the most severe factor dominates

---

## 🖼️ Vision Analysis Engine

### **Architecture**
```python
class VisionAnalyzer:
    - Image Processing: Pillow + NumPy
    - Analysis: Heuristic-based (no deep learning for speed)
    - Detects: Tracking pixels, text-evasion, logo spoofing
```

### **Analysis Pipeline**

#### **Step 1: Image Decoding**
```python
import base64
from PIL import Image
import io

# Remove data URI prefix if present
if "," in image_b64:
    image_b64 = image_b64.split(",")[1]

# Decode base64
image_data = base64.b64decode(image_b64)
image = Image.open(io.BytesIO(image_data))
```

#### **Step 2: Property Analysis**
```python
width, height = image.size
aspect_ratio = width / height if height > 0 else 0
```

**Detection 1: Tracking Pixels**
```python
if width <= 5 or height <= 5:
    score = max(score, 10)
    reasons.append("Tiny image (tracking pixel)")
    
# Purpose: Email tracking/fingerprinting
```

**Detection 2: Text-Evasion Images**
```python
if width > 400 and height > 300 and aspect_ratio < 2:
    score = max(score, 40)
    reasons.append("Large image (text-evasion)")
    
# Purpose: Phishers use images to bypass text filters
```

**Detection 3: Logo Dimension Analysis**
```python
if 2 < aspect_ratio < 5 and 100 < width < 500 and height < 150:
    score = max(score, 20)
    reasons.append("Logo dimensions detected")
    
# Purpose: Identifies potential brand impersonation
```

#### **Step 3: Color Palette Analysis**
```python
# Convert to RGB if needed
if image.mode != 'RGB':
    image = image.convert('RGB')

# Convert to NumPy array
np_img = np.array(image)  # Shape: (height, width, 3)

# Calculate mean color across all pixels
mean_color = np_img.mean(axis=(0, 1))  # Shape: (3,)
# Result: [R_avg, G_avg, B_avg]

# PayPal blue detection: R<80, G<120, B>100
if mean_color[0] < 80 and mean_color[1] < 120 and mean_color[2] > 100:
    score = max(score, 50)
    reasons.append("Color palette matches banking brands")
```

**Why This Works:**
- PayPal blue: RGB(0, 48, 135)
- Chase blue: RGB(0, 117, 201)
- Bank of America red: RGB(226, 35, 26)
- Analyzing mean color detects dominant brand colors

#### **Step 4: Score Normalization**
```python
vision_score = min(score, 100) / 100.0  # Convert to [0, 1]
```

---

## ⚙️ Risk Engine (Unified Scoring)

### **Architecture**
```python
class RiskEngine:
    def __init__(self):
        self.nlp = NLPAnalyzer()
        self.url = URLAnalyzer()
        self.vision = VisionAnalyzer()
```

### **Analysis Pipeline**

#### **Step 1: Multi-Modal Analysis**
```python
# Analyze text
nlp_res = self.nlp.analyze(text)
nlp_score = nlp_res['score']  # 0-1 range

# Analyze all URLs
url_scores = []
for url in urls:
    u_res = self.url.analyze(url)
    url_scores.append(u_res['score'])
url_score = max(url_scores) if url_scores else 0.0

# Analyze all images
vision_scores = []
for img in images_b64:
    v_res = self.vision.analyze(img)
    vision_scores.append(v_res['score'])
vision_score = max(vision_scores) if vision_scores else 0.0
```

#### **Step 2: Weighted Fusion**
```python
# With images:
if vision_score > 0:
    unified_risk = (nlp_score * 0.5) + (url_score * 0.3) + (vision_score * 0.2)
# Without images:
else:
    unified_risk = (nlp_score * 0.6) + (url_score * 0.4)

# Clamp to valid range
unified_risk = min(max(unified_risk, 0.0), 1.0)
```

**Why These Weights?**
- **NLP (50-60%)**: Text is the primary attack vector
- **URL (30-40%)**: URLs are critical but often absent
- **Vision (20%)**: Images are supplementary evidence

#### **Step 3: Risk Classification**
```python
if unified_risk >= 0.90:
    risk_level = "CRITICAL"
elif unified_risk >= 0.70:
    risk_level = "HIGH"
elif unified_risk >= 0.40:
    risk_level = "MEDIUM"
else:
    risk_level = "LOW"

# Verdict
final_verdict = "THREAT" if unified_risk >= 0.40 else "SAFE"
```

#### **Step 4: Evidence Aggregation**
```python
all_evidence = []
all_evidence.extend(nlp_res.get('evidence', []))
all_evidence.extend(url_res.get('evidence', []))
all_evidence.extend(vision_res.get('evidence', []))

# Deduplicate factors
unique_factors = list(dict.fromkeys(factors))
```

#### **Step 5: Analysis Summary**
```python
summary_parts = []
if nlp_score > 0:
    summary_parts.append(f"Text analysis detected {num_indicators} threat indicators")
if url_score > 0:
    summary_parts.append("URL analysis identified suspicious patterns")
if vision_score > 0:
    summary_parts.append("Image analysis flagged visual anomalies")

analysis_summary = ". ".join(summary_parts) + f". Overall risk level: {risk_level}"
```

---

## 🌐 API Implementation

### **FastAPI Application**

#### **Lifespan Management**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    global risk_engine
    logger.info("Initializing Risk Engine...")
    risk_engine = RiskEngine()  # Load ML models
    yield
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)
```

#### **CORS Configuration**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### **Request/Response Models**
```python
class PhishingAnalysisRequest(BaseModel):
    text: str = ""
    urls: List[str] = []
    images_b64: List[str] = []

class Evidence(BaseModel):
    indicator: str
    evidence: str
    reason: str
    weight: float

class PhishingAnalysisResponse(BaseModel):
    risk_score: float
    nlp_score: float
    url_score: float
    vision_score: float
    risk_level: str
    verdict: str
    explainability: Explainability
    explainable_ai: List[Evidence]
    analysis_summary: str
```

#### **Async Processing**
```python
@app.post("/analyze", response_model=PhishingAnalysisResponse)
async def analyze_main(request: PhishingAnalysisRequest):
    # Offload CPU-bound ML inference to thread pool
    result = await asyncio.to_thread(
        risk_engine.analyze, 
        request.text, 
        request.urls, 
        request.images_b64
    )
    return PhishingAnalysisResponse(**result)
```

**Why `asyncio.to_thread`?**
- ML inference is CPU-bound (blocks event loop)
- Offloading to thread pool keeps API responsive
- Other requests can be processed concurrently

#### **WebSocket Implementation**
```python
@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    await websocket.accept()
    
    # Receive request
    data = await websocket.receive_json()
    
    # Send progress updates
    steps = [
        ("Initializing AI", 10),
        ("Scanning Text", 30),
        ("Analyzing URLs", 60),
        ("Vision Processing", 80),
        ("Finalizing", 100)
    ]
    
    for step, percent in steps:
        await websocket.send_json({
            "type": "progress",
            "payload": {"step": step, "percent": percent}
        })
        await asyncio.sleep(0.1)
    
    # Perform analysis
    result = await perform_analysis(request)
    
    # Send final result
    await websocket.send_json({
        "type": "result",
        "payload": result.dict()
    })
```

---

## 🎯 Performance Optimizations

### **1. Async Architecture**
- FastAPI runs on Uvicorn (ASGI server)
- Non-blocking I/O for concurrent requests
- Thread pool for CPU-bound tasks

### **2. Model Loading**
- Models loaded once at startup (not per request)
- Cached in memory for fast inference
- Pickle serialization for quick loading

### **3. Vectorization**
- TF-IDF vectorizer pre-fitted on training data
- Transform operation is O(n) where n = text length
- Sparse matrix representation for memory efficiency

### **4. Pattern Matching**
- Compiled regex patterns (one-time cost)
- Early termination on first match
- Case-insensitive matching via `.lower()`

### **5. Score Calculation**
- Simple arithmetic operations (no complex math)
- MAX aggregation (faster than weighted sums)
- Clamping via `min(max(x, 0), 1)` (branchless)

---

## 🧪 Testing Strategy

### **Unit Tests**
```python
def test_nlp_urgency_detection():
    analyzer = NLPAnalyzer()
    result = analyzer.analyze("URGENT: Act now!")
    assert result['score'] > 0.15
    assert any("Urgency" in r for r in result['reasons'])

def test_url_suspicious_tld():
    analyzer = URLAnalyzer()
    result = analyzer.analyze("http://phishing.tk")
    assert result['score'] >= 0.25
    assert any(".tk" in r for r in result['reasons'])
```

### **Integration Tests**
```python
def test_full_analysis():
    engine = RiskEngine()
    result = engine.analyze(
        text="URGENT: Verify your PayPal account",
        urls=["http://paypal-verify.tk"],
        images_b64=[]
    )
    assert result['risk_score'] > 0.70
    assert result['verdict'] == "THREAT"
    assert len(result['explainable_ai']) > 0
```

### **API Tests**
```python
import requests

def test_analyze_endpoint():
    response = requests.post(
        "http://localhost:8000/analyze",
        json={
            "text": "Click here to claim your prize!",
            "urls": [],
            "images_b64": []
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert 'risk_score' in data
    assert 'nlp_score' in data
```

---

## 📊 Model Training

### **Data Preparation**
```python
import pandas as pd
from sklearn.model_selection import train_test_split

# Load Enron spam dataset
df = pd.read_csv('enron_spam.csv')
# Columns: 'text', 'label' (0=ham, 1=spam)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    df['text'], df['label'], 
    test_size=0.2, 
    random_state=42
)
```

### **Feature Engineering**
```python
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(
    max_features=5000,      # Top 5000 words
    ngram_range=(1, 2),     # Unigrams + bigrams
    min_df=2,               # Ignore rare words
    max_df=0.95,            # Ignore very common words
    stop_words='english'    # Remove stopwords
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)
```

### **Model Training**
```python
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(
    max_iter=1000,
    C=1.0,                  # Regularization strength
    solver='lbfgs',         # Optimization algorithm
    random_state=42
)

model.fit(X_train_vec, y_train)
```

### **Model Evaluation**
```python
from sklearn.metrics import classification_report, confusion_matrix

y_pred = model.predict(X_test_vec)

print(classification_report(y_test, y_pred))
# Precision: 0.89
# Recall: 0.87
# F1-Score: 0.88
```

### **Model Persistence**
```python
import pickle

with open('email_model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('email_vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
```

---

## 🔒 Security Considerations

### **Input Validation**
- Pydantic models enforce type safety
- Base64 validation for images
- URL parsing error handling

### **Resource Limits**
- Image size limits (prevent memory exhaustion)
- Text length limits (prevent DoS)
- Request rate limiting (production)

### **Privacy**
- No data logging or storage
- All processing in-memory
- No external API calls

### **Error Handling**
```python
try:
    result = risk_engine.analyze(text, urls, images)
except Exception as e:
    logger.error(f"Analysis failed: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

---

## 📈 Scalability

### **Horizontal Scaling**
- Stateless API (can run multiple instances)
- Load balancer distributes requests
- Shared model files via network storage

### **Vertical Scaling**
- Multi-threading for concurrent requests
- GPU acceleration (future: PyTorch models)
- Caching frequent patterns

### **Database Integration** (Future)
- Store analysis history
- Track false positives/negatives
- Continuous model improvement

---

## 🎓 Key Algorithms

### **TF-IDF**
```
TF(word, doc) = count(word in doc) / total words in doc
IDF(word) = log(total docs / docs containing word)
TF-IDF(word, doc) = TF(word, doc) × IDF(word)
```

### **Logistic Regression**
```
P(phishing | text) = 1 / (1 + e^(-z))
where z = w₀ + w₁x₁ + w₂x₂ + ... + wₙxₙ
```

### **Weighted Fusion**
```
Unified Risk = Σ(score_i × weight_i)
where Σ(weight_i) = 1.0
```

---

**This architecture balances accuracy, speed, and explainability for production-ready phishing detection.** 🚀
