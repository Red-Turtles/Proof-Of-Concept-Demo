#!/usr/bin/env python3
"""
Turtle Species Identification App
Startup script for the Flask application
"""

import os
import sys
from app import app

if __name__ == '__main__':
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found!")
        print("   Please copy env.example to .env and add your API keys.")
        print("   Example: cp env.example .env")
        print()
    
    # Check for API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if not openai_key and not gemini_key:
        print("⚠️  Warning: No API keys found!")
        print("   Please add at least one API key to your .env file:")
        print("   - OPENAI_API_KEY for OpenAI GPT-4 Vision (recommended)")
        print("   - GEMINI_API_KEY for Google Gemini Vision")
        print()
    
    print("🐢 Starting Turtle Species Identification App...")
    print("   Open your browser to: http://localhost:8080")
    print("   Press Ctrl+C to stop the server")
    print()
    
    try:
        app.run(debug=True, host='0.0.0.0', port=8080)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
