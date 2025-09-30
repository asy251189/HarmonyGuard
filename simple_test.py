#!/usr/bin/env python3
"""
Simple test script to demonstrate the abuse detection functionality
"""

import asyncio
from src.detector import AbuseDetector
from src.models import DetectionRequest
from src.config import get_settings

async def test_detection():
    """Test the detection functionality directly"""
    
    print("🧪 Testing Multilingual Abuse Detection")
    print("=" * 50)
    
    # Initialize detector
    settings = get_settings()
    detector = AbuseDetector(settings)
    
    print("🔧 Initializing detector components...")
    await detector.initialize()
    print("✅ Detector ready!")
    
    # Test cases
    test_cases = [
        {
            "name": "Clean English text",
            "text": "Hello, how are you doing today?",
            "expected": "allow"
        },
        {
            "name": "English profanity",
            "text": "You are such an idiot and stupid person",
            "expected": "flag/block"
        },
        {
            "name": "Hindi text (clean)",
            "text": "आप कैसे हैं? आज का दिन कैसा है?",
            "expected": "allow"
        },
        {
            "name": "Hindi abuse",
            "text": "तुम बहुत बेवकूफ हो",
            "expected": "flag"
        },
        {
            "name": "Mixed language",
            "text": "Hello यार, you are बेवकूफ",
            "expected": "flag"
        },
        {
            "name": "Negated statement",
            "text": "I am not stupid or an idiot",
            "expected": "allow (context-aware)"
        }
    ]
    
    print(f"\n🔍 Running {len(test_cases)} test cases...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print(f"Text: '{test_case['text']}'")
        
        try:
            # Create request
            request = DetectionRequest(
                text=test_case["text"],
                include_highlights=True
            )
            
            # Run detection
            result = await detector.detect(request)
            
            # Display results
            print(f"✅ Decision: {result.decision}")
            print(f"   Severity: {result.severity_score:.3f}")
            print(f"   Languages: {result.detected_languages}")
            print(f"   Labels: {result.labels}")
            print(f"   Confidence: {result.confidence:.3f}")
            
            if result.highlights:
                print("   Highlights:")
                for highlight in result.highlights:
                    highlighted_text = test_case['text'][highlight.start:highlight.end]
                    print(f"     '{highlighted_text}' ({highlight.type}, severity: {highlight.severity:.3f})")
            
            print(f"   Expected: {test_case['expected']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)
    
    # Cleanup
    await detector.cleanup()
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_detection())