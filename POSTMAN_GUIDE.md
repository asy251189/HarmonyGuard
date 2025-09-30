# Postman Testing Guide - Multilingual Abuse Detection API

This guide provides comprehensive Postman collections for testing the Multilingual Abuse Detection API across all supported languages and features.

## 📁 Files Included

- `postman_collection.json` - Complete API test collection
- `postman_environment.json` - Environment variables for local testing
- `POSTMAN_GUIDE.md` - This guide

## 🚀 Quick Setup

### 1. Import Collection & Environment

1. Open Postman
2. Click **Import** button
3. Select both files:
   - `postman_collection.json`
   - `postman_environment.json`
4. Click **Import**

### 2. Set Environment

1. Click the environment dropdown (top right)
2. Select **"Multilingual Abuse Detection - Local"**
3. Verify `base_url` is set to `http://localhost:8000`

### 3. Start API Server

```bash
# Using Docker (recommended)
docker-compose up -d

# Or locally
python run_demo.py
```

## 📋 Collection Structure

### 🏥 Health & Status
- **Health Check** - Verify API is running
- **Get Supported Languages** - List all supported languages

### 🔍 Single Text Detection
- **Clean English Text** - Test with safe content
- **English Profanity** - Test abuse detection
- **Hindi Clean Text** - Test Devanagari script
- **Hindi Abusive Text** - Test Hindi abuse detection
- **Mixed Language (Hinglish)** - Test code-switching
- **Context Aware - Negation** - Test context analysis
- **Custom Threshold Test** - Test threshold configuration

### 📦 Batch Detection
- **Batch Process Multiple Texts** - Process 5 texts simultaneously

### ⚙️ Advanced Features
- **With Language Hints** - Provide language codes
- **Without Highlights** - Faster processing option
- **With Context Information** - Additional metadata

### ❌ Error Cases
- **Empty Text** - Validation error testing
- **Invalid Threshold** - Parameter validation
- **Large Batch Request** - Batch size limits

## 🧪 Test Cases Overview

| Test Case | Input | Expected Result | Purpose |
|-----------|-------|----------------|---------|
| Clean English | "Hello, how are you doing today?" | `allow` (severity ~0.06) | Baseline positive case |
| English Profanity | "You are such an idiot and stupid person" | `flag` (severity ~0.7) | English abuse detection |
| Hindi Clean | "आप कैसे हैं? आज का दिन कैसा है?" | `allow` (severity ~0.06) | Hindi baseline |
| Hindi Abuse | "तुम बहुत बेवकूफ हो और मूर्ख भी" | `flag` (severity ~0.7) | Hindi abuse detection |
| Mixed Language | "Hello यार, you are बेवकूफ and stupid" | `flag` (severity ~0.7) | Code-switching detection |
| Negation | "I am not stupid or an idiot" | `allow` (severity ~0.15) | Context awareness |

## 📊 Response Format

All detection endpoints return:

```json
{
    "severity_score": 0.7,           // 0-1 severity rating
    "decision": "flag",              // allow/flag/block
    "detected_languages": ["en"],    // Auto-detected languages
    "labels": ["harassment"],        // Abuse categories
    "highlights": [                  // Problematic spans
        {
            "start": 8,
            "end": 14,
            "severity": 0.7,
            "type": "harassment",
            "matched_term": "stupid"
        }
    ],
    "confidence": 0.857,             // Detection confidence
    "processing_time_ms": 67.3       // Processing duration
}
```

## 🎯 Testing Scenarios

### Basic Functionality
1. Run **Health Check** - Ensure API is ready
2. Test **Clean English Text** - Verify baseline
3. Test **English Profanity** - Verify detection works
4. Test **Hindi Clean Text** - Verify multilingual support

### Language Support
1. **Hindi Abusive Text** - Test Devanagari script detection
2. **Mixed Language** - Test Hinglish code-switching
3. **With Language Hints** - Test language specification

### Advanced Features
1. **Context Aware - Negation** - Verify context analysis
2. **Custom Threshold Test** - Test threshold sensitivity
3. **Batch Process** - Test bulk processing
4. **Without Highlights** - Test performance optimization

### Error Handling
1. **Empty Text** - Verify validation
2. **Invalid Threshold** - Test parameter validation
3. **Large Batch Request** - Test limits

## 🔧 Environment Variables

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `base_url` | `http://localhost:8000` | API server URL |
| `api_version` | `1.0.0` | API version |
| `default_threshold` | `0.5` | Default severity threshold |
| `test_user_id` | `test_user_123` | Test user identifier |

## 📈 Performance Expectations

| Metric | Expected Value | Notes |
|--------|----------------|-------|
| Health Check | < 50ms | Simple status endpoint |
| Single Detection | < 200ms | Including ML processing |
| Batch Detection (5 items) | < 500ms | Parallel processing |
| Model Loading | ~2-3 minutes | One-time initialization |

## 🐛 Troubleshooting

### API Not Responding
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs abuse-detector

# Restart if needed
docker-compose restart abuse-detector
```

### Slow Response Times
- First request after startup takes longer (model loading)
- Subsequent requests should be faster
- Check Docker resource allocation

### Validation Errors
- Ensure text is not empty (min 1 character)
- Threshold must be between 0.0 and 1.0
- Batch requests limited to 100 items

## 🌍 Language Testing

### Supported Scripts
- **Latin**: English, Romanized text
- **Devanagari**: Hindi (हिंदी)
- **Bengali**: বাংলা
- **Tamil**: தமிழ்
- **Telugu**: తెలుగు
- **Kannada**: ಕನ್ನಡ
- **Malayalam**: മലയാളം
- **Gujarati**: ગુજરાતી
- **Gurmukhi**: ਪੰਜਾਬੀ (Punjabi)
- **Odia**: ଓଡ଼ିଆ
- **Arabic**: اردو (Urdu)

### Test Phrases by Language

```json
{
    "english_clean": "Hello, how are you today?",
    "english_abuse": "You are stupid and annoying",
    "hindi_clean": "आप कैसे हैं? आज का दिन कैसा है?",
    "hindi_abuse": "तुम बहुत बेवकूफ हो",
    "mixed_hinglish": "Hello यार, you are बेवकूफ",
    "bengali_clean": "আপনি কেমন আছেন?",
    "tamil_clean": "நீங்கள் எப்படி இருக்கிறீர்கள்?"
}
```

## 📝 Custom Test Creation

### Adding New Test Cases

1. Duplicate existing request
2. Modify request body:
   ```json
   {
       "text": "Your test text here",
       "threshold": 0.5,
       "include_highlights": true,
       "languages": ["hi", "en"]  // Optional
   }
   ```
3. Update description and expected results
4. Add to appropriate folder

### Testing New Languages

1. Add text in target language
2. Verify language detection in response
3. Test both clean and abusive content
4. Document expected behavior

## 🔄 Automated Testing

### Collection Runner
1. Select collection
2. Choose environment
3. Set iterations and delay
4. Run all tests automatically

### Newman CLI
```bash
# Install Newman
npm install -g newman

# Run collection
newman run postman_collection.json \
  -e postman_environment.json \
  --reporters cli,json \
  --reporter-json-export results.json
```

This comprehensive Postman collection provides everything needed to thoroughly test the Multilingual Abuse Detection API across all supported languages and features! 🚀