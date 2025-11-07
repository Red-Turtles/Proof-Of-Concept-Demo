"""
WildID - Wildlife Identification App
A modern Flask app that uses AI to identify wildlife species from uploaded images.
"""

import os
import secrets
import requests
import base64
import json
import uuid
import tempfile
import logging
from datetime import datetime, timedelta
from urllib.parse import urlparse
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash, g, abort
from flask_cors import CORS
from flask_session import Session
from PIL import Image
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from sqlalchemy import inspect, text, func
from security import SecurityManager
from models import db, User, Identification, UserBadge
from auth import AuthManager, mail

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure secret key for sessions
secret_key = os.getenv('SECRET_KEY')
if not secret_key:
    secret_key = secrets.token_hex(32)
    app.logger.warning('SECRET_KEY not set - generated ephemeral key for this process. Set SECRET_KEY in environment for persistent sessions.')
app.config['SECRET_KEY'] = secret_key
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')
app.config['SESSION_FILE_THRESHOLD'] = 100
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'true').lower() == 'true' if not app.debug else os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
app.config['SESSION_COOKIE_SAMESITE'] = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=int(os.getenv('PERMANENT_SESSION_DAYS', '30')))
app.config['PREFERRED_URL_SCHEME'] = os.getenv('PREFERRED_URL_SCHEME', 'https' if not app.debug else 'http')
app.config['REMEMBER_COOKIE_SECURE'] = os.getenv('REMEMBER_COOKIE_SECURE', 'true').lower() == 'true' if not app.debug else os.getenv('REMEMBER_COOKIE_SECURE', 'false').lower() == 'true'
app.config.setdefault('REMEMBER_COOKIE_NAME', 'wildid_remember')
app.config.setdefault('REMEMBER_COOKIE_DURATION', 60 * 60 * 24 * 30)
app.config.setdefault('REMEMBER_COOKIE_SAMESITE', app.config.get('SESSION_COOKIE_SAMESITE', 'Lax'))


def _parse_csv_env(var_name, fallback=None):
    value = os.getenv(var_name)
    if value is None:
        return fallback[:] if fallback else []
    parsed = [item.strip() for item in value.split(',') if item.strip()]
    return parsed or (fallback[:] if fallback else [])


default_allowed_hosts = ['localhost', '127.0.0.1']
app.config['ALLOWED_HOSTS'] = _parse_csv_env('ALLOWED_HOSTS', default_allowed_hosts)
app.config['MAGIC_LINK_BASE_URL'] = os.getenv('MAGIC_LINK_BASE_URL')

default_cors_origins = ['http://localhost:3000', 'http://127.0.0.1:3000']
if app.config['MAGIC_LINK_BASE_URL']:
    parsed_magic_link = urlparse(app.config['MAGIC_LINK_BASE_URL'])
    if parsed_magic_link.hostname and parsed_magic_link.hostname not in app.config['ALLOWED_HOSTS']:
        app.config['ALLOWED_HOSTS'].append(parsed_magic_link.hostname)
    default_cors_origins.append(app.config['MAGIC_LINK_BASE_URL'])
allowed_cors_origins = _parse_csv_env('CORS_ALLOWED_ORIGINS', default_cors_origins)
allowed_cors_origins = list(dict.fromkeys([origin.rstrip('/') for origin in allowed_cors_origins]))

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///wildid.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'localhost')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 1025))  # Default to Mailhog port for development
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'False').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@wildid.app')

CORS(app, resources={r"/api/*": {"origins": allowed_cors_origins}}, supports_credentials=True)

# Initialize extensions
Session(app)
db.init_app(app)
mail.init_app(app)

# Initialize managers
security = SecurityManager(app)
auth = AuthManager(app)

# Create database tables
with app.app_context():
    db.create_all()
    try:
        inspector = inspect(db.engine)
        identification_columns = {column['name'] for column in inspector.get_columns('identifications')}
        migrations = []
        if 'user_feedback' not in identification_columns:
            migrations.append("ALTER TABLE identifications ADD COLUMN user_feedback VARCHAR(20)")
        if 'feedback_comment' not in identification_columns:
            migrations.append("ALTER TABLE identifications ADD COLUMN feedback_comment TEXT")
        if 'feedback_at' not in identification_columns:
            migrations.append("ALTER TABLE identifications ADD COLUMN feedback_at TIMESTAMP")
        for statement in migrations:
            db.session.execute(text(statement))
        if migrations:
            db.session.commit()
    except Exception as migration_error:
        app.logger.error(f"Failed to ensure identifications columns: {migration_error}")
        db.session.rollback()

@app.before_request
def restore_user_from_cookie():
    auth.ensure_user_from_remember_cookie()

# Security headers
@app.after_request
def add_security_headers(response):
    """Add security headers for enhanced protection"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    nonce = getattr(g, 'csp_nonce', '')
    script_sources = ["'self'", 'https://unpkg.com']
    if nonce:
        script_sources.append(f"'nonce-{nonce}'")

    csp = " ".join([
        "default-src 'self';",
        f"script-src {' '.join(script_sources)};",
        "style-src 'self' 'unsafe-inline' https://unpkg.com;",
        "img-src 'self' data: https://*.tile.openstreetmap.org;"
    ])
    response.headers['Content-Security-Policy'] = csp
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

CSRF_PROTECTED_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}
CSRF_EXEMPT_ENDPOINTS = {'static'}


def _get_or_create_csrf_token():
    token = session.get('_csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['_csrf_token'] = token
    return token


@app.before_request
def ensure_csrf_token():
    _get_or_create_csrf_token()


@app.before_request
def set_csp_nonce():
    g.csp_nonce = secrets.token_urlsafe(16)


def _csrf_failure_response():
    logger.warning('CSRF token missing or invalid for %s %s', request.method, request.path)
    if request.path.startswith('/api/') or request.is_json or request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
        return jsonify({'success': False, 'error': 'CSRF token missing or invalid'}), 400
    flash('Your session has expired. Please try again.', 'error')
    return redirect(request.referrer or url_for('index'))


@app.before_request
def csrf_protect():
    if request.method not in CSRF_PROTECTED_METHODS:
        return

    endpoint = (request.endpoint or '').split('.')[-1]
    if endpoint in CSRF_EXEMPT_ENDPOINTS:
        return

    session_token = session.get('_csrf_token')
    if not session_token:
        return _csrf_failure_response()

    request_token = request.headers.get('X-CSRF-Token')
    if not request_token:
        if request.is_json:
            payload = request.get_json(silent=True) or {}
            request_token = payload.get('csrf_token')
        else:
            request_token = request.form.get('csrf_token')

    if not request_token or not secrets.compare_digest(session_token, request_token):
        return _csrf_failure_response()


@app.context_processor
def inject_security_tokens():
    return {
        'csrf_token': _get_or_create_csrf_token,
        'csp_nonce': getattr(g, 'csp_nonce', '')
    }

# Configuration
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Badge configuration
BADGE_DEFINITIONS = [
    {
        'key': 'first_identification',
        'name': 'First Discovery',
        'description': 'Complete your first wildlife identification.',
        'icon': '🌱',
        'type': 'total_identifications',
        'threshold': 1
    },
    {
        'key': 'trailblazer',
        'name': 'Trailblazer',
        'description': 'Complete five wildlife identifications.',
        'icon': '🔥',
        'type': 'total_identifications',
        'threshold': 5
    },
    {
        'key': 'wildlife_champion',
        'name': 'Wildlife Champion',
        'description': 'Complete ten wildlife identifications.',
        'icon': '🏆',
        'type': 'total_identifications',
        'threshold': 10
    },
    {
        'key': 'species_sleuth',
        'name': 'Species Sleuth',
        'description': 'Identify three unique species.',
        'icon': '🕵️',
        'type': 'unique_species',
        'threshold': 3
    },
    {
        'key': 'habitat_hopper',
        'name': 'Habitat Hopper',
        'description': 'Identify animals from three different animal types.',
        'icon': '🦋',
        'type': 'animal_types',
        'threshold': 3
    }
]

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Utility Functions
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def calculate_user_identification_stats(user_id):
    """Aggregate identification stats used for achievements."""
    total_identifications = db.session.query(func.count(Identification.id)).filter_by(user_id=user_id).scalar() or 0

    unique_species = (
        db.session.query(func.count(func.distinct(Identification.species)))
        .filter(
            Identification.user_id == user_id,
            Identification.species.isnot(None),
            Identification.species != ''
        )
        .scalar()
    ) or 0

    unique_animal_types = (
        db.session.query(func.count(func.distinct(Identification.animal_type)))
        .filter(
            Identification.user_id == user_id,
            Identification.animal_type.isnot(None),
            Identification.animal_type != ''
        )
        .scalar()
    ) or 0

    return {
        'total_identifications': total_identifications,
        'unique_species': unique_species,
        'animal_types': unique_animal_types
    }


def evaluate_badge_progress(badge_definition, stats):
    metric_key = badge_definition['type']
    current_value = stats.get(metric_key, 0)
    return current_value, current_value >= badge_definition['threshold']


def award_badges_for_user(user):
    """Check badge criteria for a user and award new badges."""
    stats = calculate_user_identification_stats(user.id)
    existing_badges = {
        badge.badge_key: badge for badge in UserBadge.query.filter_by(user_id=user.id)
    }

    new_badges = []
    for badge_definition in BADGE_DEFINITIONS:
        if badge_definition['key'] in existing_badges:
            continue

        progress_value, achieved = evaluate_badge_progress(badge_definition, stats)
        if achieved:
            badge = UserBadge(
                user_id=user.id,
                badge_key=badge_definition['key'],
                badge_name=badge_definition['name'],
                badge_description=badge_definition['description'],
                badge_icon=badge_definition['icon'],
                metadata_json=json.dumps({
                    'progress_value': progress_value,
                    'threshold': badge_definition['threshold']
                })
            )
            db.session.add(badge)
            new_badges.append(badge)

    if new_badges:
        db.session.commit()

    return new_badges


def build_badge_overview(user_id):
    stats = calculate_user_identification_stats(user_id)
    awarded_badges = {
        badge.badge_key: badge for badge in UserBadge.query.filter_by(user_id=user_id)
    }

    overview = []
    for definition in BADGE_DEFINITIONS:
        progress_value, achieved = evaluate_badge_progress(definition, stats)
        threshold = definition['threshold']
        ratio = min(progress_value / threshold if threshold else 1, 1.0)
        award = awarded_badges.get(definition['key'])

        overview.append({
            'key': definition['key'],
            'name': definition['name'],
            'description': definition['description'],
            'icon': definition['icon'],
            'is_earned': bool(award),
            'awarded_at': award.awarded_at if award else None,
            'progress_value': progress_value,
            'threshold': threshold,
            'progress_ratio': ratio,
            'remaining': max(threshold - progress_value, 0)
        })

    return overview, stats

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
                            "text": """Carefully analyze this image to identify the animal species.

INSTRUCTIONS:
1. Look carefully at the ENTIRE image, including partially visible animals or animals in the background
2. If you see ANY animal (mammal, bird, reptile, fish, insect, etc.), set "is_animal" to true
3. Be generous in your interpretation - if it might be an animal, identify it
4. Consider image quality, lighting, and angle in your confidence assessment
5. If unsure about exact species, provide your best educated guess with appropriate confidence level
6. Only set "is_animal" to false if you are CERTAIN there is NO animal visible

For animal identification, provide:
- Scientific name (or "Unknown" if cannot determine)
- Common name (or general type like "Unidentified Bird" if species unknown)
- Animal type: mammal, bird, reptile, amphibian, fish, or invertebrate
- Conservation status (estimate if not certain)
- Key identifying features you can see
- Your confidence level: high (certain), medium (likely), or low (uncertain)

IMPORTANT: Format your response as valid JSON with this exact structure:
{
    "is_animal": true/false,
    "species": "scientific name or Unknown",
    "common_name": "common name or general description",
    "animal_type": "mammal/bird/reptile/amphibian/fish/invertebrate/unknown",
    "conservation_status": "Least Concern/Near Threatened/Vulnerable/Endangered/Critically Endangered/Data Deficient/Unknown",
    "confidence": "high/medium/low",
    "description": "key identifying features and reasoning",
    "notes": "image quality notes, partial visibility, or other relevant observations"
}

Use double quotes and valid JSON syntax. If you see an animal but cannot identify species, still provide a general identification."""
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
            "max_tokens": 600,
            "temperature": 0.2
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
                    "is_animal": True,
                    "species": "Unknown",
                    "common_name": "Unknown",
                    "animal_type": "unknown",
                    "conservation_status": "Unknown",
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

def get_conservation_info(species_name, common_name, conservation_status):
    """Get detailed conservation information for a species"""
    # Comprehensive conservation database
    conservation_data = {
        # Least Concern species
        "panthera leo": {
            "status": "Vulnerable",
            "population": "20,000-25,000 mature individuals",
            "trend": "Decreasing",
            "threats": "Habitat loss, human-wildlife conflict, poaching, prey depletion"
        },
        "ursus arctos": {
            "status": "Least Concern",
            "population": "200,000+ individuals worldwide",
            "trend": "Stable",
            "threats": "Habitat fragmentation, hunting in some regions"
        },
        "elephas maximus": {
            "status": "Endangered",
            "population": "40,000-50,000 individuals",
            "trend": "Decreasing",
            "threats": "Habitat loss, human-elephant conflict, poaching"
        },
        "canis lupus": {
            "status": "Least Concern",
            "population": "300,000+ individuals",
            "trend": "Stable",
            "threats": "Persecution, habitat loss, disease"
        },
        
        # Birds
        "aquila chrysaetos": {
            "status": "Least Concern",
            "population": "170,000-250,000 mature individuals",
            "trend": "Stable",
            "threats": "Habitat loss, persecution, lead poisoning"
        },
        "aptenodytes forsteri": {
            "status": "Near Threatened",
            "population": "595,000 mature individuals",
            "trend": "Stable",
            "threats": "Climate change, fishing activities"
        },
        "turdus migratorius": {
            "status": "Least Concern",
            "population": "320,000,000 mature individuals",
            "trend": "Increasing",
            "trend": "Stable"
        },
        
        # Reptiles
        "chelonia mydas": {
            "status": "Endangered",
            "population": "85,000-90,000 nesting females",
            "trend": "Decreasing",
            "threats": "Climate change, ocean pollution, fishing nets, illegal harvesting"
        },
        "crocodylus niloticus": {
            "status": "Least Concern",
            "population": "250,000-500,000 mature individuals",
            "trend": "Stable",
            "threats": "Habitat destruction, hunting"
        },
        
        # Amphibians
        "rana catesbeiana": {
            "status": "Least Concern",
            "population": "Large and stable",
            "trend": "Stable",
            "threats": "Habitat loss, pollution, invasive species"
        },
        
        # Fish
        "thunnus thynnus": {
            "status": "Endangered",
            "population": "Unknown but declining",
            "trend": "Decreasing",
            "threats": "Overfishing, bycatch, habitat degradation"
        },
        "carcharodon carcharias": {
            "status": "Vulnerable",
            "population": "Unknown",
            "trend": "Unknown",
            "threats": "Overfishing, bycatch, habitat loss"
        },
        
        # Invertebrates
        "apis mellifera": {
            "status": "Data Deficient",
            "population": "Unknown",
            "trend": "Unknown",
            "threats": "Pesticides, habitat loss, diseases, climate change"
        },
        "danaus plexippus": {
            "status": "Endangered",
            "population": "Unknown but declining",
            "trend": "Decreasing",
            "threats": "Habitat loss, pesticides, climate change"
        }
    }
    
    # Try to find by scientific name first
    species_key = species_name.lower().strip() if species_name else ""
    if species_key in conservation_data:
        return conservation_data[species_key]
    
    # Try to find by common name
    for key, data in conservation_data.items():
        if common_name and common_name.lower().strip() in data.get("name", "").lower():
            return data
    
    # Return default based on AI-provided conservation status
    default_data = {
        "status": conservation_status or "Unknown",
        "population": "Population data not available",
        "trend": "Unknown",
        "threats": "Conservation threats vary by species and region"
    }
    
    # Customize based on conservation status
    if conservation_status:
        if "endangered" in conservation_status.lower():
            default_data["trend"] = "Decreasing"
            default_data["threats"] = "Habitat loss, climate change, human activities"
        elif "vulnerable" in conservation_status.lower():
            default_data["trend"] = "Decreasing"
            default_data["threats"] = "Habitat degradation, hunting, pollution"
        elif "least concern" in conservation_status.lower():
            default_data["trend"] = "Stable"
            default_data["threats"] = "General habitat protection needed"
        elif "near threatened" in conservation_status.lower():
            default_data["trend"] = "Stable to decreasing"
            default_data["threats"] = "Monitoring needed, potential future threats"
    
    return default_data

def get_species_fun_facts(species_name, common_name, animal_type):
    """Get species-specific fun facts and additional information"""
    fun_facts_db = {
        # Mammals
        "panthera leo": {
            "fun_fact": "Lions are the only big cats that live in groups called prides! A pride can have up to 40 lions, but typically consists of 10-15 members including several females, their cubs, and 1-3 males.",
            "origin": "African savannas and grasslands, with a small population in India's Gir Forest"
        },
        "ursus arctos": {
            "fun_fact": "Brown bears can run up to 35 mph (56 km/h) for short distances, faster than most humans! They can also stand on their hind legs to get a better view or to appear larger when threatened.",
            "origin": "Northern forests, mountains, and tundra across North America, Europe, and Asia"
        },
        "elephas maximus": {
            "fun_fact": "Asian elephants have an incredible memory and can remember the locations of water sources and feeding grounds for decades! They also use their trunks like a hand with over 40,000 muscles.",
            "origin": "Tropical forests and grasslands of Southeast Asia and India"
        },
        "canis lupus": {
            "fun_fact": "Wolves have a complex communication system using howls, barks, growls, and body language. Their howls can be heard up to 10 miles away and help coordinate pack activities!",
            "origin": "Forests, tundra, grasslands, and mountains across North America and Eurasia"
        },
        
        # Birds
        "aquila chrysaetos": {
            "fun_fact": "Golden eagles have incredible eyesight - they can spot a rabbit from 2 miles away! They can also dive at speeds of over 150 mph when hunting, making them one of the fastest birds on Earth.",
            "origin": "Mountainous regions and open landscapes across the Northern Hemisphere"
        },
        "aptenodytes forsteri": {
            "fun_fact": "Emperor penguins can dive deeper than any other bird - up to 1,850 feet (565 meters) deep! They can also hold their breath for up to 22 minutes underwater while hunting for fish.",
            "origin": "Antarctica - the only continent where they breed and live year-round"
        },
        "turdus migratorius": {
            "fun_fact": "American robins can eat up to 14 feet of earthworms per day! They're also one of the first birds to sing in the morning, often starting before sunrise during breeding season.",
            "origin": "Throughout North America, from Alaska to Mexico"
        },
        
        # Reptiles
        "chelonia mydas": {
            "fun_fact": "Green sea turtles can hold their breath for up to 5 hours underwater! They also return to the exact beach where they were born to lay their own eggs, sometimes traveling thousands of miles.",
            "origin": "Tropical and subtropical oceans worldwide"
        },
        "crocodylus niloticus": {
            "fun_fact": "Nile crocodiles can live for over 100 years and have the strongest bite force of any living animal - up to 5,000 pounds per square inch! They can also go months without eating.",
            "origin": "Freshwater rivers, lakes, and marshes across Africa"
        },
        
        # Amphibians
        "rana catesbeiana": {
            "fun_fact": "American bullfrogs can jump up to 10 times their body length! They're also voracious eaters and will consume almost anything that fits in their mouth, including other frogs, snakes, and small birds.",
            "origin": "Ponds, lakes, and slow-moving streams in eastern North America"
        },
        
        # Fish
        "thunnus thynnus": {
            "fun_fact": "Atlantic bluefin tuna can swim at speeds of up to 43 mph (70 km/h) and maintain body temperatures warmer than the surrounding water, making them warm-blooded fish!",
            "origin": "Temperate and tropical waters of the Atlantic Ocean and Mediterranean Sea"
        },
        "carcharodon carcharias": {
            "fun_fact": "Great white sharks can detect a single drop of blood in 25 gallons of water! They also have up to 300 teeth arranged in rows, with new teeth constantly replacing old ones throughout their lifetime.",
            "origin": "Coastal and offshore waters of all major oceans"
        },
        
        # Invertebrates
        "apis mellifera": {
            "fun_fact": "Honey bees perform a 'waggle dance' to communicate the location of food sources to other bees! A single bee produces only about 1/12 teaspoon of honey in its lifetime.",
            "origin": "Originally from Europe, Africa, and Asia; now found worldwide"
        },
        "danaus plexippus": {
            "fun_fact": "Monarch butterflies migrate up to 3,000 miles from North America to Mexico for winter! It takes 3-4 generations of monarchs to complete the full migration cycle.",
            "origin": "North America, with migratory populations traveling between Canada and Mexico"
        }
    }
    
    # Try to find by scientific name first
    species_key = species_name.lower().strip() if species_name else ""
    if species_key in fun_facts_db:
        return fun_facts_db[species_key]
    
    # Try to find by common name
    for key, data in fun_facts_db.items():
        if common_name and common_name.lower().strip() in data.get("name", "").lower():
            return data
    
    # Return default based on animal type
    default_facts = {
        "fun_fact": "This species has unique characteristics and behaviors that make it fascinating to study. Each animal plays an important role in its ecosystem.",
        "origin": f"Native habitats vary by region for this {animal_type or 'animal'} species"
    }
    
    # Customize based on animal type
    if animal_type:
        if animal_type.lower() == "mammal":
            default_facts["fun_fact"] = "Mammals are warm-blooded animals with fur or hair that feed their young with milk. They have complex social behaviors and advanced intelligence."
        elif animal_type.lower() == "bird":
            default_facts["fun_fact"] = "Birds are the only animals with feathers and can fly (with some exceptions). They have excellent vision and complex migration patterns."
        elif animal_type.lower() == "reptile":
            default_facts["fun_fact"] = "Reptiles are cold-blooded animals with scales or bony plates. They have been on Earth for over 300 million years!"
        elif animal_type.lower() == "amphibian":
            default_facts["fun_fact"] = "Amphibians can live both in water and on land. They have permeable skin that can absorb water and oxygen."
        elif animal_type.lower() == "fish":
            default_facts["fun_fact"] = "Fish have been swimming in Earth's waters for over 500 million years. They come in amazing shapes, sizes, and colors!"
        elif animal_type.lower() == "invertebrate":
            default_facts["fun_fact"] = "Invertebrates make up 97% of all animal species on Earth! They have no backbone but incredible diversity and adaptations."
    
    return default_facts

def get_species_help_tips(species_name, common_name, animal_type, conservation_status):
    """Get species-specific conservation help tips"""
    help_tips_db = {
        # Endangered species
        "chelonia mydas": "Reduce plastic use (especially single-use items), support beach conservation programs, avoid disturbing nesting sites, and choose sustainable seafood to protect sea turtle habitats.",
        "elephas maximus": "Support elephant conservation organizations, avoid products containing palm oil from unsustainable sources, and promote wildlife-friendly tourism that doesn't exploit elephants.",
        "danaus plexippus": "Plant native milkweed and nectar plants in your garden, avoid using pesticides, and support monarch butterfly conservation initiatives and habitat restoration projects.",
        "thunnus thynnus": "Choose sustainably caught fish, support marine protected areas, and reduce your carbon footprint to help combat climate change affecting ocean ecosystems.",
        
        # Vulnerable species
        "panthera leo": "Support wildlife conservation organizations, promote coexistence between humans and lions, and advocate for habitat protection in lion territories.",
        "carcharodon carcharias": "Support shark conservation research, choose sustainable seafood, and educate others about the importance of sharks in marine ecosystems.",
        
        # General tips based on animal type
        "mammal": "Support habitat conservation, reduce your carbon footprint, and choose products from companies committed to wildlife protection.",
        "bird": "Keep cats indoors, use bird-friendly windows, plant native vegetation, and support bird conservation organizations.",
        "reptile": "Support habitat protection, avoid collecting wild reptiles, and educate others about reptile conservation needs.",
        "amphibian": "Protect wetlands, avoid using pesticides, and support amphibian conservation research and habitat restoration.",
        "fish": "Choose sustainable seafood, reduce plastic pollution, and support marine protected areas and clean water initiatives.",
        "invertebrate": "Plant pollinator-friendly gardens, avoid pesticides, and support research into invertebrate conservation and ecosystem health."
    }
    
    # Try to find species-specific tips first
    species_key = species_name.lower().strip() if species_name else ""
    if species_key in help_tips_db:
        return help_tips_db[species_key]
    
    # Try to find by common name
    for key, tip in help_tips_db.items():
        if common_name and common_name.lower().strip() in key.lower():
            return tip
    
    # Return general tips based on animal type
    if animal_type and animal_type.lower() in help_tips_db:
        return help_tips_db[animal_type.lower()]
    
    # Return conservation status-based tips
    if conservation_status:
        if "endangered" in conservation_status.lower():
            return "Support conservation organizations, reduce your environmental impact, and advocate for stronger wildlife protection laws."
        elif "vulnerable" in conservation_status.lower():
            return "Support habitat conservation, choose sustainable products, and promote awareness about wildlife protection."
        elif "least concern" in conservation_status.lower():
            return "Continue supporting general wildlife conservation efforts and habitat protection to maintain healthy populations."
    
    # Default general tip
    return "Support wildlife conservation organizations, reduce your environmental impact, and educate others about the importance of protecting all species and their habitats."

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
    current_user = auth.get_current_user()
    return render_template('index.html', current_user=current_user)

@app.route('/discovery')
def discovery():
    """Serve the discovery page"""
    current_user = auth.get_current_user()
    return render_template('discovery.html', current_user=current_user)

# Authentication routes
@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    """Handle login page and magic link sending"""
    if request.method == 'GET':
        # Check if already logged in
        if auth.is_authenticated():
            return redirect(url_for('index'))
        
        return render_template('login.html')
    
    # POST - send magic link
    email = request.form.get('email', '').strip().lower()
    
    if not email:
        flash('Please enter your email address', 'error')
        return render_template('login.html')
    
    # Basic email validation
    if '@' not in email or '.' not in email.split('@')[1]:
        flash('Please enter a valid email address', 'error')
        return render_template('login.html')
    
    try:
        # Generate and send magic link
        token = auth.generate_magic_link_token(email)

        if auth.send_magic_link(email, token):
            flash('Check your email! We sent you a magic link to sign in.', 'success')
        else:
            flash('There was an issue sending the email. Please try again.', 'error')
    except Exception as e:
        logger.error(f"Error sending magic link: {str(e)}")
        flash('An error occurred. Please try again.', 'error')
    
    return render_template('login.html', email_sent=True)

@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    """Handle registration - same as login for passwordless"""
    # For passwordless auth, registration is the same as login
    return login()

@app.route('/auth/verify')
def verify_magic_link():
    """Verify magic link token and log user in"""
    token = request.args.get('token')
    
    if not token:
        flash('Invalid magic link', 'error')
        return redirect(url_for('login'))
    
    # Verify token
    email = auth.verify_magic_link_token(token)
    
    if not email:
        flash('This magic link has expired or is invalid. Please request a new one.', 'error')
        return redirect(url_for('login'))
    
    # Create or get user
    user = auth.create_or_get_user(email)
    
    # Log user in
    auth.login_user(user)
    response = redirect(url_for('index'))
    auth.set_remember_cookie(response, user)
    
    flash(f'Welcome back, {email}!', 'success')
    return response

@app.route('/auth/logout', methods=['POST'])
def logout():
    """Log out the current user"""
    auth.logout_user()
    response = redirect(url_for('index'))
    auth.clear_remember_cookie(response)
    flash('You have been logged out successfully', 'success')
    return response

@app.route('/history')
def history():
    """Show user's identification history"""
    current_user = auth.get_current_user()
    
    if not current_user:
        flash('Please sign in to view your history', 'info')
        return redirect(url_for('login'))
    
    # Get user's identifications, ordered by most recent
    identifications = Identification.query.filter_by(user_id=current_user.id)\
        .order_by(Identification.created_at.desc())\
        .all()
    
    return render_template('history.html', 
                         current_user=current_user, 
                         identifications=identifications)

@app.route('/profile')
def profile():
    """Show account overview with recent identifications"""
    current_user = auth.get_current_user()

    if not current_user:
        flash('Please sign in to view your profile', 'info')
        return redirect(url_for('login'))

    recent_identifications = (
        Identification.query
        .filter_by(user_id=current_user.id)
        .order_by(Identification.created_at.desc())
        .limit(5)
        .all()
    )

    total_identifications = Identification.query.filter_by(user_id=current_user.id).count()
    latest_identification = recent_identifications[0] if recent_identifications else None

    badge_overview, badge_stats = build_badge_overview(current_user.id)

    return render_template(
        'profile.html',
        current_user=current_user,
        recent_identifications=recent_identifications,
        total_identifications=total_identifications,
        latest_identification=latest_identification,
        badge_overview=badge_overview,
        badge_stats=badge_stats
    )

@app.route('/history/<int:identification_id>')
def history_detail(identification_id):
    """Detailed view for a single identification"""
    current_user = auth.get_current_user()

    if not current_user:
        flash('Please sign in to view identification details', 'info')
        return redirect(url_for('login'))

    identification = Identification.query.filter_by(
        id=identification_id,
        user_id=current_user.id
    ).first()

    if not identification:
        abort(404)

    result_data = identification.get_result_json() or {
        'species': identification.species,
        'common_name': identification.common_name,
        'animal_type': identification.animal_type,
        'conservation_status': identification.conservation_status,
        'confidence': identification.confidence,
        'description': identification.description,
        'notes': identification.notes,
    }

    return render_template(
        'history_detail.html',
        current_user=current_user,
        identification=identification,
        result=result_data
    )

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback on an identification"""
    try:
        data = request.get_json()
        identification_id = data.get('identification_id')
        feedback = data.get('feedback')  # 'correct' or 'incorrect'
        comment = data.get('comment', '')
        
        if not identification_id or feedback not in ['correct', 'incorrect']:
            return jsonify({'success': False, 'error': 'Invalid feedback data'}), 400
        
        # Authentication required
        current_user = auth.get_current_user()
        if not current_user:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401

        # Get the identification
        identification = Identification.query.get(identification_id)
        if not identification or identification.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Update feedback
        identification.user_feedback = feedback
        identification.feedback_comment = comment
        identification.feedback_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Feedback received: {feedback} for identification {identification_id}")
        
        return jsonify({
            'success': True, 
            'message': 'Thank you for your feedback!'
        })
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to submit feedback'}), 500


@app.route('/api/security/status', methods=['GET'])
def security_status():
    """Return current security status for the session"""
    status = security.get_status()
    status['csrf_token'] = _get_or_create_csrf_token()
    status['captcha_enabled'] = True
    status['rate_limit_window_seconds'] = security.rate_limit_window
    return jsonify(status)


@app.route('/api/security/captcha', methods=['POST'])
def generate_captcha():
    """Generate a CAPTCHA challenge"""
    captcha_id, question = security.create_captcha()
    logger.info('Issued CAPTCHA challenge for session %s', session.get('browser_fingerprint', 'unknown'))
    return jsonify({
        'captcha_id': captcha_id,
        'question': question,
        'expires_in': security.captcha_ttl
    })


@app.route('/api/security/verify', methods=['POST'])
def verify_captcha():
    """Verify CAPTCHA response and update trust state"""
    data = request.get_json() or {}
    captcha_id = data.get('captcha_id')
    answer = data.get('answer')

    if not captcha_id or answer is None:
        return jsonify({'success': False, 'error': 'captcha_id and answer are required'}), 400

    success, error_code = security.verify_captcha(captcha_id, answer)

    if success:
        status = security.get_status()
        logger.info('CAPTCHA verification succeeded for session %s', session.get('browser_fingerprint', 'unknown'))
        return jsonify({'success': True, 'message': 'Verification successful', 'status': status, 'code': 'verified'})

    error_messages = {
        'invalid_captcha': 'This CAPTCHA challenge is no longer valid. Please request a new one.',
        'expired_captcha': 'This CAPTCHA challenge expired. Please request a new one.',
        'incorrect_answer': 'Incorrect answer. Please try again.',
        'too_many_attempts': 'Too many incorrect attempts. Please request a new CAPTCHA.'
    }

    message = error_messages.get(error_code, 'Failed to verify CAPTCHA. Please try again.')
    logger.warning('CAPTCHA verification failed (%s) for session %s', error_code, session.get('browser_fingerprint', 'unknown'))

    status = security.get_status()
    return jsonify({'success': False, 'error': message, 'status': status, 'code': error_code}), 400 if error_code != 'too_many_attempts' else 429

@app.route('/identify', methods=['POST'])
def upload_file():
    """Handle file upload and species identification"""
    temp_file_path = None
    current_user = auth.get_current_user()
    allowed, reason = security.can_proceed('identify')
    if not allowed:
        message = 'Security verification required. Please complete the CAPTCHA challenge before continuing.'
        wants_json = request.is_json or request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']
        if wants_json:
            status = security.get_status()
            return jsonify({'error': message, 'code': reason, 'status': status}), 429
        flash(message, 'error')
        return redirect(url_for('discovery'))
    
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
        
        security.record_request('identify')

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
        
        # Get conservation information
        conservation_info = None
        fun_facts_info = None
        help_tips = None
        
        if result.get('is_animal') and not result.get('error'):
            conservation_info = get_conservation_info(
                result.get('species', ''),
                result.get('common_name', ''),
                result.get('conservation_status', '')
            )
            
            fun_facts_info = get_species_fun_facts(
                result.get('species', ''),
                result.get('common_name', ''),
                result.get('animal_type', '')
            )
            
            help_tips = get_species_help_tips(
                result.get('species', ''),
                result.get('common_name', ''),
                result.get('animal_type', ''),
                result.get('conservation_status', '')
            )
        
        # Save to history if user is logged in
        identification_id = None
        if current_user and result.get('is_animal') and not result.get('error'):
            try:
                identification = Identification(
                    user_id=current_user.id,
                    species=result.get('species'),
                    common_name=result.get('common_name'),
                    animal_type=result.get('animal_type'),
                    conservation_status=result.get('conservation_status'),
                    confidence=result.get('confidence'),
                    description=result.get('description'),
                    notes=result.get('notes'),
                    image_data=image_data,
                    image_mime=image_mime,
                    result_json=json.dumps(result)
                )
                db.session.add(identification)
                db.session.commit()
                identification_id = identification.id
                logger.info(f"Saved identification to history for user {current_user.email}")

                new_badges = award_badges_for_user(current_user)
                for badge in new_badges:
                    flash(f"{badge.badge_icon} New badge unlocked: {badge.badge_name}!", 'success')
            except Exception as e:
                logger.error(f"Error saving identification to history: {str(e)}")
                # Don't fail the request if history save fails
        
        return render_template('results.html', 
                             result=result, 
                             image_data=image_data, 
                             image_mime=image_mime,
                             conservation_info=conservation_info,
                             fun_facts_info=fun_facts_info,
                             help_tips=help_tips,
                             current_user=current_user,
                             identification_id=identification_id)
        
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

@app.route('/test-coordinates')
def test_coordinates():
    """Test endpoint to check coordinate data"""
    habitat_data = get_animal_habitat_data("panthera leo", "African Lion", "mammal")
    
    # Show raw data
    print("=== RAW HABITAT DATA ===")
    print(f"Type: {type(habitat_data)}")
    print(f"Data: {habitat_data}")
    
    if 'habitats' in habitat_data:
        for i, habitat in enumerate(habitat_data['habitats']):
            print(f"Habitat {i+1}:")
            print(f"  Name: {habitat['name']}")
            print(f"  Lat: {habitat['lat']} (type: {type(habitat['lat'])})")
            print(f"  Lng: {habitat['lng']} (type: {type(habitat['lng'])})")
    
    return jsonify({
        "raw_data": habitat_data,
        "analysis": "Check console for detailed output"
    })

@app.route('/test-map')
def test_map():
    """Test map page for debugging coordinates"""
    return render_template('test-map.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'WildID API is running'})

if __name__ == '__main__':
    # Get port from environment or default to 3000
    port = int(os.getenv('PORT', 3000))
    
    print("🦜 Starting WildID - Wildlife Identification App...")
    print(f"   Open your browser to: http://localhost:{port}")
    print("   Press Ctrl+C to stop the server")
    print()
    
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() in ('1', 'true', 'yes')
    app.run(debug=debug_mode, host='0.0.0.0', port=port)