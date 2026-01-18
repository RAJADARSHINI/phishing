"""
FastAPI Backend for Phishing Detection

Provides REST API endpoints for:
- /predict-email: Predict if email text is spam
- /predict-url: Predict if URL is phishing
- /analyze_email: Comprehensive analysis endpoint (for frontend integration)
- WebSocket endpoint for progress updates
"""

import os
import pickle
import re
import numpy as np
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Phishing Detection API", version="1.0.0")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class EmailPredictionRequest(BaseModel):
    text: str

class URLPredictionRequest(BaseModel):
    url: str

class EmailPredictionResponse(BaseModel):
    prediction: int  # 0 = not spam, 1 = spam
    probability: float
    confidence: float

class URLPredictionResponse(BaseModel):
    prediction: int  # 0 = safe, 1 = phishing
    probability: float
    confidence: float

class PhishingAnalysisRequest(BaseModel):
    text: str
    urls: List[str]
    images_b64: List[str]

class Explainability(BaseModel):
    factors: List[str]
    warnings: List[str]

class PhishingAnalysisResponse(BaseModel):
    risk_score: float
    nlp_score: float
    url_score: float
    vision_score: float
    explainability: Explainability

class LiveProgress(BaseModel):
    step: str
    percent: Optional[float] = None
    partial_result: Optional[dict] = None


# Global variables for loaded models
email_model = None
email_vectorizer = None
url_model = None
url_vectorizer = None


def load_models():
    """
    Load trained models and vectorizers from disk
    """
    global email_model, email_vectorizer, url_model, url_vectorizer
    
    try:
        # Load email model
        with open('models/email_model.pkl', 'rb') as f:
            email_model = pickle.load(f)
        logger.info("Loaded email model")
        
        with open('models/email_vectorizer.pkl', 'rb') as f:
            email_vectorizer = pickle.load(f)
        logger.info("Loaded email vectorizer")
        
        # Load URL model
        with open('models/url_model.pkl', 'rb') as f:
            url_model = pickle.load(f)
        logger.info("Loaded URL model")
        
        with open('models/url_vectorizer.pkl', 'rb') as f:
            url_vectorizer = pickle.load(f)
        logger.info("Loaded URL vectorizer")
        
        logger.info("All models loaded successfully")
        return True
    except FileNotFoundError as e:
        logger.error(f"Model files not found: {e}")
        logger.error("Please run train_models.py first to train the models")
        return False
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        return False


def preprocess_email(text: str) -> str:
    """
    Preprocess email text (same as training)
    """
    if not text:
        return ""
    text = str(text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def preprocess_url(url: str) -> str:
    """
    Preprocess URL (same as training)
    """
    if not url:
        return ""
    url = str(url)
    url = re.sub(r'\s+', ' ', url)
    url = url.strip('"\'')
    return url.strip()


def predict_email_spam(text: str) -> tuple:
    """
    Predict if email is spam
    Returns: (prediction, probability, confidence)
    """
    if email_model is None or email_vectorizer is None:
        raise HTTPException(status_code=500, detail="Email model not loaded")
    
    # Preprocess
    cleaned_text = preprocess_email(text)
    
    # Transform to features
    features = email_vectorizer.transform([cleaned_text])
    
    # Predict
    prediction = email_model.predict(features)[0]
    probabilities = email_model.predict_proba(features)[0]
    probability = probabilities[1] if len(probabilities) > 1 else probabilities[0]
    
    # Calculate confidence (distance from 0.5)
    confidence = abs(probability - 0.5) * 2
    
    return int(prediction), float(probability), float(confidence)


def predict_url_phishing(url: str) -> tuple:
    """
    Predict if URL is phishing
    Returns: (prediction, probability, confidence)
    """
    if url_model is None or url_vectorizer is None:
        raise HTTPException(status_code=500, detail="URL model not loaded")
    
    # Preprocess
    cleaned_url = preprocess_url(url)
    
    # Transform to features
    features = url_vectorizer.transform([cleaned_url])
    
    # Predict
    prediction = url_model.predict(features)[0]
    probabilities = url_model.predict_proba(features)[0]
    probability = probabilities[1] if len(probabilities) > 1 else probabilities[0]
    
    # Calculate confidence
    confidence = abs(probability - 0.5) * 2
    
    return int(prediction), float(probability), float(confidence)


def extract_urls_from_text(text: str) -> List[str]:
    """
    Extract URLs from text
    """
    url_pattern = re.compile(r'https?://[^\s)"\'<>]+')
    return url_pattern.findall(text)


@app.on_event("startup")
async def startup_event():
    """
    Load models when the application starts
    """
    logger.info("Starting up...")
    load_models()


@app.get("/")
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "Phishing Detection API",
        "version": "1.0.0",
        "endpoints": {
            "predict_email": "POST /predict-email",
            "predict_url": "POST /predict-url",
            "analyze_email": "POST /analyze_email",
            "websocket": "WS /ws/analyze"
        }
    }


@app.post("/predict-email", response_model=EmailPredictionResponse)
async def predict_email(request: EmailPredictionRequest):
    """
    Predict if an email is spam
    
    Args:
        request: EmailPredictionRequest with email text
        
    Returns:
        EmailPredictionResponse with prediction, probability, and confidence
    """
    try:
        prediction, probability, confidence = predict_email_spam(request.text)
        
        return EmailPredictionResponse(
            prediction=prediction,
            probability=probability,
            confidence=confidence
        )
    except Exception as e:
        logger.error(f"Error predicting email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict-url", response_model=URLPredictionResponse)
async def predict_url(request: URLPredictionRequest):
    """
    Predict if a URL is phishing
    
    Args:
        request: URLPredictionRequest with URL string
        
    Returns:
        URLPredictionResponse with prediction, probability, and confidence
    """
    try:
        prediction, probability, confidence = predict_url_phishing(request.url)
        
        return URLPredictionResponse(
            prediction=prediction,
            probability=probability,
            confidence=confidence
        )
    except Exception as e:
        logger.error(f"Error predicting URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze_email", response_model=PhishingAnalysisResponse)
async def analyze_email(request: PhishingAnalysisRequest):
    """
    Comprehensive phishing analysis endpoint (for frontend integration)
    
    Analyzes:
    - Email text (NLP score)
    - URLs in the text (URL score)
    - Overall risk score
    
    Args:
        request: PhishingAnalysisRequest with text, urls, and images
        
    Returns:
        PhishingAnalysisResponse with risk scores and explainability
    """
    try:
        # Simulate progress updates via WebSocket would happen here
        # For now, we'll do synchronous analysis
        
        # Analyze email text
        nlp_prediction, nlp_prob, nlp_conf = predict_email_spam(request.text)
        nlp_score = nlp_prob  # Convert to 0-1 scale
        
        # Analyze URLs
        url_scores = []
        url_warnings = []
        
        # Extract URLs from text if not provided
        all_urls = request.urls.copy()
        if request.text:
            extracted_urls = extract_urls_from_text(request.text)
            all_urls.extend(extracted_urls)
        
        # Remove duplicates
        all_urls = list(set(all_urls))
        
        for url in all_urls:
            url_pred, url_prob, url_conf = predict_url_phishing(url)
            url_scores.append(url_prob)
            if url_pred == 1:
                url_warnings.append(f"Suspicious URL detected: {url}")
        
        # Calculate average URL score
        url_score = np.mean(url_scores) if url_scores else 0.0
        
        # Vision score (placeholder - would use image analysis if implemented)
        vision_score = 0.0
        if request.images_b64:
            # In a real implementation, you would analyze images here
            vision_score = 0.5  # Placeholder
        
        # Calculate overall risk score (weighted average)
        risk_score = (nlp_score * 0.5 + url_score * 0.4 + vision_score * 0.1)
        
        # Generate explainability factors
        factors = []
        if nlp_score > 0.7:
            factors.append("Email text shows high spam indicators")
        if url_score > 0.7:
            factors.append("Suspicious URLs detected in the message")
        if len(url_warnings) > 0:
            factors.append(f"{len(url_warnings)} suspicious URL(s) found")
        if risk_score < 0.3:
            factors.append("Message appears safe")
        
        if not factors:
            factors.append("Mixed signals detected")
        
        explainability = Explainability(
            factors=factors,
            warnings=url_warnings
        )
        
        return PhishingAnalysisResponse(
            risk_score=float(risk_score),
            nlp_score=float(nlp_score),
            url_score=float(url_score),
            vision_score=float(vision_score),
            explainability=explainability
        )
        
    except Exception as e:
        logger.error(f"Error analyzing email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    """
    WebSocket endpoint for real-time analysis progress updates
    """
    await websocket.accept()
    
    try:
        # Wait for analysis request
        data = await websocket.receive_json()
        
        # Send progress updates
        steps = [
            ("Loading models", 10),
            ("Analyzing email text", 30),
            ("Checking URLs", 60),
            ("Finalizing results", 90),
            ("Complete", 100)
        ]
        
        for step, percent in steps:
            await websocket.send_json({
                "type": "progress",
                "payload": {
                    "step": step,
                    "percent": percent
                }
            })
            await asyncio.sleep(0.5)  # Simulate processing time
        
        # Perform actual analysis
        request = PhishingAnalysisRequest(**data)
        
        # Analyze email text
        nlp_prediction, nlp_prob, nlp_conf = predict_email_spam(request.text)
        nlp_score = nlp_prob
        
        # Analyze URLs
        all_urls = request.urls.copy()
        if request.text:
            extracted_urls = extract_urls_from_text(request.text)
            all_urls.extend(extracted_urls)
        all_urls = list(set(all_urls))
        
        url_scores = []
        url_warnings = []
        for url in all_urls:
            url_pred, url_prob, url_conf = predict_url_phishing(url)
            url_scores.append(url_prob)
            if url_pred == 1:
                url_warnings.append(f"Suspicious URL detected: {url}")
        
        url_score = np.mean(url_scores) if url_scores else 0.0
        vision_score = 0.0
        risk_score = (nlp_score * 0.5 + url_score * 0.4 + vision_score * 0.1)
        
        factors = []
        if nlp_score > 0.7:
            factors.append("Email text shows high spam indicators")
        if url_score > 0.7:
            factors.append("Suspicious URLs detected")
        if len(url_warnings) > 0:
            factors.append(f"{len(url_warnings)} suspicious URL(s) found")
        if risk_score < 0.3:
            factors.append("Message appears safe")
        if not factors:
            factors.append("Mixed signals detected")
        
        # Send final result
        result = {
            "risk_score": float(risk_score),
            "nlp_score": float(nlp_score),
            "url_score": float(url_score),
            "vision_score": float(vision_score),
            "explainability": {
                "factors": factors,
                "warnings": url_warnings
            }
        }
        
        await websocket.send_json({
            "type": "result",
            "payload": result
        })
        
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({
            "type": "error",
            "payload": {"message": str(e)}
        })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
