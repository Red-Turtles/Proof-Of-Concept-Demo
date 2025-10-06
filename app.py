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
from flask import Flask, request, jsonify, render_template, session, redirect
from flask_cors import CORS
from flask_session import Session
from PIL import Image
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from security import SecurityManager

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure secret key for sessions
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')
app.config['SESSION_FILE_THRESHOLD'] = 100

CORS(app)

# Initialize session
Session(app)

# Initialize security manager
security = SecurityManager(app)

# Security headers
@app.after_request
def add_security_headers(response):
    """Add security headers for enhanced protection"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com; style-src 'self' 'unsafe-inline' https://unpkg.com; img-src 'self' data: https://*.tile.openstreetmap.org;"
    return response

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
                            "text": """Please identify the animal species in this image. 
                            Provide the scientific name, common name, animal type (mammal, bird, reptile, amphibian, fish, invertebrate), and a brief description of key identifying features. 
                            If this is not an animal or if you cannot clearly identify the species, please state that clearly.
                            
                            IMPORTANT: Format your response as valid JSON with the following exact structure:
                            {
                                "is_animal": true/false,
                                "species": "scientific name or Unknown",
                                "common_name": "common name or Unknown",
                                "animal_type": "mammal/bird/reptile/amphibian/fish/invertebrate/unknown",
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

def get_animal_habitat_data(species_name, common_name, animal_type):
    """Get habitat and distribution data for any animal species"""
    # Comprehensive database of animals and their habitats
    animal_habitats = {
        # Mammals
        "panthera leo": {
            "name": "African Lion",
            "habitats": [
                {"name": "Serengeti, Tanzania", "lat": -2.0, "lng": 34.0, "type": "savanna"},
                {"name": "Kruger National Park, South Africa", "lat": -24.0, "lng": 31.0, "type": "savanna"},
                {"name": "Masai Mara, Kenya", "lat": -1.0, "lng": 35.0, "type": "savanna"},
                {"name": "Gir Forest, India", "lat": 21.0, "lng": 70.0, "type": "forest"}
            ],
            "description": "Found in savannas and grasslands of Africa and Asia"
        },
        "ursus arctos": {
            "name": "Brown Bear",
            "habitats": [
                {"name": "Alaska, USA", "lat": 64.0, "lng": -150.0, "type": "boreal"},
                {"name": "Kamchatka, Russia", "lat": 56.0, "lng": 159.0, "type": "boreal"},
                {"name": "Yellowstone, USA", "lat": 44.0, "lng": -110.0, "type": "temperate"},
                {"name": "Carpathian Mountains", "lat": 47.0, "lng": 25.0, "type": "temperate"}
            ],
            "description": "Widely distributed across North America, Europe, and Asia"
        },
        "elephas maximus": {
            "name": "Asian Elephant",
            "habitats": [
                {"name": "Sri Lanka", "lat": 7.0, "lng": 80.0, "type": "tropical"},
                {"name": "Thailand", "lat": 15.0, "lng": 101.0, "type": "tropical"},
                {"name": "India", "lat": 20.0, "lng": 77.0, "type": "tropical"},
                {"name": "Borneo", "lat": 1.0, "lng": 114.0, "type": "tropical"}
            ],
            "description": "Found in tropical forests and grasslands of Asia"
        },
        "canis lupus": {
            "name": "Gray Wolf",
            "habitats": [
                {"name": "Yellowstone, USA", "lat": 44.0, "lng": -110.0, "type": "temperate"},
                {"name": "Alaska, USA", "lat": 64.0, "lng": -150.0, "type": "boreal"},
                {"name": "Siberia, Russia", "lat": 60.0, "lng": 100.0, "type": "boreal"},
                {"name": "Carpathian Mountains", "lat": 47.0, "lng": 25.0, "type": "temperate"}
            ],
            "description": "Found in forests, tundra, and grasslands of North America and Eurasia"
        },
        
        # Birds
        "aquila chrysaetos": {
            "name": "Golden Eagle",
            "habitats": [
                {"name": "Rocky Mountains, USA", "lat": 40.0, "lng": -105.0, "type": "mountain"},
                {"name": "Scottish Highlands", "lat": 57.0, "lng": -4.0, "type": "mountain"},
                {"name": "Himalayas", "lat": 28.0, "lng": 84.0, "type": "mountain"},
                {"name": "Alps", "lat": 46.0, "lng": 10.0, "type": "mountain"}
            ],
            "description": "Found in mountainous regions across the Northern Hemisphere"
        },
        "aptenodytes forsteri": {
            "name": "Emperor Penguin",
            "habitats": [
                {"name": "Antarctica", "lat": -75.0, "lng": 0.0, "type": "polar"},
                {"name": "Ross Sea", "lat": -77.0, "lng": 180.0, "type": "polar"}
            ],
            "description": "Endemic to Antarctica, the southernmost breeding bird"
        },
        "turdus migratorius": {
            "name": "American Robin",
            "habitats": [
                {"name": "North America", "lat": 45.0, "lng": -100.0, "type": "temperate"},
                {"name": "Canada", "lat": 60.0, "lng": -100.0, "type": "boreal"},
                {"name": "Mexico", "lat": 23.0, "lng": -102.0, "type": "subtropical"}
            ],
            "description": "Widely distributed across North America"
        },
        
        # Reptiles
        "chelonia mydas": {
            "name": "Green Sea Turtle",
            "habitats": [
                {"name": "Caribbean Sea", "lat": 15.5, "lng": -80.0, "type": "tropical"},
                {"name": "Great Barrier Reef", "lat": -18.0, "lng": 147.0, "type": "tropical"},
                {"name": "Hawaiian Islands", "lat": 21.0, "lng": -157.0, "type": "tropical"},
                {"name": "Florida Keys", "lat": 24.5, "lng": -81.5, "type": "subtropical"}
            ],
            "description": "Found in tropical and subtropical waters worldwide"
        },
        "crocodylus niloticus": {
            "name": "Nile Crocodile",
            "habitats": [
                {"name": "Nile River, Egypt", "lat": 26.0, "lng": 31.0, "type": "tropical"},
                {"name": "Lake Victoria", "lat": -1.0, "lng": 33.0, "type": "tropical"},
                {"name": "Okavango Delta", "lat": -19.0, "lng": 23.0, "type": "tropical"},
                {"name": "Madagascar", "lat": -19.0, "lng": 47.0, "type": "tropical"}
            ],
            "description": "Found in freshwater habitats across Africa and Madagascar"
        },
        
        # Amphibians
        "rana catesbeiana": {
            "name": "American Bullfrog",
            "habitats": [
                {"name": "Eastern United States", "lat": 40.0, "lng": -75.0, "type": "temperate"},
                {"name": "Canada", "lat": 50.0, "lng": -100.0, "type": "temperate"},
                {"name": "Mexico", "lat": 23.0, "lng": -102.0, "type": "subtropical"}
            ],
            "description": "Native to eastern North America, now found worldwide"
        },
        
        # Fish
        "thunnus thynnus": {
            "name": "Atlantic Bluefin Tuna",
            "habitats": [
                {"name": "North Atlantic", "lat": 45.0, "lng": -40.0, "type": "temperate"},
                {"name": "Mediterranean Sea", "lat": 35.0, "lng": 20.0, "type": "temperate"},
                {"name": "Gulf of Mexico", "lat": 28.0, "lng": -90.0, "type": "subtropical"}
            ],
            "description": "Found in temperate and subtropical waters of the Atlantic"
        },
        "carcharodon carcharias": {
            "name": "Great White Shark",
            "habitats": [
                {"name": "California Coast", "lat": 36.0, "lng": -122.0, "type": "temperate"},
                {"name": "South Africa", "lat": -34.0, "lng": 18.0, "type": "temperate"},
                {"name": "Australia", "lat": -33.0, "lng": 151.0, "type": "temperate"},
                {"name": "Mediterranean Sea", "lat": 35.0, "lng": 20.0, "type": "temperate"}
            ],
            "description": "Found in temperate coastal waters worldwide"
        },
        
        # Invertebrates
        "apis mellifera": {
            "name": "Western Honey Bee",
            "habitats": [
                {"name": "Europe", "lat": 50.0, "lng": 10.0, "type": "temperate"},
                {"name": "North America", "lat": 40.0, "lng": -100.0, "type": "temperate"},
                {"name": "Australia", "lat": -25.0, "lng": 133.0, "type": "temperate"},
                {"name": "South America", "lat": -15.0, "lng": -60.0, "type": "tropical"}
            ],
            "description": "Found worldwide, domesticated and wild populations"
        },
        "danaus plexippus": {
            "name": "Monarch Butterfly",
            "habitats": [
                {"name": "North America", "lat": 40.0, "lng": -100.0, "type": "temperate"},
                {"name": "Mexico (winter)", "lat": 19.0, "lng": -99.0, "type": "subtropical"},
                {"name": "Canada (summer)", "lat": 50.0, "lng": -100.0, "type": "temperate"}
            ],
            "description": "Migratory butterfly found across North America"
        }
    }
    
    # Try to find by scientific name first
    species_key = species_name.lower().strip() if species_name else ""
    if species_key in animal_habitats:
        return animal_habitats[species_key]
    
    # Try to find by common name
    for key, data in animal_habitats.items():
        if common_name and common_name.lower().strip() in data["name"].lower():
            return data
    
    # Try to find by animal type if no specific match
    if animal_type:
        for key, data in animal_habitats.items():
            if animal_type.lower() in data.get("description", "").lower():
                return data
    
    # Default habitat data for unknown species
    return {
        "name": common_name or "Unknown Animal Species",
        "habitats": [
            {"name": "Global Distribution", "lat": 0.0, "lng": 0.0, "type": "unknown"}
        ],
        "description": f"Habitat information not available for this {animal_type or 'animal'} species"
    }

# Routes
@app.route('/')
def index():
    """Serve the main page"""
    security_status = security.get_security_status()
    
    # Generate CAPTCHA if rate limited
    captcha_data = None
    if security_status.get('rate_limited') and not security_status.get('is_trusted'):
        captcha_data = security.generate_captcha()
    
    return render_template('index.html', 
                         security_status=security_status,
                         captcha_data=captcha_data)

@app.route('/verify-captcha', methods=['POST'])
def verify_captcha():
    """Handle CAPTCHA verification"""
    captcha_id = request.form.get('captcha_id')
    captcha_answer = request.form.get('captcha_answer')
    
    if not captcha_id or not captcha_answer:
        return render_template('index.html', 
                             security_status=security.get_security_status(),
                             error_message='Please enter a CAPTCHA answer')
    
    if security.verify_captcha(captcha_id, captcha_answer):
        # CAPTCHA verified successfully, redirect to main page
        return redirect('/')
    else:
        # CAPTCHA failed, generate new one
        captcha_data = security.generate_captcha()
        return render_template('index.html', 
                             security_status=security.get_security_status(),
                             captcha_data=captcha_data,
                             error_message='CAPTCHA verification failed. Please try again.')

@app.route('/test-captcha')
def test_captcha():
    """Serve CAPTCHA test page"""
    return app.send_static_file('test_captcha.html')

@app.route('/identify', methods=['POST'])
def upload_file():
    """Handle file upload and species identification"""
    temp_file_path = None
    try:
        # Check security requirements
        requires_captcha = False
        
        # Check if browser is trusted
        if not security.is_browser_trusted():
            # Check rate limiting
            if security.check_rate_limit():
                requires_captcha = True
                logger.info("Rate limit exceeded, CAPTCHA required")
        
        # Check if CAPTCHA is required (should be verified separately now)
        if requires_captcha:
            logger.warning("CAPTCHA required but not verified")
            # Return to the main page with CAPTCHA required message
            captcha_data = security.generate_captcha()
            return render_template('index.html', 
                                 security_status=security.get_security_status(),
                                 captcha_data=captcha_data,
                                 error_message='Security verification required. Please solve the CAPTCHA below.')
        
        # Record the request for rate limiting
        security.record_request()
        
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

@app.route('/map')
def show_map():
    """Show interactive map for animal species"""
    species = request.args.get('species', '')
    common_name = request.args.get('common_name', '')
    animal_type = request.args.get('animal_type', '')
    
    # Get habitat data for the species
    habitat_data = get_animal_habitat_data(species, common_name, animal_type)
    
    return render_template('map.html', 
                         species=species,
                         common_name=common_name,
                         animal_type=animal_type,
                         habitat_data=habitat_data)

@app.route('/api/habitat/<species>')
def get_habitat_api(species):
    """API endpoint to get habitat data for a species"""
    common_name = request.args.get('common_name', '')
    animal_type = request.args.get('animal_type', '')
    habitat_data = get_animal_habitat_data(species, common_name, animal_type)
    return jsonify(habitat_data)

@app.route('/api/security/status')
def security_status():
    """Get current security status"""
    return jsonify(security.get_security_status())

@app.route('/api/security/captcha', methods=['POST'])
def generate_captcha_endpoint():
    """Generate a new CAPTCHA challenge"""
    captcha_data = security.generate_captcha()
    return jsonify(captcha_data)

@app.route('/api/security/verify', methods=['POST'])
def verify_captcha_endpoint():
    """Verify CAPTCHA answer"""
    data = request.get_json()
    captcha_id = data.get('captcha_id')
    answer = data.get('answer')
    
    if not captcha_id or not answer:
        return jsonify({'success': False, 'error': 'Missing captcha_id or answer'}), 400
    
    if security.verify_captcha(captcha_id, answer):
        return jsonify({'success': True, 'message': 'CAPTCHA verified successfully'})
    else:
        return jsonify({'success': False, 'error': 'CAPTCHA verification failed'}), 400

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