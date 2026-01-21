
import re
import logging
from urllib.parse import urlparse
import socket

logger = logging.getLogger(__name__)

class URLAnalyzer:
    def __init__(self):
        self.suspicious_tlds = ['.xyz', '.top', '.club', '.info', '.gq', '.cn', '.ru']
        self.suspicious_keywords = ['login', 'verify', 'secure', 'account', 'update', 'banking', 'signin']
        self.shorteners = ['bit.ly', 'goo.gl', 'tinyurl.com', 't.co']

    def analyze(self, url: str):
        if not url:
            return {"score": 0.0, "reasons": []}

        score = 0.0
        reasons = []

        try:
            parsed = urlparse(url if url.startswith('http') else 'http://' + url)
            domain = parsed.netloc.lower()
            
            # 1. Check for IP address based URL
            ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
            if re.match(ip_pattern, domain):
                score = 0.9
                reasons.append("URL uses an IP address instead of a domain name")
            
            # 2. Suspicious TLD
            if any(domain.endswith(tld) for tld in self.suspicious_tlds):
                score += 0.4
                reasons.append("Suspicious Top-Level Domain (TLD) detected")

            # 3. Keyword stuffing in URL
            found_keywords = [k for k in self.suspicious_keywords if k in url.lower()]
            if found_keywords:
                score += 0.3
                reasons.append(f"Suspicious keywords in URL: {', '.join(found_keywords)}")

            # 4. URL Shorteners
            if domain in self.shorteners:
                score += 0.3
                reasons.append("URL Shortener used (hides true destination)")

            # 5. Length check
            if len(url) > 75:
                score += 0.2
                reasons.append("URL is abnormally long")

            # 6. '@' Symbol (Credentials in URL)
            if '@' in url:
                score = 0.95
                reasons.append("URL contains '@' symbol (possible credential harvesting)")

        except Exception as e:
            logger.error(f"URL analysis error: {e}")
            pass

        score = min(score, 0.99)
        return {
            "score": score,
            "reasons": reasons
        }
