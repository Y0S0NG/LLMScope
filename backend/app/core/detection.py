"""PII and injection detection"""
import re
from typing import List, Dict, Any


class PIIDetector:
    """Detect personally identifiable information"""

    # Regex patterns for common PII
    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    }

    @classmethod
    def detect(cls, text: str) -> List[Dict[str, Any]]:
        """Detect PII in text"""
        detections = []
        for pii_type, pattern in cls.PATTERNS.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                detections.append({
                    "type": pii_type,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end()
                })
        return detections


class InjectionDetector:
    """Detect potential prompt injection attempts"""

    # Common injection patterns
    INJECTION_PATTERNS = [
        r"ignore\s+previous\s+instructions",
        r"ignore\s+all\s+previous",
        r"disregard\s+previous",
        r"system\s*:\s*you\s+are",
    ]

    @classmethod
    def detect(cls, text: str) -> bool:
        """Check if text contains potential injection"""
        text_lower = text.lower()
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, text_lower):
                return True
        return False
