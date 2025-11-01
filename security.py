"""
Security module for WildID
Handles session management and basic security features
"""

import hashlib
import json
from datetime import timedelta
from flask import request, session
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self, app=None):
        self.app = app
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the security manager with Flask app"""
        self.app = app
        
        # Set up session configuration
        app.config['SESSION_TYPE'] = 'filesystem'
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
        app.config['SECRET_KEY'] = app.config.get('SECRET_KEY', 'dev-secret-key-change-in-production')
        
        # Generate a unique browser fingerprint
        @app.before_request
        def generate_browser_fingerprint():
            if 'browser_fingerprint' not in session:
                session['browser_fingerprint'] = self._generate_browser_fingerprint()
                session.permanent = True
    
    def _generate_browser_fingerprint(self):
        """Generate a unique browser fingerprint based on request headers"""
        fingerprint_data = {
            'user_agent': request.headers.get('User-Agent', ''),
            'accept_language': request.headers.get('Accept-Language', ''),
            'accept_encoding': request.headers.get('Accept-Encoding', ''),
        }
        
        # Create a hash of the fingerprint data
        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()[:16]
    
    def _get_client_ip(self):
        """Get client IP address, considering proxy headers"""
        # Only trust proxy headers if explicitly enabled
        trust_proxy = False
        if self.app is not None:
            trust_proxy = bool(self.app.config.get('TRUST_PROXY_HEADERS', False))

        if trust_proxy:
            # Check for forwarded headers (proxies, load balancers, etc.)
            forwarded_for = request.headers.get('X-Forwarded-For')
            if forwarded_for:
                return forwarded_for.split(',')[0].strip()

            real_ip = request.headers.get('X-Real-IP')
            if real_ip:
                return real_ip

        # Fallback to remote address when not trusting proxy headers or unavailable
        return request.remote_addr
