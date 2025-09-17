import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from PIL import Image
import io
from dotenv import load_dotenv

# Import our utility modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.file_utils import allowed_file, get_secure_filename, validate_file_size
from utils.image_utils import encode_image_to_base64, validate_image

# Load environment variables
load_dotenv()

# Set template folder to the correct path
template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
app = Flask(__name__, template_folder=template_dir)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configuration

def identify_turtle_species_openai(image_path):
    """Use OpenAI GPT-4 Vision to identify turtle species"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {"error": "OpenAI API key not configured"}
        
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
            
            # Try to parse as JSON, fallback to text if not valid JSON
            try:
                import json
                return json.loads(content)
            except:
                return {
                    "is_turtle": True,
                    "species": "Unknown",
                    "common_name": "Unknown",
                    "confidence": "low",
                    "description": content,
                    "notes": "Response was not in expected JSON format"
                }
        else:
            return {"error": f"OpenAI API error: {response.status_code} - {response.text}"}
            
    except Exception as e:
        return {"error": f"Error calling OpenAI API: {str(e)}"}

def identify_turtle_species_gemini(image_path):
    """Use Google Gemini Vision to identify turtle species"""
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return {"error": "Gemini API key not configured"}
        
        base64_image = encode_image_to_base64(image_path)
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
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
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": base64_image
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 500
            }
        }
        
        response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}", 
                               headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']
            
            # Try to parse as JSON, fallback to text if not valid JSON
            try:
                import json
                return json.loads(content)
            except:
                return {
                    "is_turtle": True,
                    "species": "Unknown",
                    "common_name": "Unknown",
                    "confidence": "low",
                    "description": content,
                    "notes": "Response was not in expected JSON format"
                }
        else:
            return {"error": f"Gemini API error: {response.status_code} - {response.text}"}
            
    except Exception as e:
        return {"error": f"Error calling Gemini API: {str(e)}"}

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and species identification"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Please upload PNG, JPG, JPEG, GIF, BMP, or WEBP'}), 400
        
        # Save file
        filename = get_secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Validate image
        if not validate_image(filepath):
            os.remove(filepath)
            return jsonify({'error': 'Invalid image file'}), 400
        
        # Get API preference from request
        api_preference = request.form.get('api', 'openai').lower()
        
        # Identify species using selected API
        if api_preference == 'gemini':
            result = identify_turtle_species_gemini(filepath)
        else:  # Default to OpenAI
            result = identify_turtle_species_openai(filepath)
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Turtle ID API is running'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
