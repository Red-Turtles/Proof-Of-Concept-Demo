# 🐾 Animal Species Identification App

A simple proof-of-concept web app that uses AI to identify animal species from uploaded images.

## Features

- 🐾 **AI-Powered Identification**: Upload animal images (PNG, JPG, JPEG, GIF, BMP, WEBP) and get species identification using Together.ai's Qwen2.5-VL Vision model
- 🔒 **Advanced Security**: CAPTCHA system, rate limiting (2 requests before verification), and browser trust tracking
- 🌍 **Interactive Habitat Map**: Global distribution visualization of identified species
- 🎨 **Modern UI**: Clean, responsive web interface with dark theme and yellow header
- 🔐 **Secure File Handling**: Automatic file cleanup, secure temporary file processing, and randomized filenames
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices

## Quick Start

### Option 1: Docker (Recommended)

1. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env and add your TOGETHER_API_KEY
   ```

2. **Run with Docker Compose:**
   ```bash
   # Production
   docker-compose up -d
   
   # Development (with live reload)
   docker-compose -f docker-compose.dev.yml up
   ```

3. **Open your browser:**
   ```
   http://localhost:3000
   ```

### Option 2: Local Python

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

- **Together.ai API Key** (for Qwen2.5-VL Vision model)

Get your key from:
- Together.ai: https://api.together.xyz/settings/api-keys

## Usage

1. Upload an image of any animal
2. Click "Identify" to analyze with Together.ai
3. View the AI's analysis including:
   - Is Animal (Yes/No)
   - Scientific name
   - Common name
   - Confidence level (High/Medium/Low with visual indicators)
   - Image preview

## File Structure

```
Proof-Of-Concept-Demo/
├── app.py                 # Main Flask application
├── security.py            # Security and CAPTCHA system
├── templates/
│   ├── index.html         # Main upload interface
│   ├── results.html       # Results display page
│   └── map.html          # Interactive habitat map
├── static/
│   ├── css/
│   │   └── style.css      # Styling (dark theme with yellow accents)
│   └── test_captcha.html  # CAPTCHA testing page
├── uploads/               # Temporary file storage
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── test_security.py      # Security feature testing
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

## Docker Deployment

### Production Deployment
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Development with Live Reload
```bash
# Run with volume mounting for development
docker-compose -f docker-compose.dev.yml up
```

### Docker Commands
```bash
# Build image
docker build -t animal-identifier .

# Run container
docker run -p 3000:3000 -e TOGETHER_API_KEY=your_key_here animal-identifier

# Run with environment file
docker run -p 3000:3000 --env-file .env animal-identifier
```

## Security Features

### CAPTCHA System
- **Rate Limiting**: After a configurable number of identifications (default 2), users must complete a CAPTCHA challenge
- **Session Trust**: Successful CAPTCHA completion marks the session as trusted until it expires or the browser clears cookies
- **Math CAPTCHA**: Simple arithmetic challenges for accessibility

### Advanced Security
- **Browser Fingerprinting**: Unique identification based on browser characteristics
- **Session-aware Rate Limiting**: Prevents abuse within the same browser session while remaining user friendly
- **Session Management**: Secure session handling with configurable timeouts and SameSite/Secure cookies
- **Security Headers**: Comprehensive security headers with per-request script nonces to mitigate XSS


## Technical Details

- **AI Model**: Qwen2.5-VL-72B-Instruct via Together.ai
- **Security**: CAPTCHA system, rate limiting, browser fingerprinting, secure file handling
- **File Handling**: Images are automatically deleted after processing with randomized filenames
- **Maximum file size**: 16MB
- **Supported formats**: PNG, JPG, JPEG, GIF, BMP, WEBP
- **Port**: Runs on port 3000 by default (configurable via PORT environment variable)
- **Styling**: Modern dark theme with yellow header and slate background
- **Container**: Multi-stage Docker build with health checks
- **Session Storage**: File-based sessions with secure cookie configuration

## Security Configuration

### Environment Variables
```env
# Security Settings
SECRET_KEY=your-super-secret-key-change-in-production
SECURITY_RATE_LIMIT_WINDOW_SECONDS=600   # Window before counters reset (default 10 minutes)
SECURITY_RATE_LIMIT_THRESHOLD=2          # Identifications allowed before CAPTCHA is required
SECURITY_CAPTCHA_TTL_SECONDS=300         # CAPTCHA validity window (default 5 minutes)
SECURITY_CAPTCHA_MAX_ATTEMPTS=3          # Attempts allowed before forcing a new challenge
```

### Security Endpoints
- `GET /api/security/status` - Get current security status
- `POST /api/security/captcha` - Generate CAPTCHA challenge
- `POST /api/security/verify` - Verify CAPTCHA answer
