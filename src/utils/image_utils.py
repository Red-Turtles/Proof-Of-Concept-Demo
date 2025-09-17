"""
Image processing utilities for the Turtle Species Identification App
"""

import base64
from PIL import Image

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

def get_image_info(image_path):
    """Get basic image information"""
    try:
        with Image.open(image_path) as img:
            return {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height
            }
    except Exception:
        return None
