"""
FastAPI Backend for Phishing Detection

Provides REST API endpoints for:
- /predict-email: Predict if email text is spam
- /predict-url: Predict if URL is phishing
- /analyze: Comprehensive analysis endpoint (frontend target)
- /analyze_email: Same as /analyze (legacy)
- WebSocket endpoint for progress updates
"""

import os
import pickle
import re
import numpy as np
import logging
import asyncio
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Global variables
risk_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    global risk_engine
    logger.info("Starting up...")
    logger.info("Initializing Advanced AI Risk Engine...")
    
    # Import here to avoid circular dependencies if any, and ensuring env is ready
    from logic import RiskEngine
    risk_engine = RiskEngine()
    
    logger.info("Risk Engine initialized successfully")
    yield
    logger.info("Shutting down...")

app = FastAPI(title="Phishing Detection API", version="2.0.0", lifespan=lifespan)

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    # Explicitly allow the frontend port and common dev ports
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class PhishingAnalysisRequest(BaseModel):
    text: str = ""
    urls: List[str] = []
    images_b64: List[str] = []

class Explainability(BaseModel):
    factors: List[str]
    warnings: List[str]

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
    explainable_reasons: List[str]
    explainable_ai: List[Evidence]
    analysis_summary: str

# Helper
def extract_urls_from_text(text: str) -> List[str]:
    url_pattern = re.compile(r'https?://[^\s)"\'<>]+')
    return url_pattern.findall(text)

@app.get("/")
async def root():
    return {
        "message": "Phishing Detection API v2 (Transformer/Advanced)",
        "version": "2.0.0",
        "endpoints": {
            "analyze": "POST /analyze",
        }
    }

async def perform_analysis(request: PhishingAnalysisRequest) -> PhishingAnalysisResponse:
    if risk_engine is None:
        raise HTTPException(status_code=503, detail="Risk Engine not ready")

    # Extract URLs if needed
    all_urls = request.urls.copy()
    if request.text:
        extracted = extract_urls_from_text(request.text)
        all_urls.extend(extracted)
    
    # Dedup
    all_urls = list(set(all_urls))

    # Run Analysis
    # Note: RiskEngine run is synchronous (compute bound), but fast enough or should be offloaded if heavy.
    # For now, running in main thread is okay for a demo, or use run_in_executor.
    
    try:
        # Offload to thread pool to avoid blocking async loop since models are CPU bound
        result = await asyncio.to_thread(risk_engine.analyze, request.text, all_urls, request.images_b64)
        
        explainability = Explainability(
            factors=result['factors'],
            warnings=result['warnings']
        )
        
        # CRITICAL: Backend returns scores in 0-100 range, but frontend expects 0-1 range
        # Convert by dividing by 100
        return PhishingAnalysisResponse(
            risk_score=result['risk_score'] / 100.0,
            nlp_score=result['nlp_score'] / 100.0,
            url_score=result['url_score'] / 100.0,
            vision_score=result['vision_score'] / 100.0,
            risk_level=result['risk_level'],
            verdict=result['verdict'],
            explainability=explainability,
            explainable_reasons=result['factors'],
            explainable_ai=[Evidence(**ev) for ev in result['explainable_ai']],
            analysis_summary=result['analysis_summary']
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze", response_model=PhishingAnalysisResponse)
async def analyze_main(request: PhishingAnalysisRequest):
    return await perform_analysis(request)

@app.post("/analyze_email", response_model=PhishingAnalysisResponse)
async def analyze_email(request: PhishingAnalysisRequest):
    return await perform_analysis(request)

@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        
        # Mock progress
        steps = [("Initializing AI", 10), ("Scanning Text (Transformer)", 30), 
                 ("Analyzing URLs", 60), ("Vision Processing", 80), ("Finalizing", 100)]
        
        for step, percent in steps:
            await websocket.send_json({"type": "progress", "payload": {"step": step, "percent": percent}})
            await asyncio.sleep(0.1)
        
        request = PhishingAnalysisRequest(
            text=data.get('text', ''),
            urls=data.get('urls', []),
            images_b64=data.get('images_b64', [])
        )
        
        result_response = await perform_analysis(request)
        
        await websocket.send_json({
            "type": "result",
            "payload": result_response.dict()
        })
        
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WS Error: {e}")
        await websocket.send_json({"type": "error", "payload": {"message": str(e)}})


if __name__ == '__main__':
    try:
        logger.info('Starting server on port 8000...')
        uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')
    except Exception as e:
        logger.error(f'Failed to start server: {e}')
        raise
