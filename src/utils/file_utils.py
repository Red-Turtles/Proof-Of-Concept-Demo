"""
File handling utilities for the Turtle Species Identification App
"""

import os
from werkzeug.utils import secure_filename

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_secure_filename(filename):
    """Get a secure filename for upload"""
    return secure_filename(filename)

def validate_file_size(file_size, max_size=16 * 1024 * 1024):
    """Validate file size (default 16MB)"""
    return file_size <= max_size
