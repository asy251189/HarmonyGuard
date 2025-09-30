"""
Multilingual Abusive Language Detection API
Production-ready FastAPI application
"""

import time
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import structlog

from src.detector import AbuseDetector
from src.models import DetectionRequest, DetectionResponse
from src.middleware import RateLimitMiddleware, MetricsMiddleware
from src.config import get_settings

logger = structlog.get_logger()

# Global detector instance
detector: Optional[AbuseDetector] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global detector
    
    logger.info("Starting Multilingual Abuse Detection API")
    
    # Initialize detector
    settings = get_settings()
    detector = AbuseDetector(settings)
    await detector.initialize()
    
    logger.info("API ready to serve requests")
    yield
    
    # Cleanup
    if detector:
        await detector.cleanup()
    logger.info("API shutdown complete")

app = FastAPI(
    title="Multilingual Abusive Language Detection API",
    description="Production-ready API for detecting abusive content across English and Indian languages",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(MetricsMiddleware)

def get_detector() -> AbuseDetector:
    """Dependency to get detector instance"""
    if detector is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    return detector

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

@app.post("/detect", response_model=DetectionResponse)
async def detect_abuse(
    request: DetectionRequest,
    detector: AbuseDetector = Depends(get_detector)
) -> DetectionResponse:
    """
    Detect abusive language in multilingual text
    
    Args:
        request: Detection request with text and optional parameters
        
    Returns:
        DetectionResponse with severity score, decision, and highlights
    """
    start_time = time.time()
    
    try:
        result = await detector.detect(request)
        processing_time = (time.time() - start_time) * 1000
        
        result.processing_time_ms = processing_time
        
        logger.info(
            "Detection completed",
            text_length=len(request.text),
            severity=result.severity_score,
            decision=result.decision,
            processing_time_ms=processing_time
        )
        
        return result
        
    except Exception as e:
        logger.error("Detection failed", error=str(e))
        raise HTTPException(status_code=500, detail="Detection failed")

@app.post("/batch-detect")
async def batch_detect(
    requests: List[DetectionRequest],
    detector: AbuseDetector = Depends(get_detector)
) -> List[DetectionResponse]:
    """Batch detection endpoint for multiple texts"""
    if len(requests) > 100:
        raise HTTPException(status_code=400, detail="Batch size too large (max 100)")
    
    results = []
    for req in requests:
        result = await detector.detect(req)
        results.append(result)
    
    return results

@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "supported_languages": [
            {"code": "en", "name": "English"},
            {"code": "hi", "name": "Hindi"},
            {"code": "bn", "name": "Bengali"},
            {"code": "ta", "name": "Tamil"},
            {"code": "te", "name": "Telugu"},
            {"code": "kn", "name": "Kannada"},
            {"code": "ml", "name": "Malayalam"},
            {"code": "gu", "name": "Gujarati"},
            {"code": "pa", "name": "Punjabi"},
            {"code": "or", "name": "Odia"},
            {"code": "ur", "name": "Urdu"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)