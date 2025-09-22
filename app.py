"""
Turtle Species Identification App
A simple Flask app that uses AI to identify turtle species from uploaded images.
"""

import os
import requests
import base64
import json
import uuid
import tempfile
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Utility Functions
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_secure_temp_file(file):
    """Create a secure temporary file with randomized name"""
    try:
        # Generate a unique filename with UUID
        file_extension = secure_filename(file.filename).rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Create temporary file in system temp directory
        temp_fd, temp_path = tempfile.mkstemp(suffix=f".{file_extension}", prefix="turtle_")
        
        # Save file content to temporary file
        file.seek(0)  # Reset file pointer
        with os.fdopen(temp_fd, 'wb') as temp_file:
            temp_file.write(file.read())
        
        logger.info(f"Created secure temporary file: {temp_path}")
        return temp_path, unique_filename
        
    except Exception as e:
        logger.error(f"Error creating secure temp file: {str(e)}")
        raise Exception("Failed to process uploaded file")

def cleanup_temp_file(file_path):
    """Safely remove temporary file"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            logger.info(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up temp file {file_path}: {str(e)}")

def get_secure_filename(filename):
    """Get a secure filename for upload"""
    return secure_filename(filename)

def encode_image_to_base64(image_path):
    """Convert image to base64 string for API calls"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def validate_image(image_path):
    """Validate that the file is a valid image"""
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def identify_turtle_species_openai(image_path):
    """Use OpenAI GPT-4 Vision to identify turtle species"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("OpenAI API key not configured")
            return {"error": "Service temporarily unavailable"}
        
        base64_image = encode_image_to_base64(image_path)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Please identify the species of turtle in this image. 
                            Provide the scientific name, common name, and a brief description of key identifying features. 
                            If this is not a turtle or if you cannot clearly identify the species, please state that clearly.
                            Format your response as JSON with the following structure:
                            {
                                "is_turtle": true/false,
                                "species": "scientific name",
                                "common_name": "common name",
                                "confidence": "high/medium/low",
                                "description": "key identifying features",
                                "notes": "any additional notes"
                            }"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 500
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", 
                               headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            logger.info("OpenAI API call successful")
            
            # Try to parse as JSON, fallback to text if not valid JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                logger.warning("OpenAI response not in expected JSON format")
                return {
                    "is_turtle": True,
                    "species": "Unknown",
                    "common_name": "Unknown",
                    "confidence": "low",
                    "description": content,
                    "notes": "Response was not in expected JSON format"
                }
        else:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return {"error": "Service temporarily unavailable"}
            
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        return {"error": "Service temporarily unavailable"}

def identify_turtle_species_together_ai(image_path):
    """Use Together.ai to identify turtle species"""
    try:
        api_key = os.getenv('TOGETHER_API_KEY')
        if not api_key:
            logger.error("Together.ai API key not configured")
            return {"error": "Service temporarily unavailable"}
        
        base64_image = encode_image_to_base64(image_path)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "Qwen/Qwen2.5-VL-72B-Instruct",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Please identify the species of turtle in this image. 
                            Provide the scientific name, common name, and a brief description of key identifying features. 
                            If this is not a turtle or if you cannot clearly identify the species, please state that clearly.
                            
                            IMPORTANT: Format your response as valid JSON with the following exact structure:
                            {
                                "is_turtle": true/false,
                                "species": "scientific name or Unknown",
                                "common_name": "common name or Unknown", 
                                "confidence": "high/medium/low",
                                "description": "key identifying features",
                                "notes": "any additional notes"
                            }
                            
                            Make sure to use double quotes and valid JSON syntax."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 500,
            "temperature": 0.1
        }
        
        response = requests.post("https://api.together.xyz/v1/chat/completions", 
                               headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            logger.info("Together.ai API call successful")
            
            # Try to parse as JSON, handle markdown code blocks
            try:
                # Clean up the response if it has markdown formatting
                clean_content = content
                if content.strip().startswith('```'):
                    # Remove markdown code blocks
                    lines = content.strip().split('\n')
                    json_lines = []
                    in_json = False
                    for line in lines:
                        if line.strip().startswith('```'):
                            in_json = not in_json
                            continue
                        if in_json:
                            json_lines.append(line)
                    clean_content = '\n'.join(json_lines)
                
                result = json.loads(clean_content)
                logger.info("Together.ai JSON parsing successful")
                return result
            except json.JSONDecodeError as e:
                logger.warning(f"Together.ai response not in expected JSON format: {str(e)}")
                logger.warning(f"Raw response: {content[:200]}...")
                return {
                    "is_turtle": True,
                    "species": "Unknown",
                    "common_name": "Unknown",
                    "confidence": "low",
                    "description": content,
                    "notes": "Response was not in expected JSON format"
                }
        else:
            logger.error(f"Together.ai API error: {response.status_code} - {response.text}")
            return {"error": "Service temporarily unavailable"}
            
    except Exception as e:
        logger.error(f"Error calling Together.ai API: {str(e)}")
        return {"error": "Service temporarily unavailable"}

# Routes
@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/identify', methods=['POST'])
def upload_file():
    """Handle file upload and species identification"""
    temp_file_path = None
    try:
        # Check if file is present
        if 'file' not in request.files:
            logger.warning("Upload attempt without file")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            logger.warning("Upload attempt with empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            logger.warning(f"Upload attempt with disallowed file type: {file.filename}")
            return jsonify({'error': 'File type not allowed. Please upload PNG, JPG, JPEG, GIF, BMP, or WEBP'}), 400
        
        # Create secure temporary file
        try:
            temp_file_path, unique_filename = create_secure_temp_file(file)
            logger.info(f"Processing file: {unique_filename}")
        except Exception as e:
            logger.error(f"Failed to create secure temp file: {str(e)}")
            return jsonify({'error': 'Failed to process uploaded file'}), 400
        
        # Validate image
        if not validate_image(temp_file_path):
            cleanup_temp_file(temp_file_path)
            logger.warning(f"Invalid image file uploaded: {unique_filename}")
            return jsonify({'error': 'Invalid image file'}), 400
        
        # Use Together.ai for species identification
        logger.info("Using Together.ai for species identification")
        result = identify_turtle_species_together_ai(temp_file_path)
        
        # Prepare image data for display BEFORE cleaning up temp file
        image_data = None
        image_mime = None
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                with open(temp_file_path, 'rb') as img_file:
                    image_data = base64.b64encode(img_file.read()).decode('utf-8')
                    # Get actual MIME type from file extension
                    if file.filename.lower().endswith('.png'):
                        image_mime = 'image/png'
                    elif file.filename.lower().endswith('.gif'):
                        image_mime = 'image/gif'
                    elif file.filename.lower().endswith('.webp'):
                        image_mime = 'image/webp'
                    else:
                        image_mime = 'image/jpeg'  # Default to JPEG
            except Exception as e:
                logger.warning(f"Could not encode image for display: {str(e)}")
        
        # Clean up temporary file
        cleanup_temp_file(temp_file_path)
        
        logger.info(f"Successfully processed file: {unique_filename}")
        
        return render_template('results.html', 
                             result=result, 
                             image_data=image_data, 
                             image_mime=image_mime)
        
    except Exception as e:
        # Log the actual error internally
        logger.error(f"Upload error: {str(e)}")
        
        # Clean up temp file if it exists
        if temp_file_path:
            cleanup_temp_file(temp_file_path)
        
        # Return error page
        return render_template('results.html', 
                             result={'error': 'An error occurred while processing your request'})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Turtle ID API is running'})

if __name__ == '__main__':
    # Get port from environment or default to 3000
    port = int(os.getenv('PORT', 3000))
    
    print("🐢 Starting Turtle Species Identification App...")
    print(f"   Open your browser to: http://localhost:{port}")
    print("   Press Ctrl+C to stop the server")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=port)