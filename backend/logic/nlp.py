
import logging
import os
import pickle
import re
import numpy as np

logger = logging.getLogger(__name__)

class NLPAnalyzer:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self._load_models()

        # 2. Psychological Manipulation Detection (Rule-based)
        self.urgency_patterns = [
            r"urgent", r"immediately", r"now", r"limited time", r"24 hours", 
            r"act fast", r"immediate action", r"expires", r"deadline"
        ]
        self.fear_patterns = [
            r"suspended", r"blocked", r"unusual activity", r"unauthorized", 
            r"legal action", r"warrant", r"arrest", r"terminated", r"breach"
        ]
        self.authority_patterns = [
            r"admin", r"support team", r"security department", r"verification center",
            r"bank", r"irs", r"tax", r"ceo", r"hr department"
        ]
        self.action_requests = [
            r"click here", r"verify", r"confirm", r"update your", 
            r"sign in", r"log in", r"reply", r"download"
        ]

    def _load_models(self):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_path, "models", "email_model.pkl")
        vectorizer_path = os.path.join(base_path, "models", "email_vectorizer.pkl")

        try:
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                logger.info("Loading local NLP models...")
                with open(model_path, "rb") as f:
                    self.model = pickle.load(f)
                with open(vectorizer_path, "rb") as f:
                    self.vectorizer = pickle.load(f)
                logger.info("Local NLP models loaded successfully.")
            else:
                logger.error(f"Model files not found at {model_path} or {vectorizer_path}")
        except Exception as e:
            logger.error(f"Failed to load NLP models: {e}")

    def analyze(self, text: str):
        """
        PRODUCTION-GRADE NLP Analysis with Psychological Detection + ML
        Returns score in 0-100 range with detailed evidence
        
        CRITICAL: Psychological rules are PRIMARY (reliable), ML is SECONDARY boost
        """
        if not text:
            return {"score": 0.0, "reasons": [], "evidence": [], "ml_confidence": 0.0}

        lower_text = text.lower()
        detected_indicators = []
        psychological_score = 0.0
        
        # ========================================
        # STEP 1: PSYCHOLOGICAL MANIPULATION DETECTION (PRIMARY)
        # Each pattern adds points - this is RELIABLE
        # ========================================
        
        # PATTERN 1: Urgency / Time Pressure (+20 points)
        urgency_evidence = self._extract_evidence(text, lower_text, self.urgency_patterns)
        if urgency_evidence:
            psychological_score += 20.0
            detected_indicators.append({
                "indicator": "⏰ Urgency / Time Pressure",
                "evidence": urgency_evidence,
                "reason": "Creates artificial deadline to bypass rational decision-making",
                "weight": 20.0
            })

        # PATTERN 2: Fear / Threat Language (+25 points - HIGHEST WEIGHT)
        fear_evidence = self._extract_evidence(text, lower_text, self.fear_patterns)
        if fear_evidence:
            psychological_score += 25.0
            detected_indicators.append({
                "indicator": "😱 Fear / Loss Threat",
                "evidence": fear_evidence,
                "reason": "Threatens negative consequences to induce panic-driven compliance",
                "weight": 25.0
            })

        # PATTERN 3: Authority Impersonation (+18 points)
        authority_evidence = self._extract_evidence(text, lower_text, self.authority_patterns)
        if authority_evidence:
            psychological_score += 18.0
            detected_indicators.append({
                "indicator": "👔 Authority Impersonation",
                "evidence": authority_evidence,
                "reason": "Falsely claims to represent trusted authority to gain compliance",
                "weight": 18.0
            })

        # PATTERN 4: Coercive Action Requests (+15 points)
        action_evidence = self._extract_evidence(text, lower_text, self.action_requests)
        if action_evidence:
            psychological_score += 15.0
            detected_indicators.append({
                "indicator": "🎯 Coercive Action Request",
                "evidence": action_evidence,
                "reason": "Demands immediate action without allowing verification",
                "weight": 15.0
            })

        # PATTERN 5: Generic/Unverifiable Identity (+12 points)
        generic_patterns = [r"dear user", r"dear customer", r"dear account holder", 
                          r"valued customer", r"dear member", r"account user"]
        identity_evidence = self._extract_evidence(text, lower_text, generic_patterns)
        if identity_evidence:
            psychological_score += 12.0
            detected_indicators.append({
                "indicator": "👤 Generic Identity",
                "evidence": identity_evidence,
                "reason": "Uses generic salutation instead of personalized information",
                "weight": 12.0
            })

        # PATTERN 6: Ambiguous Security Claims (+10 points)
        ambiguous_patterns = [r"security alert", r"unusual activity", r"suspicious login",
                            r"verification required", r"account review", r"security update"]
        ambiguous_evidence = self._extract_evidence(text, lower_text, ambiguous_patterns)
        if ambiguous_evidence:
            psychological_score += 10.0
            detected_indicators.append({
                "indicator": "🔒 Ambiguous Security Claim",
                "evidence": ambiguous_evidence,
                "reason": "Makes vague security claims without specific verifiable details",
                "weight": 10.0
            })

        # ========================================
        # STEP 2: ML MODEL - SECONDARY BOOST (if available)
        # Only use ML if it's confident AND psychological score is low
        # ========================================
        ml_confidence = 0.0
        ml_boost = 0.0
        
        if self.model and self.vectorizer:
            try:
                features = self.vectorizer.transform([text])
                ml_prob = self.model.predict_proba(features)[0][1]  # Probability of phishing
                ml_confidence = ml_prob
                
                # Only use ML boost if:
                # 1. ML is confident (>70%)
                # 2. Psychological score is low (<40)
                # This prevents ML from dominating when rules already detected threats
                if ml_prob > 0.7 and psychological_score < 40:
                    ml_boost = min(ml_prob * 30.0, 30.0)  # Max +30 points
                    detected_indicators.append({
                        "indicator": "🤖 ML Pattern Recognition",
                        "evidence": f"AI model confidence: {int(ml_prob*100)}%",
                        "reason": "Machine learning detected linguistic patterns consistent with phishing",
                        "weight": ml_boost
                    })
                
                logger.info(f"ML Model: confidence={ml_confidence:.2f}, boost={ml_boost:.1f}")
                
            except Exception as e:
                logger.error(f"ML prediction error: {e}")

        # ========================================
        # STEP 3: FINAL NLP SCORE CALCULATION
        # Psychological score + ML boost
        # ========================================
        final_nlp_score = psychological_score + ml_boost
        
        # Clamp to 0-100 range
        final_nlp_score = min(max(final_nlp_score, 0.0), 100.0)
        
        logger.info(f"NLP Analysis: Psychological={psychological_score:.1f} + ML Boost={ml_boost:.1f} = {final_nlp_score:.1f}")
        
        # ========================================
        # STEP 4: GENERATE HUMAN-READABLE REASONS
        # ========================================
        reasons = []
        for ind in detected_indicators:
            evidence_text = ind['evidence'][:60] + "..." if len(ind['evidence']) > 60 else ind['evidence']
            reasons.append(f"{ind['indicator']} (+{ind['weight']:.0f} risk): {evidence_text}")
        
        # Add ML confidence note if it was used
        if ml_confidence > 0.5 and ml_boost == 0:
            reasons.append(f"🤖 ML Model: {int(ml_confidence*100)}% confidence (not used - psychological signals sufficient)")
        
        return {
            "score": float(final_nlp_score),  # 0-100 range
            "reasons": reasons,
            "evidence": detected_indicators,
            "ml_confidence": ml_confidence,
            "psychological_score": psychological_score,
            "ml_boost": ml_boost
        }
    
    def _extract_evidence(self, original_text: str, lower_text: str, patterns: list) -> str:
        """
        Extract the actual text that matched the pattern as evidence
        """
        for pattern in patterns:
            match = re.search(pattern, lower_text)
            if match:
                # Find the match position and extract surrounding context from original text
                start = max(0, match.start() - 10)
                end = min(len(original_text), match.end() + 30)
                evidence = original_text[start:end].strip()
                # Clean up
                if start > 0:
                    evidence = "..." + evidence
                if end < len(original_text):
                    evidence = evidence + "..."
                return evidence
        return ""

    def _check_patterns(self, text, patterns):
        for p in patterns:
            if re.search(p, text):
                return True
        return False
