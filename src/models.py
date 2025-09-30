"""
Pydantic models for API requests and responses
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class DecisionType(str, Enum):
    ALLOW = "allow"
    FLAG = "flag"
    BLOCK = "block"

class LabelType(str, Enum):
    HATE_SPEECH = "hate_speech"
    PROFANITY = "profanity"
    HARASSMENT = "harassment"
    THREAT = "threat"
    SEXUAL_CONTENT = "sexual_content"
    SPAM = "spam"
    CLEAN = "clean"

class Highlight(BaseModel):
    """Represents a highlighted span in the text"""
    start: int = Field(..., description="Start position of the span")
    end: int = Field(..., description="End position of the span")
    severity: float = Field(..., ge=0, le=1, description="Severity score for this span")
    type: LabelType = Field(..., description="Type of abuse detected")
    matched_term: Optional[str] = Field(None, description="The specific term that matched")

class DetectionRequest(BaseModel):
    """Request model for abuse detection"""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to analyze")
    languages: Optional[List[str]] = Field(
        None, 
        description="Expected languages (ISO codes). If not provided, auto-detected"
    )
    threshold: Optional[float] = Field(
        0.5, 
        ge=0, 
        le=1, 
        description="Severity threshold for flagging content"
    )
    include_highlights: bool = Field(True, description="Whether to include span highlights")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for detection")

class DetectionResponse(BaseModel):
    """Response model for abuse detection"""
    severity_score: float = Field(..., ge=0, le=1, description="Overall severity score")
    decision: DecisionType = Field(..., description="Recommended action")
    detected_languages: List[str] = Field(..., description="Detected language codes")
    labels: List[LabelType] = Field(..., description="Types of abuse detected")
    highlights: List[Highlight] = Field(default_factory=list, description="Highlighted problematic spans")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in the detection")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    
    class Config:
        json_encoders = {
            DecisionType: lambda v: v.value,
            LabelType: lambda v: v.value
        }