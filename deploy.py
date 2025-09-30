#!/usr/bin/env python3
"""
Deployment script for the Multilingual Abuse Detection API
"""

import subprocess
import sys
import time
import requests

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return None

def check_docker():
    """Check if Docker is available"""
    result = run_command("docker --version", "Checking Docker")
    if result:
        print(f"Docker version: {result.stdout.strip()}")
        return True
    return False

def build_image():
    """Build the Docker image"""
    print("\n🏗️ Building Docker image...")
    cmd = "docker build -t abuse-detector:latest ."
    return run_command(cmd, "Building Docker image")

def deploy_container():
    """Deploy the container using docker-compose"""
    print("\n🚀 Deploying container...")
    cmd = "docker-compose up -d"
    return run_command(cmd, "Starting container")

def check_health():
    """Check if the API is healthy"""
    print("\n🏥 Checking API health...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API is healthy and ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"⏳ Waiting for API to start... ({i+1}/{max_retries})")
        time.sleep(10)
    
    print("❌ API health check failed")
    return False

def show_logs():
    """Show container logs"""
    print("\n📋 Recent container logs:")
    run_command("docker-compose logs --tail=20 abuse-detector", "Fetching logs")

def main():
    """Main deployment function"""
    print("🚀 Multilingual Abuse Detection API - Docker Deployment")
    print("=" * 60)
    
    # Check Docker
    if not check_docker():
        print("❌ Docker is not available. Please install Docker first.")
        sys.exit(1)
    
    # Build image
    if not build_image():
        print("❌ Failed to build Docker image")
        sys.exit(1)
    
    # Deploy container
    if not deploy_container():
        print("❌ Failed to deploy container")
        sys.exit(1)
    
    # Check health
    if check_health():
        print("\n🎉 Deployment successful!")
        print("\n📡 API is running at: http://localhost:8000")
        print("📖 API documentation: http://localhost:8000/docs")
        print("\n🧪 Test the API:")
        print("   curl -X POST http://localhost:8000/detect \\")
        print('     -H "Content-Type: application/json" \\')
        print('     -d \'{"text": "Hello world", "threshold": 0.5}\'')
        print("\n📋 View logs: docker-compose logs -f abuse-detector")
        print("🛑 Stop service: docker-compose down")
    else:
        print("\n❌ Deployment completed but API is not responding")
        show_logs()
        print("\n🔍 Troubleshooting:")
        print("1. Check logs: docker-compose logs abuse-detector")
        print("2. Check container status: docker-compose ps")
        print("3. Restart: docker-compose restart abuse-detector")

if __name__ == "__main__":
    main()