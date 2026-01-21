
from .nlp import NLPAnalyzer
from .url_analysis import URLAnalyzer
from .vision import VisionAnalyzer
import numpy as np

class RiskEngine:
    def __init__(self):
        self.nlp = NLPAnalyzer()
        self.url = URLAnalyzer()
        self.vision = VisionAnalyzer()

    def analyze(self, text: str, urls: list, images_b64: list):
        # 1. NLP
        nlp_res = self.nlp.analyze(text)
        nlp_score = nlp_res['score']
        factors = nlp_res['reasons'][:]

        # 2. URL
        url_scores = []
        # If URLs are passed explicitly, use them. Else extraction happens in backend (but here we assume extract happened before or we do it here)
        # Note: app.py handles extraction.
        
        for u in urls:
            u_res = self.url.analyze(u)
            url_scores.append(u_res['score'])
            factors.extend(u_res['reasons'])
        
        url_score = max(url_scores) if url_scores else 0.0

        # 3. Vision
        vision_scores = []
        for img in images_b64:
            v_res = self.vision.analyze(img)
            vision_scores.append(v_res['score'])
            factors.extend(v_res['reasons'])
        
        vision_score = max(vision_scores) if vision_scores else 0.0

        # 4. Unified Scoring Logic
        # New weighted logic: URL is highest risk, then NLP, then Vision is supplementary
        # If ANY channel is Critical (>0.9), the whole Global score boosts up.
        
        weights = {'nlp': 0.4, 'url': 0.5, 'vision': 0.1}
        
        # Adaptive weights: If URL is 0 risk, rely more on NLP
        if url_score == 0 and vision_score == 0:
            weights = {'nlp': 1.0, 'url': 0.0, 'vision': 0.0}
        elif nlp_score == 0 and url_score > 0:
            weights = {'nlp': 0.0, 'url': 0.9, 'vision': 0.1}

        risk_score = (nlp_score * weights['nlp']) + (url_score * weights['url']) + (vision_score * weights['vision'])

        # Critical Overrides
        if url_score > 0.9:
            risk_score = max(risk_score, 0.95)
            factors.append("CRITICAL: Known malicious URL pattern detected")
        
        if nlp_score > 0.9:
             risk_score = max(risk_score, 0.90)

        # 5. Final Factor Cleanup
        if risk_score < 0.1:
            factors.append("No significant threats detected")
        elif risk_score > 0.8:
            factors.append("Target is HIGH RISK based on composite analysis")

        return {
            "risk_score": float(risk_score),
            "nlp_score": float(nlp_score),
            "url_score": float(url_score),
            "vision_score": float(vision_score),
            "factors": list(set(factors)), # dedup
            "warnings": [f for f in factors if "CRITICAL" in f or "Suspicious" in f]
        }
