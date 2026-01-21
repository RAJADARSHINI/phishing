
import logging
import torch
from transformers import pipeline
from PIL import Image
import io
import base64

logger = logging.getLogger(__name__)

class VisionAnalyzer:
    def __init__(self):
        self.pipeline = None
        self.device = 0 if torch.cuda.is_available() else -1
        try:
            # Using CLIP (Contrastive Language-Image Pre-Training) for zero-shot classification
            # It can detect if an image matches description "login page" or "screenshot" vs "nature"
            logger.info("Loading Vision model (clip-vit-base-patch32)...")
            self.pipeline = pipeline("zero-shot-image-classification", model="openai/clip-vit-base-patch32", device=self.device)
            logger.info("Vision model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Vision model: {e}")
            self.pipeline = None
        
        # Classes to check against
        self.candidate_labels = ["login page", "screenshot of a website", "logo", "natural image", "document", "random noise"]

    def analyze(self, image_b64: str):
        if not image_b64:
            return {"score": 0.0, "reasons": []}

        score = 0.0
        reasons = []

        try:
            # Decode base64
            if "," in image_b64:
                image_b64 = image_b64.split(",")[1]
            image_data = base64.b64decode(image_b64)
            image = Image.open(io.BytesIO(image_data))

            # 1. CLIP Analysis
            if self.pipeline:
                predictions = self.pipeline(images=image, candidate_labels=self.candidate_labels)
                # Format: [{'score': 0.9, 'label': 'login page'}, ...]
                
                # Check top prediction
                top_pred = predictions[0]
                label = top_pred['label']
                conf = top_pred['score']

                if label in ["login page", "screenshot of a website"] and conf > 0.6:
                    score = conf
                    reasons.append(f"Image appears to be a {label} ({int(conf*100)}% match)")
                    # High risk if an image is a screenshot of a login page (common in phishing to evade text filters)
                    if label == "login page":
                        score = max(score, 0.8)
                        reasons.append("Login form detected in image (potential text-evasion phishing)")
                
                if label == "logo" and conf > 0.7:
                    reasons.append("Brand logo detected")
                    # Logo alone isn't phishing, but context matters.
                    score += 0.2

            # 2. Simple Image Entropy/Size Heuristics
            # Very small images are usually tracking pixels or icons, harmless usually.
            if image.size[0] < 50 or image.size[1] < 50:
                pass # Tracker pixel?
            
        except Exception as e:
            logger.error(f"Vision analysis error: {e}")
            pass

        score = min(score, 0.99)
        return {
            "score": score,
            "reasons": reasons
        }
