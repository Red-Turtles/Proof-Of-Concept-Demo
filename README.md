# 🐢 Turtle Species Identification App

A simple proof-of-concept web app that uses AI to identify turtle species from uploaded images.

## Features

- Upload turtle images (PNG, JPG, JPEG, GIF, BMP, WEBP)
- AI-powered species identification using Together.ai's Qwen2.5-VL Vision model
- Clean, modern web interface with yellow header theme
- Automatic file cleanup and security features
- Real-time image preview with results

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
# Build secure image for DigitalOcean (AMD64)
docker buildx build --platform linux/amd64 -t turtle-identifier:latest .

# Build and push for DigitalOcean
docker buildx build --platform linux/amd64 -t turtle-identifier:latest .
docker tag turtle-identifier:latest your-registry/turtle-identifier:latest
docker push your-registry/turtle-identifier:latest

# Run container locally
docker run -p 3000:3000 -e TOGETHER_API_KEY=your_key_here turtle-identifier:latest

# Run with environment file
docker run -p 3000:3000 --env-file .env turtle-identifier:latest
```

### DigitalOcean Deployment
```bash
# Build secure image for DigitalOcean platform
docker buildx build --platform linux/amd64 -t turtle-identifier:latest .

# Tag for your registry
docker tag turtle-identifier:latest registry.digitalocean.com/your-app/turtle-identifier:latest

# Push to DigitalOcean Container Registry
docker push registry.digitalocean.com/your-app/turtle-identifier:latest
```

## Security Features

- **Zero critical/high vulnerabilities**: All Python packages updated to latest secure versions
- **Single-stage secure build**: Eliminates vulnerable layer copying from builder stage
- **Non-root user**: Runs as `appuser` (UID 1001) for security
- **Production-only dependencies**: Uses `requirements-prod.txt` with minimal packages
- **Pinned dependencies**: All packages have specific versions to prevent supply chain attacks
- **Minimal base image**: Uses Python slim image with only necessary runtime dependencies
- **Secure file handling**: Randomized filenames, automatic cleanup, input validation
- **Security headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
- **No secrets in image**: Environment variables and secrets excluded from build
- **Health checks**: Container monitoring and automatic restart on failure
- **Vulnerability scanning**: Automated security checks with Trivy and Docker Scout

## Security Scanning

```bash
# Run security scan
./security-scan.sh

# Manual security checks
docker scout cves turtle-identifier
trivy image turtle-identifier
```

## Technical Details

- **AI Model**: Qwen2.5-VL-72B-Instruct via Together.ai
- **Security**: Randomized filenames, secure file handling, non-root user in container
- **File Handling**: Images are automatically deleted after processing
- **Maximum file size**: 16MB
- **Supported formats**: PNG, JPG, JPEG, GIF, BMP, WEBP
- **Port**: Runs on port 3000 by default (configurable via PORT environment variable)
- **Styling**: Modern dark theme with yellow header and slate background
- **Container**: Multi-stage Docker build with health checks