"""
Main abuse detection engine with ensemble approach
"""

import asyncio
import re
from typing import List, Dict, Tuple, Optional
import structlog

from .models import DetectionRequest, DetectionResponse, DecisionType, LabelType, Highlight
from .language_detector import LanguageDetector
from .config import Settings

logger = structlog.get_logger()

class AbuseDetector:
    """Main ensemble detector combining ML, lexicon, and context analysis"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.language_detector = LanguageDetector()
        self.text_normalizer = TextNormalizer()
        self.ml_classifier = MLClassifier(settings)
        self.lexicon_detector = LexiconDetector(settings)
        self.context_analyzer = ContextAnalyzer()
        
    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing abuse detector components")
        
        await asyncio.gather(
            self.ml_classifier.initialize(),
            self.lexicon_detector.initialize(),
            self.language_detector.initialize()
        )
        
        logger.info("All detector components initialized")
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.ml_classifier.cleanup()
    
    async def detect(self, request: DetectionRequest) -> DetectionResponse:
        """
        Main detection method using ensemble approach
        
        Args:
            request: Detection request
            
        Returns:
            DetectionResponse with analysis results
        """
        # Step 1: Normalize text
        normalized_text = self.text_normalizer.normalize(request.text)
        
        # Step 2: Detect languages
        if request.languages:
            detected_languages = request.languages
        else:
            detected_languages = await self.language_detector.detect(normalized_text)
        
        # Step 3: Run ensemble detection
        ml_result = await self.ml_classifier.predict(normalized_text, detected_languages)
        lexicon_result = await self.lexicon_detector.detect(normalized_text, detected_languages)
        context_result = self.context_analyzer.analyze(normalized_text, ml_result, lexicon_result)
        
        # Step 4: Combine results
        final_result = self._combine_results(
            request, normalized_text, detected_languages,
            ml_result, lexicon_result, context_result
        )
        
        return final_result
    
    def _combine_results(
        self,
        request: DetectionRequest,
        text: str,
        languages: List[str],
        ml_result: Dict,
        lexicon_result: Dict,
        context_result: Dict
    ) -> DetectionResponse:
        """Combine results from all detection methods"""
        
        # Calculate weighted severity score
        ml_weight = 0.6
        lexicon_weight = 0.3
        context_weight = 0.1
        
        severity_score = (
            ml_result["severity"] * ml_weight +
            lexicon_result["severity"] * lexicon_weight +
            context_result["severity"] * context_weight
        )
        
        # Apply context adjustments
        severity_score = context_result.get("adjusted_severity", severity_score)
        
        # Determine decision
        decision = self._make_decision(severity_score, request.threshold or self.settings.default_threshold)
        
        # Combine labels
        labels = list(set(
            ml_result.get("labels", []) +
            lexicon_result.get("labels", []) +
            context_result.get("labels", [])
        ))
        
        if not labels or severity_score < 0.1:
            labels = [LabelType.CLEAN]
        
        # Combine highlights
        highlights = []
        if request.include_highlights:
            highlights.extend(lexicon_result.get("highlights", []))
            highlights.extend(ml_result.get("highlights", []))
        
        # Calculate confidence
        confidence = min(
            ml_result.get("confidence", 0.5),
            lexicon_result.get("confidence", 0.5)
        )
        
        return DetectionResponse(
            severity_score=min(1.0, max(0.0, severity_score)),
            decision=decision,
            detected_languages=languages,
            labels=labels,
            highlights=highlights,
            confidence=confidence
        )
    
    def _make_decision(self, severity: float, threshold: float) -> DecisionType:
        """Make final decision based on severity and thresholds"""
        if severity >= self.settings.block_threshold:
            return DecisionType.BLOCK
        elif severity >= threshold:
            return DecisionType.FLAG
        else:
            return DecisionType.ALLOW


class MLClassifier:
    """ML-based toxicity classifier using transformers"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = None
        self.tokenizer = None
    
    async def initialize(self):
        """Initialize ML model"""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            
            logger.info("Loading ML toxicity model", model=self.settings.model_name)
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.settings.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.settings.model_name)
            
            if torch.cuda.is_available() and self.settings.device == "cuda":
                self.model = self.model.cuda()
            
            logger.info("ML model loaded successfully")
            
        except Exception as e:
            logger.error("Failed to load ML model", error=str(e))
            # Fallback to dummy classifier
            self.model = None
            self.tokenizer = None
    
    async def cleanup(self):
        """Cleanup model resources"""
        self.model = None
        self.tokenizer = None
    
    async def predict(self, text: str, languages: List[str]) -> Dict:
        """Predict toxicity using ML model"""
        if not self.model or not self.tokenizer:
            # Fallback prediction
            return {
                "severity": 0.1,
                "confidence": 0.3,
                "labels": [],
                "highlights": []
            }
        
        try:
            import torch
            
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            if torch.cuda.is_available() and self.settings.device == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Get prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=-1)
                
            # Extract toxicity score (assuming binary classification)
            toxicity_score = probabilities[0][1].item()  # Toxic class probability
            
            labels = []
            if toxicity_score > 0.7:
                labels.append(LabelType.HATE_SPEECH)
            elif toxicity_score > 0.5:
                labels.append(LabelType.HARASSMENT)
            
            return {
                "severity": toxicity_score,
                "confidence": max(probabilities[0]).item(),
                "labels": labels,
                "highlights": []  # Would need attention weights for highlights
            }
            
        except Exception as e:
            logger.error("ML prediction failed", error=str(e))
            return {
                "severity": 0.1,
                "confidence": 0.3,
                "labels": [],
                "highlights": []
            }


class LexiconDetector:
    """Lexicon-based detection using curated word lists"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.lexicons = {}
        
    async def initialize(self):
        """Initialize lexicons for all supported languages"""
        logger.info("Initializing lexicon detector")
        
        # Sample lexicons - in production, load from files
        self.lexicons = {
            'en': {
                'profanity': ['damn', 'hell', 'shit', 'fuck', 'bitch', 'asshole'],
                'hate_speech': ['hate', 'kill', 'die', 'terrorist', 'nazi'],
                'harassment': ['stupid', 'idiot', 'loser', 'ugly', 'fat']
            },
            'hi': {
                'profanity': ['बकवास', 'गंदा', 'भड़वा', 'रंडी'],
                'hate_speech': ['मार', 'मरना', 'घृणा', 'आतंकवादी'],
                'harassment': ['बेवकूफ', 'मूर्ख', 'गधा']
            },
            'bn': {
                'profanity': ['বাজে', 'খারাপ', 'গন্দা'],
                'hate_speech': ['মার', 'মরা', 'ঘৃণা'],
                'harassment': ['বোকা', 'মূর্খ']
            }
            # Add more languages as needed
        }
        
        logger.info("Lexicon detector initialized")
    
    async def detect(self, text: str, languages: List[str]) -> Dict:
        """Detect abuse using lexicon matching"""
        highlights = []
        labels = set()
        max_severity = 0.0
        
        text_lower = text.lower()
        
        for lang in languages:
            if lang not in self.lexicons:
                continue
                
            for category, words in self.lexicons[lang].items():
                for word in words:
                    word_lower = word.lower()
                    
                    # Find all occurrences
                    start = 0
                    while True:
                        pos = text_lower.find(word_lower, start)
                        if pos == -1:
                            break
                        
                        # Check word boundaries for better matching
                        if self._is_word_boundary(text_lower, pos, len(word_lower)):
                            severity = self._get_severity_for_category(category)
                            max_severity = max(max_severity, severity)
                            
                            highlights.append(Highlight(
                                start=pos,
                                end=pos + len(word),
                                severity=severity,
                                type=LabelType(category),
                                matched_term=word
                            ))
                            
                            labels.add(LabelType(category))
                        
                        start = pos + 1
        
        return {
            "severity": max_severity,
            "confidence": 0.9 if highlights else 0.1,
            "labels": list(labels),
            "highlights": highlights
        }
    
    def _is_word_boundary(self, text: str, pos: int, length: int) -> bool:
        """Check if the match is at word boundaries"""
        import string
        
        # Check character before
        if pos > 0 and text[pos - 1] not in string.whitespace + string.punctuation:
            return False
        
        # Check character after
        if pos + length < len(text) and text[pos + length] not in string.whitespace + string.punctuation:
            return False
        
        return True
    
    def _get_severity_for_category(self, category: str) -> float:
        """Get severity score for lexicon category"""
        severity_map = {
            'profanity': 0.6,
            'hate_speech': 0.9,
            'harassment': 0.7,
            'threat': 0.95,
            'sexual_content': 0.8
        }
        return severity_map.get(category, 0.5)


class ContextAnalyzer:
    """Analyzes context to adjust detection results"""
    
    def __init__(self):
        # Negation patterns
        self.negation_patterns = [
            re.compile(r'\b(not|no|never|don\'t|doesn\'t|won\'t|can\'t)\s+', re.IGNORECASE),
            re.compile(r'\b(नहीं|ना|मत)\s+', re.IGNORECASE),  # Hindi negation
        ]
        
        # Quote patterns
        self.quote_patterns = [
            re.compile(r'["\']([^"\']*)["\']'),
            re.compile(r'[\u201c\u201d]([^\u201c\u201d]*)[\u201c\u201d]'),  # Smart quotes
        ]
        
        # Self-reference patterns
        self.self_ref_patterns = [
            re.compile(r'\b(i am|i\'m|myself|my own)\b', re.IGNORECASE),
            re.compile(r'\b(मैं|मेरा|खुद)\b', re.IGNORECASE),  # Hindi self-reference
        ]
    
    def analyze(self, text: str, ml_result: Dict, lexicon_result: Dict) -> Dict:
        """Analyze context and adjust results"""
        
        base_severity = max(ml_result.get("severity", 0), lexicon_result.get("severity", 0))
        adjusted_severity = base_severity
        context_labels = []
        
        # Check for negation
        if self._has_negation(text):
            adjusted_severity *= 0.3  # Reduce severity for negated statements
            
        # Check for quotes (reporting speech)
        if self._has_quotes(text):
            adjusted_severity *= 0.5  # Reduce severity for quoted content
            
        # Check for self-reference
        if self._has_self_reference(text):
            adjusted_severity *= 0.7  # Slightly reduce for self-directed content
        
        # Check for question format
        if text.strip().endswith('?'):
            adjusted_severity *= 0.8  # Questions are often less severe
        
        return {
            "severity": adjusted_severity,
            "adjusted_severity": adjusted_severity,
            "labels": context_labels
        }
    
    def _has_negation(self, text: str) -> bool:
        """Check if text contains negation"""
        return any(pattern.search(text) for pattern in self.negation_patterns)
    
    def _has_quotes(self, text: str) -> bool:
        """Check if text contains quoted content"""
        return any(pattern.search(text) for pattern in self.quote_patterns)
    
    def _has_self_reference(self, text: str) -> bool:
        """Check if text contains self-reference"""
        return any(pattern.search(text) for pattern in self.self_ref_patterns)


class TextNormalizer:
    """Normalizes text for consistent processing"""
    
    def __init__(self):
        # Common text substitutions
        self.substitutions = [
            (re.compile(r'[0-9]+'), ' NUM '),  # Replace numbers
            (re.compile(r'https?://\S+'), ' URL '),  # Replace URLs
            (re.compile(r'@\w+'), ' MENTION '),  # Replace mentions
            (re.compile(r'#\w+'), ' HASHTAG '),  # Replace hashtags
            (re.compile(r'\s+'), ' '),  # Normalize whitespace
        ]
    
    def normalize(self, text: str) -> str:
        """Normalize input text"""
        normalized = text.strip()
        
        # Apply substitutions
        for pattern, replacement in self.substitutions:
            normalized = pattern.sub(replacement, normalized)
        
        return normalized.strip()