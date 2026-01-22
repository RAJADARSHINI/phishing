
import re
import logging
from urllib.parse import urlparse
import socket

logger = logging.getLogger(__name__)

class URLAnalyzer:
    def __init__(self):
        self.suspicious_tlds = ['.tk', '.ru', '.cn', '.zip', '.xyz', '.top', '.gq']
        self.suspicious_keywords = ['login', 'verify', 'secure', 'account', 'update', 'banking', 'signin', 'support']
        self.shorteners = ['bit.ly', 'goo.gl', 'tinyurl.com', 't.co', 'is.gd', 'buff.ly', 'ad.vu']
        
        # Simulating brand names for mismatch detection
        self.common_brands = ['paypal', 'google', 'apple', 'microsoft', 'facebook', 'netflix', 'amazon']

    def analyze(self, url: str):
        """
        PRODUCTION-GRADE URL Intelligence Analysis
        Returns score in 0-100 range with detailed evidence
        
        CRITICAL: Uses ADDITIVE scoring - multiple threats compound
        """
        if not url:
            return {"score": 0.0, "reasons": [], "evidence": []}

        score = 0.0
        reasons = []
        evidence = []

        try:
            # Fix URL scheme
            if not url.startswith(('http://', 'https://')):\
                url = 'http://' + url
                
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            
            # ========================================
            # THREAT DETECTION - ADDITIVE SCORING
            # ========================================
            
            # 1. IP Address check (CRITICAL: +40 points)
            ipv4_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
            if re.match(ipv4_pattern, domain):
                score += 40.0
                reasons.append(f"🚨 IP-based URL detected: {domain}")
                evidence.append({
                    "indicator": "IP-based URL (CRITICAL)",
                    "evidence": domain,
                    "reason": "Legitimate sites use domain names, not raw IP addresses",
                    "weight": 40.0
                })
            
            # 2. Suspicious TLDs (HIGH: +25 points)
            for tld in self.suspicious_tlds:
                if domain.endswith(tld):
                    score += 25.0
                    reasons.append(f"⚠️ Suspicious TLD: {tld}")
                    evidence.append({
                        "indicator": "Suspicious Top-Level Domain",
                        "evidence": tld,
                        "reason": "This TLD is commonly associated with malicious campaigns",
                        "weight": 25.0
                    })
                    break

            # 3. URL Shorteners (MEDIUM: +20 points)
            if domain in self.shorteners:
                score += 20.0
                reasons.append(f"🔗 URL shortener used: {domain}")
                evidence.append({
                    "indicator": "URL Shortener",
                    "evidence": domain,
                    "reason": "Shorteners hide the true destination - potential redirection attack",
                    "weight": 20.0
                })
                
            # 4. Brand Mismatch / Typosquatting (HIGH: +30 points)
            for brand in self.common_brands:
                if brand in domain:
                    if not (domain == f"{brand}.com" or domain.endswith(f".{brand}.com")):
                        score += 30.0
                        reasons.append(f"🎭 Brand impersonation: '{brand}' in suspicious domain")
                        evidence.append({
                            "indicator": "Brand Impersonation (CRITICAL)",
                            "evidence": domain,
                            "reason": f"Domain contains '{brand}' but is NOT the official domain",
                            "weight": 30.0
                        })
                        break

            # 5. Keyword Stuffing (MEDIUM: +5 per keyword, max +15)
            found_keywords = [k for k in self.suspicious_keywords if k in url.lower()]
            if found_keywords:
                keyword_score = min(len(found_keywords) * 5.0, 15.0)
                score += keyword_score
                reasons.append(f"🔑 Suspicious keywords: {', '.join(found_keywords)}")
                evidence.append({
                    "indicator": "Credential Harvesting Keywords",
                    "evidence": ', '.join(found_keywords),
                    "reason": "URL contains terms commonly used in phishing attacks",
                    "weight": keyword_score
                })

            # 6. Length and Obfuscation (LOW: +10 points)
            if len(url) > 75:
                score += 10.0
                reasons.append(f"📏 Abnormally long URL: {len(url)} characters")
                evidence.append({
                    "indicator": "URL Length Anomaly",
                    "evidence": f"{len(url)} characters",
                    "reason": "Long URLs may be obfuscating malicious intent",
                    "weight": 10.0
                })
            
            # 7. '@' symbol (CRITICAL: +50 points)
            if '@' in url:
                score += 50.0
                reasons.append("🚨 URL contains '@' symbol - CRITICAL THREAT")
                evidence.append({
                    "indicator": "Credential Harvesting Attempt (CRITICAL)",
                    "evidence": "@ symbol in URL",
                    "reason": "@ symbol redirects to different domain - common phishing technique",
                    "weight": 50.0
                })
            
            # 8. HTTP (not HTTPS) with sensitive keywords (+15 points)
            if parsed.scheme == 'http' and any(k in url.lower() for k in ['login', 'signin', 'account', 'verify']):
                score += 15.0
                reasons.append("🔓 Unencrypted connection for sensitive action")
                evidence.append({
                    "indicator": "Insecure Protocol",
                    "evidence": "HTTP used for credential-related page",
                    "reason": "Legitimate sites use HTTPS for login/account pages",
                    "weight": 15.0
                })

        except Exception as e:
            logger.error(f"URL analysis error: {e}")
            pass

        # Clamp to 0-100 range
        score = min(score, 100.0)
        
        logger.info(f"URL Analysis: {url} -> Score: {score:.1f} ({len(evidence)} threats detected)")
        
        return {
            "score": float(score),
            "reasons": reasons,
            "evidence": evidence
        }

