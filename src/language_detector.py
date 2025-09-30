"""
Language detection for multilingual text
"""

import re
from typing import List, Dict
from langdetect import detect_langs, LangDetectException
import structlog

logger = structlog.get_logger()

class LanguageDetector:
    """Detects languages in multilingual text"""
    
    def __init__(self):
        # Script patterns for Indian languages
        self.script_patterns = {
            'hi': re.compile(r'[\u0900-\u097F]+'),  # Devanagari
            'bn': re.compile(r'[\u0980-\u09FF]+'),  # Bengali
            'ta': re.compile(r'[\u0B80-\u0BFF]+'),  # Tamil
            'te': re.compile(r'[\u0C00-\u0C7F]+'),  # Telugu
            'kn': re.compile(r'[\u0C80-\u0CFF]+'),  # Kannada
            'ml': re.compile(r'[\u0D00-\u0D7F]+'),  # Malayalam
            'gu': re.compile(r'[\u0A80-\u0AFF]+'),  # Gujarati
            'pa': re.compile(r'[\u0A00-\u0A7F]+'),  # Gurmukhi (Punjabi)
            'or': re.compile(r'[\u0B00-\u0B7F]+'),  # Odia
            'ur': re.compile(r'[\u0600-\u06FF]+'),  # Arabic script (Urdu)
        }
        
        # Common romanized patterns
        self.romanized_patterns = {
            'hi': re.compile(r'\b(hai|hain|kya|aur|main|tum|yeh|woh|kaise|kahan)\b', re.IGNORECASE),
            'ur': re.compile(r'\b(aap|hum|yeh|woh|kaise|kahan|kyun|jab)\b', re.IGNORECASE),
        }
    
    async def initialize(self):
        """Initialize language detector"""
        logger.info("Language detector initialized")
    
    async def detect(self, text: str) -> List[str]:
        """
        Detect languages in text
        
        Args:
            text: Input text
            
        Returns:
            List of detected language codes
        """
        detected_langs = []
        
        # Check for script-based detection
        for lang_code, pattern in self.script_patterns.items():
            if pattern.search(text):
                detected_langs.append(lang_code)
        
        # Check for romanized text
        for lang_code, pattern in self.romanized_patterns.items():
            if pattern.search(text) and lang_code not in detected_langs:
                detected_langs.append(lang_code)
        
        # Use langdetect for additional detection
        try:
            lang_probs = detect_langs(text)
            for lang_prob in lang_probs[:2]:  # Top 2 languages
                if lang_prob.prob > 0.3 and lang_prob.lang not in detected_langs:
                    detected_langs.append(lang_prob.lang)
        except LangDetectException:
            pass
        
        # Default to English if no languages detected
        if not detected_langs:
            detected_langs = ['en']
        
        # Ensure English is included if Latin script is present
        if re.search(r'[a-zA-Z]+', text) and 'en' not in detected_langs:
            detected_langs.append('en')
        
        return detected_langs[:3]  # Limit to top 3 languages