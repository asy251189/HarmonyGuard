"""
Test script for the Multilingual Abuse Detection API
"""

import asyncio
import httpx
import json

async def test_api():
    """Test the abuse detection API with various examples"""
    
    base_url = "http://localhost:8000"
    
    # Test cases covering different languages and abuse types
    test_cases = [
        {
            "name": "English profanity",
            "text": "You are such an idiot and stupid person",
            "expected_decision": "flag"
        },
        {
            "name": "Hindi abuse",
            "text": "तुम बहुत बेवकूफ हो",
            "expected_decision": "flag"
        },
        {
            "name": "Clean English text",
            "text": "Hello, how are you doing today?",
            "expected_decision": "allow"
        },
        {
            "name": "Mixed language",
            "text": "Hello यार, you are बेवकूफ",
            "expected_decision": "flag"
        },
        {
            "name": "Negated abuse",
            "text": "I am not stupid or an idiot",
            "expected_decision": "allow"
        },
        {
            "name": "Quoted speech",
            "text": 'He said "you are stupid" but I disagree',
            "expected_decision": "flag"
        }
    ]
    
    async with httpx.AsyncClient() as client:
        print("Testing Multilingual Abuse Detection API")
        print("=" * 50)
        
        # Test health endpoint
        try:
            response = await client.get(f"{base_url}/health")
            print(f"Health check: {response.status_code}")
            print()
        except Exception as e:
            print(f"API not available: {e}")
            return
        
        # Test supported languages
        try:
            response = await client.get(f"{base_url}/languages")
            if response.status_code == 200:
                languages = response.json()
                print("Supported languages:")
                for lang in languages["supported_languages"]:
                    print(f"  {lang['code']}: {lang['name']}")
                print()
        except Exception as e:
            print(f"Error getting languages: {e}")
        
        # Test detection endpoint
        for i, test_case in enumerate(test_cases, 1):
            print(f"Test {i}: {test_case['name']}")
            print(f"Text: {test_case['text']}")
            
            try:
                response = await client.post(
                    f"{base_url}/detect",
                    json={
                        "text": test_case["text"],
                        "include_highlights": True
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    print(f"Decision: {result['decision']}")
                    print(f"Severity: {result['severity_score']:.3f}")
                    print(f"Languages: {result['detected_languages']}")
                    print(f"Labels: {result['labels']}")
                    
                    if result['highlights']:
                        print("Highlights:")
                        for highlight in result['highlights']:
                            highlighted_text = test_case['text'][highlight['start']:highlight['end']]
                            print(f"  '{highlighted_text}' ({highlight['type']}, {highlight['severity']:.3f})")
                    
                    print(f"Processing time: {result.get('processing_time_ms', 0):.1f}ms")
                    
                    # Check if result matches expectation
                    expected = test_case['expected_decision']
                    actual = result['decision']
                    status = "✓" if actual == expected else "✗"
                    print(f"Expected: {expected}, Got: {actual} {status}")
                    
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"Request failed: {e}")
            
            print("-" * 40)
        
        # Test batch detection
        print("\nTesting batch detection:")
        batch_requests = [
            {"text": "Hello world", "threshold": 0.5},
            {"text": "You are stupid", "threshold": 0.5},
            {"text": "तुम बेवकूफ हो", "threshold": 0.5}
        ]
        
        try:
            response = await client.post(
                f"{base_url}/batch-detect",
                json=batch_requests
            )
            
            if response.status_code == 200:
                results = response.json()
                print(f"Processed {len(results)} texts in batch")
                for i, result in enumerate(results):
                    print(f"  Text {i+1}: {result['decision']} (severity: {result['severity_score']:.3f})")
            else:
                print(f"Batch error: {response.status_code}")
                
        except Exception as e:
            print(f"Batch request failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())