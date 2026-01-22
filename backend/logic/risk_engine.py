
import re
from .nlp import NLPAnalyzer
from .url_analysis import URLAnalyzer
from .vision import VisionAnalyzer
import numpy as np
import logging

logger = logging.getLogger(__name__)

class RiskEngine:
    def __init__(self):
        self.nlp = NLPAnalyzer()
        self.url = URLAnalyzer()
        self.vision = VisionAnalyzer()

    def _extract_urls_from_text(self, text: str) -> list:
        """Extract all URLs from text using regex"""
        url_pattern = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')
        urls = url_pattern.findall(text)
        logger.info(f"Extracted {len(urls)} URLs from text: {urls}")
        return urls

    def analyze(self, text: str, urls: list, images_b64: list):
        """
        PRODUCTION-GRADE Explainable AI Threat Analysis Engine
        
        CRITICAL CHANGES:
        - Uses ADDITIVE scoring (not weighted averaging)
        - High-risk signals DOMINATE the final score
        - Returns 0-100 range for all scores
        - Extracts URLs from text automatically
        - Real-time threat intelligence
        
        SCORING LOGIC:
        - NLP score: 0-100 (ML model + psychological boosts)
        - URL score: 0-100 (additive threat detection)
        - Vision score: 0-100 (image analysis)
        - Unified Risk: Uses MAX of component scores with boost from multiple threats
        """
        all_evidence = []
        factors = []
        
        # ========================================
        # STEP 1: NLP ANALYSIS (0-100 scale)
        # ========================================
        nlp_res = self.nlp.analyze(text)
        nlp_score = nlp_res['score']  # Already 0-100 from new NLP analyzer
        factors.extend(nlp_res['reasons'])
        if 'evidence' in nlp_res:
            all_evidence.extend(nlp_res.get('evidence', []))
        
        logger.info(f"NLP Score: {nlp_score:.1f}/100")

        # ========================================
        # STEP 2: URL ANALYSIS (0-100 scale)
        # Extract URLs from text + provided URLs
        # ========================================
        all_urls = list(urls) if urls else []
        
        # CRITICAL: Extract URLs from text
        if text:
            extracted_urls = self._extract_urls_from_text(text)
            all_urls.extend(extracted_urls)
        
        # Deduplicate
        all_urls = list(set(all_urls))
        
        url_scores = []
        for u in all_urls:
            u_res = self.url.analyze(u)
            url_scores.append(u_res['score'])  # Already 0-100
            factors.extend(u_res['reasons'])
            if 'evidence' in u_res:
                all_evidence.extend(u_res.get('evidence', []))
        
        # Use MAX URL score (worst URL dominates)
        url_score = max(url_scores) if url_scores else 0.0
        logger.info(f"URL Score: {url_score:.1f}/100 (analyzed {len(all_urls)} URLs)")

        # ========================================
        # STEP 3: VISION ANALYSIS (0-100 scale)
        # ========================================
        vision_scores = []
        for img in images_b64:
            v_res = self.vision.analyze(img)
            vision_scores.append(v_res['score'])  # Already 0-100
            factors.extend(v_res['reasons'])
        
        vision_score = max(vision_scores) if vision_scores else 0.0
        logger.info(f"Vision Score: {vision_score:.1f}/100")

        # ========================================
        # STEP 4: UNIFIED RISK SCORE CALCULATION
        # CRITICAL: Use MAX-based scoring with multi-threat boost
        # ========================================
        
        # Start with the HIGHEST individual score (most dangerous signal)
        base_risk = max(nlp_score, url_score, vision_score)
        
        # Count how many channels detected threats (score > 30)
        threat_channels = sum([
            1 if nlp_score > 30 else 0,
            1 if url_score > 30 else 0,
            1 if vision_score > 30 else 0
        ])
        
        # Multi-channel threat boost
        # If multiple channels detect threats, it's MORE dangerous
        multi_threat_boost = 0.0
        if threat_channels >= 2:
            multi_threat_boost = 15.0  # +15 if 2 channels
        if threat_channels >= 3:
            multi_threat_boost = 25.0  # +25 if all 3 channels
        
        # Calculate unified risk
        unified_risk = base_risk + multi_threat_boost
        
        # Clamp to 0-100
        unified_risk = min(max(unified_risk, 0.0), 100.0)
        
        logger.info(f"UNIFIED RISK: {unified_risk:.1f}/100 (base={base_risk:.1f}, multi-threat-boost={multi_threat_boost:.1f})")

        # ========================================
        # STEP 5: RISK LEVEL CLASSIFICATION
        # ========================================
        if unified_risk >= 70:
            risk_level = "High Risk"
            verdict = "THREAT"
        elif unified_risk >= 31:
            risk_level = "Suspicious"
            verdict = "THREAT"
        else:
            risk_level = "Safe"
            verdict = "SAFE"
        
        logger.info(f"VERDICT: {verdict} ({risk_level})")

        # ========================================
        # STEP 6: EXPLANATIONS
        # ========================================
        unique_factors = list(dict.fromkeys(factors))  # Deduplicate
        
        # Generate analysis summary
        summary_parts = []
        if nlp_score > 30:
            summary_parts.append(f"Text analysis detected psychological manipulation (score: {nlp_score:.0f}/100)")
        if url_score > 30:
            summary_parts.append(f"URL analysis identified suspicious patterns (score: {url_score:.0f}/100)")
        if vision_score > 30:
            summary_parts.append(f"Image analysis flagged visual anomalies (score: {vision_score:.0f}/100)")
        
        if not summary_parts:
            analysis_summary = "No significant threat indicators detected. Message appears safe."
        else:
            analysis_summary = ". ".join(summary_parts) + f". Overall risk: {risk_level}."

        # ========================================
        # STEP 7: RETURN RESPONSE
        # All scores in 0-100 range
        # ========================================
        return {
            "risk_score": float(unified_risk),
            "nlp_score": float(nlp_score),
            "url_score": float(url_score),
            "vision_score": float(vision_score),
            "risk_level": risk_level,
            "verdict": verdict,
            "factors": unique_factors,
            "warnings": [f for f in unique_factors if any(word in f.lower() for word in ["critical", "threat", "suspicious", "detected", "🚨", "⚠️"])],
            "explainable_ai": all_evidence,
            "analysis_summary": analysis_summary
        }
