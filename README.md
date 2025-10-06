# 🐢 Turtle Species Identification App

A simple proof-of-concept web app that uses AI to identify turtle species from uploaded images.

## Features

- 🐢 **AI-Powered Identification**: Upload turtle images (PNG, JPG, JPEG, GIF, BMP, WEBP) and get species identification using Together.ai's Qwen2.5-VL Vision model
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

1. Upload an image of a turtle
2. Click "Identify" to analyze with Together.ai
3. View the AI's analysis including:
   - Is Turtle (Yes/No)
   - Scientific name
   - Common name
   - Confidence level (High/Medium/Low with visual indicators)
   - Image preview

## File Structure

```
Proof-Of-Concept-Demo/
├── app.py                 # Main Flask application
├── templates/
│   ├── index.html         # Main upload interface
│   └── results.html       # Results display page
├── static/
│   └── css/
│       └── style.css      # Styling (yellow header theme)
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
docker build -t turtle-identifier .

# Run container
docker run -p 3000:3000 -e TOGETHER_API_KEY=your_key_here turtle-identifier

# Run with environment file
docker run -p 3000:3000 --env-file .env turtle-identifier
```

## Security Features

### CAPTCHA System
- **Rate Limiting**: After 2 image identifications, users must complete a CAPTCHA challenge
- **Browser Trust**: Successful CAPTCHA completion marks the browser as trusted for 30 days
- **Math CAPTCHA**: Simple arithmetic problems for accessibility

### Advanced Security
- **Browser Fingerprinting**: Unique identification based on browser characteristics
- **IP-based Rate Limiting**: Prevents abuse from single IP addresses
- **Session Management**: Secure session handling with configurable timeouts
- **Security Headers**: Comprehensive security headers for XSS, clickjacking, and content type protection


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
RATE_LIMIT_WINDOW=3600  # 1 hour in seconds
MAX_REQUESTS_PER_WINDOW=2  # Max requests before CAPTCHA
CAPTCHA_TIMEOUT=300  # 5 minutes
BROWSER_TRUST_DURATION=2592000  # 30 days in seconds
```

### Security Endpoints
- `GET /api/security/status` - Get current security status
- `POST /api/security/captcha` - Generate CAPTCHA challenge
- `POST /api/security/verify` - Verify CAPTCHA answer
