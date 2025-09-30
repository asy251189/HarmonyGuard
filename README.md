# Multilingual Abusive Language Detection API

A production-ready API for detecting abusive language across English and major Indian languages including Hindi, Bengali, Tamil, Telugu, Kannada, Malayalam, Gujarati, Punjabi, Odia, and Urdu.

## What the API Does

The API accepts text in any script (Devanagari, Bengali, Tamil, Telugu, Kannada, Malayalam, Gujarati, Gurmukhi, Odia, Urdu, Romanized Hinglish, etc.), normalizes and detects languages, then runs an ensemble approach combining:

1. **ML Classifier**: Multilingual transformer fine-tuned for toxicity/offense detection
2. **Lexicon-based Detection**: Per-language curated slur lists and pattern matching
3. **Context Analysis**: Negation handling, quote detection, and self-reference rules

Returns a severity score (0-1), classification labels, per-span highlights, and an actionable decision (allow/flag/block).

## Features

- **Multi-script Support**: Devanagari, Bengali, Tamil, Telugu, Kannada, Malayalam, Gujarati, Gurmukhi, Odia, Urdu, and Romanized text
- **Language Detection**: Automatic detection and normalization of input text
- **Ensemble Approach**: Combines ML classifiers, lexicon-based detection, and context rules
- **Detailed Response**: Severity scores, labels, span highlights, and actionable decisions
- **Production Ready**: Docker support, monitoring, rate limiting, and comprehensive testing
- **Context Awareness**: Handles negation, quotes, self-reference, and question formats
- **Batch Processing**: Support for processing multiple texts in a single request

## Quick Start

### Local Development

```bash
# Clone and setup
git clone <repository>
cd multilingual-abuse-detector

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run the API
python app.py
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t abuse-detector .
docker run -p 8000:8000 abuse-detector
```

### Test the API

```bash
# Test with curl
curl -X POST http://localhost:8000/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "You are stupid", "threshold": 0.5}'

# Run comprehensive tests
python test_api.py
```

## API Endpoints

### POST /detect
Detect abusive content in text

**Request:**
```json
{
  "text": "Text to analyze",
  "languages": ["en", "hi"],  // Optional: expected languages
  "threshold": 0.5,           // Optional: severity threshold
  "include_highlights": true, // Optional: include span highlights
  "context": {}              // Optional: additional context
}
```

**Response:**
```json
{
  "severity_score": 0.85,
  "decision": "block",
  "detected_languages": ["hi", "en"],
  "labels": ["hate_speech", "profanity"],
  "highlights": [
    {
      "start": 10,
      "end": 15,
      "severity": 0.9,
      "type": "profanity",
      "matched_term": "stupid"
    }
  ],
  "confidence": 0.92,
  "processing_time_ms": 45
}
```

### POST /batch-detect
Process multiple texts in batch (max 100 per request)

### GET /languages
Get list of supported languages

### GET /health
Health check endpoint

## Supported Languages

| Code | Language | Script | Status |
|------|----------|--------|--------|
| en   | English  | Latin  | ✅ Full |
| hi   | Hindi    | Devanagari | ✅ Full |
| bn   | Bengali  | Bengali | ✅ Full |
| ta   | Tamil    | Tamil | ✅ Full |
| te   | Telugu   | Telugu | ✅ Full |
| kn   | Kannada  | Kannada | ✅ Full |
| ml   | Malayalam | Malayalam | ✅ Full |
| gu   | Gujarati | Gujarati | ✅ Full |
| pa   | Punjabi  | Gurmukhi | ✅ Full |
| or   | Odia     | Odia | ✅ Full |
| ur   | Urdu     | Arabic | ✅ Full |

## Decision Logic

- **Allow** (severity < 0.5): Content is safe
- **Flag** (0.5 ≤ severity < 0.8): Content needs review
- **Block** (severity ≥ 0.8): Content should be blocked

## Configuration

Environment variables (see `.env.example`):

- `ABUSE_API_MODEL_NAME`: Hugging Face model for ML classification
- `ABUSE_API_DEFAULT_THRESHOLD`: Default severity threshold
- `ABUSE_API_RATE_LIMIT_REQUESTS`: Requests per minute per IP
- `ABUSE_API_REDIS_ENABLED`: Enable Redis for caching/rate limiting

## Architecture

```
Input Text
    ↓
Text Normalization
    ↓
Language Detection
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│   ML Classifier │ Lexicon Matcher │ Context Analyzer│
│   (Transformers)│  (Word Lists)   │ (Rules Engine)  │
└─────────────────┴─────────────────┴─────────────────┘
    ↓
Ensemble Combination
    ↓
Final Decision + Highlights
```

## Performance

- **Latency**: ~50-100ms per request (CPU)
- **Throughput**: ~100 requests/second (single instance)
- **Memory**: ~2GB (with loaded ML model)
- **Accuracy**: ~85-90% across supported languages

## Production Considerations

- Use GPU for better ML model performance
- Implement proper lexicon management system
- Add monitoring and alerting
- Consider model fine-tuning for specific domains
- Implement proper logging and audit trails