
import logging
import torch
from transformers import pipeline
import re

logger = logging.getLogger(__name__)

class NLPAnalyzer:
    def __init__(self):
        self.pipeline = None
        self.device = 0 if torch.cuda.is_available() else -1
        try:
            # Using a tiny BERT model fine-tuned for spam detection for speed and efficiency
            # Fallback to a lightweight model if this specific one isn't desired, but this is a real model.
            logger.info("Loading NLP model (bert-tiny-finetuned-sms-spam-detection)...")
            self.pipeline = pipeline("text-classification", model="mrm8488/bert-tiny-finetuned-sms-spam-detection", device=self.device)
            logger.info("NLP model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load NLP model: {e}")
            self.pipeline = None

        # Heuristic keywords for explainability
        self.urgency_words = ["urgent", "identify", "immediately", "suspended", "lock", "verify"]
        self.financial_words = ["bank", "credit", "card", "payment", "btc", "bitcoin", "invoice"]
        self.fear_words = ["warrant", "arrest", "lawsuit", "police", "legal"]

    def analyze(self, text: str):
        if not text:
            return {"score": 0.0, "reasons": []}

        score = 0.0
        reasons = []

        # 1. Transformer Prediction
        if self.pipeline:
            try:
                # Truncate text to 512 chars to prevent model crash
                prediction = self.pipeline(text[:512])[0]
                # Label is typically LABEL_0 (Ham) or LABEL_1 (Spam) or 'HAM'/'SPAM' depending on model config
                # For this specific model: LABEL_1 = Spam
                label = prediction['label']
                raw_score = prediction['score']
                
                if label in ['LABEL_1', 'SPAM', 'Spam']:
                    score = raw_score
                    reasons.append(f"AI Model detected spam patterns ({int(raw_score*100)}% confidence)")
                else:
                    # It's Ham, but maybe low confidence?
                    # If it's confidently ham, score remains 0.
                    pass
            except Exception as e:
                logger.error(f"NLP prediction error: {e}")
                pass

        # 2. Heuristic augmentation (Transformer + Rules = Hybrid better detection)
        lower_text = text.lower()
        
        urgency_count = sum(1 for w in self.urgency_words if w in lower_text)
        if urgency_count > 0:
            boost = min(urgency_count * 0.1, 0.3)
            score = max(score, 0.3) + boost
            reasons.append("Use of urgent/threatening language")

        financial_count = sum(1 for w in self.financial_words if w in lower_text)
        if financial_count > 0:
            score += 0.15
            reasons.append("Financial request or terminology detected")

        fear_count = sum(1 for w in self.fear_words if w in lower_text)
        if fear_count > 0:
            score += 0.2
            reasons.append("Legal or authoritarian threats detected")

        # Clamp score
        score = min(score, 0.99)
        
        return {
            "score": score,
            "reasons": reasons
        }
