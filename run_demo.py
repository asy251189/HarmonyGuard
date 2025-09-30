#!/usr/bin/env python3
"""
Demo script to run the Multilingual Abuse Detection API
"""

import sys
import os

def run_demo():
    """Run a quick demo of the API"""
    
    print("🚀 Multilingual Abuse Detection API Demo")
    print("=" * 50)
    
    # Check if required packages are available
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn are available")
    except ImportError as e:
        print(f"❌ Missing required packages: {e}")
        print("Please run: pip install fastapi uvicorn pydantic-settings langdetect structlog")
        return
    
    # Start the API server
    print("\n🔧 Starting API server...")
    
    try:
        # Import and run the app
        from app import app
        import uvicorn
        
        print("✅ API modules loaded successfully")
        print("\n📡 Starting server on http://localhost:8000")
        print("📖 API documentation available at http://localhost:8000/docs")
        print("\n🧪 To test the API, run in another terminal:")
        print("   python test_api.py")
        print("\n⏹️  Press Ctrl+C to stop the server")
        
        # Run the server
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed")
        print("2. Check if port 8000 is available")
        print("3. Verify Python version is 3.8+")

if __name__ == "__main__":
    run_demo()