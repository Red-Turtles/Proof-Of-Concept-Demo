# 🐢 Turtle Species Identification App

A simple proof-of-concept web app that uses AI to identify turtle species from uploaded images.

## Features

- Upload turtle images (PNG, JPG, JPEG, GIF, BMP, WEBP)
- AI-powered species identification using:
  - OpenAI GPT-4 Vision
  - Google Gemini Vision
- Clean, simple web interface
- Automatic file cleanup

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env and add your API keys
   ```

3. **Run the app:**
   ```bash
   python app.py
   ```

4. **Open your browser:**
   ```
   http://localhost:3000
   ```

## API Keys Required

- **OpenAI API Key** (for GPT-4 Vision)
- **Google Gemini API Key** (for Gemini Vision)

Get your keys from:
- OpenAI: https://platform.openai.com/api-keys
- Google AI Studio: https://aistudio.google.com/app/apikey

## Usage

1. Upload an image of a turtle
2. Choose your preferred AI service (OpenAI or Gemini)
3. Click "Identify Species"
4. View the AI's analysis including:
   - Scientific name
   - Common name
   - Confidence level
   - Key identifying features

## File Structure

```
Proof-Of-Concept-Demo/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html         # Web interface
├── uploads/               # Temporary file storage
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── .env                  # Your API keys (create this)
└── README.md             # This file
```

## Requirements

- Python 3.8+
- Flask
- Pillow (PIL)
- Requests
- Flask-CORS
- python-dotenv

## Notes

- Images are automatically deleted after processing
- Maximum file size: 16MB
- Supported formats: PNG, JPG, JPEG, GIF, BMP, WEBP
- The app runs on port 3000 by default