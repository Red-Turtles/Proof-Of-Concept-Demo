#!/usr/bin/env python3
"""
Main entry point for the Turtle Species Identification App
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import and run the Flask app
from api.app import app

if __name__ == '__main__':
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found!")
        print("   Please copy config/env.example to .env and add your API keys.")
        print("   Example: cp config/env.example .env")
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
    
    # Get port from environment or default to 3000
    port = int(os.getenv('PORT', 3000))
    
    print("🐢 Starting Turtle Species Identification App...")
    print(f"   Open your browser to: http://localhost:{port}")
    print("   Press Ctrl+C to stop the server")
    print()
    
    try:
        app.run(debug=True, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
