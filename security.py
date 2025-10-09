"""
Security module for Turtle Species Identification App
Handles CAPTCHA, rate limiting, and browser trust tracking
"""

import hashlib
import hmac
import json
import time
import random
import string
import os
import requests
from datetime import datetime, timedelta
from flask import request, session, jsonify
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self, app=None):
        self.app = app
        self.rate_limit_window = int(os.getenv('RATE_LIMIT_WINDOW', 3600))  # 1 hour
        self.max_requests_per_window = int(os.getenv('MAX_REQUESTS_PER_WINDOW', 2))  # Max requests before CAPTCHA
        self.captcha_timeout = int(os.getenv('CAPTCHA_TIMEOUT', 300))  # 5 minutes
        self.browser_trust_duration = int(os.getenv('BROWSER_TRUST_DURATION', 86400 * 30))  # 30 days
        
        # In-memory storage for demo (use Redis in production)
        self.request_counts = {}
        self.captcha_sessions = {}
        self.trusted_browsers = {}
        
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
            'connection': request.headers.get('Connection', ''),
            'upgrade_insecure_requests': request.headers.get('Upgrade-Insecure-Requests', ''),
            'sec_fetch_dest': request.headers.get('Sec-Fetch-Dest', ''),
            'sec_fetch_mode': request.headers.get('Sec-Fetch-Mode', ''),
            'sec_fetch_site': request.headers.get('Sec-Fetch-Site', ''),
        }
        
        # Create a hash of the fingerprint data
        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()[:16]
    
    def _get_client_ip(self):
        """Get client IP address, considering proxy headers"""
        # Check for forwarded headers (proxies, load balancers, etc.)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Fallback to remote address
        return request.remote_addr
    
    def _get_rate_limit_key(self):
        """Generate rate limiting key combining IP and browser fingerprint"""
        ip = self._get_client_ip()
        browser_fp = session.get('browser_fingerprint', 'unknown')
        return f"{ip}:{browser_fp}"
    
    def check_rate_limit(self):
        """Check if client has exceeded rate limit"""
        key = self._get_rate_limit_key()
        current_time = time.time()
        
        # Clean old entries
        self._cleanup_old_entries()
        
        # Get current request count
        if key not in self.request_counts:
            self.request_counts[key] = []
        
        # Remove old requests outside the window
        window_start = current_time - self.rate_limit_window
        self.request_counts[key] = [
            req_time for req_time in self.request_counts[key] 
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        request_count = len(self.request_counts[key])
        return request_count >= self.max_requests_per_window
    
    def record_request(self):
        """Record a new request for rate limiting"""
        key = self._get_rate_limit_key()
        current_time = time.time()
        
        if key not in self.request_counts:
            self.request_counts[key] = []
        
        self.request_counts[key].append(current_time)
    
    def is_browser_trusted(self):
        """Check if the current browser is trusted"""
        browser_fp = session.get('browser_fingerprint')
        if not browser_fp:
            return False
        
        if browser_fp in self.trusted_browsers:
            trust_time = self.trusted_browsers[browser_fp]
            if time.time() - trust_time < self.browser_trust_duration:
                return True
        
        return False
    
    def trust_browser(self):
        """Mark the current browser as trusted"""
        browser_fp = session.get('browser_fingerprint')
        if browser_fp:
            self.trusted_browsers[browser_fp] = time.time()
            logger.info(f"Browser trusted: {browser_fp}")
    
    def generate_captcha(self):
        """Generate a new CAPTCHA challenge"""
        # Simple math CAPTCHA for demo purposes
        # In production, use reCAPTCHA or similar service
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operation = random.choice(['+', '-', '*'])
        
        if operation == '+':
            answer = num1 + num2
            question = f"{num1} + {num2}"
        elif operation == '-':
            # Ensure positive result
            if num1 < num2:
                num1, num2 = num2, num1
            answer = num1 - num2
            question = f"{num1} - {num2}"
        else:  # *
            answer = num1 * num2
            question = f"{num1} × {num2}"
        
        # Store CAPTCHA data
        captcha_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        self.captcha_sessions[captcha_id] = {
            'answer': answer,
            'timestamp': time.time(),
            'browser_fp': session.get('browser_fingerprint')
        }
        
        return {
            'captcha_id': captcha_id,
            'question': question,
            'timeout': self.captcha_timeout
        }
    
    def verify_captcha(self, captcha_id, user_answer):
        """Verify CAPTCHA answer"""
        if captcha_id not in self.captcha_sessions:
            return False
        
        captcha_data = self.captcha_sessions[captcha_id]
        current_time = time.time()
        
        # Check timeout
        if current_time - captcha_data['timestamp'] > self.captcha_timeout:
            del self.captcha_sessions[captcha_id]
            return False
        
        # Check browser fingerprint
        if captcha_data['browser_fp'] != session.get('browser_fingerprint'):
            del self.captcha_sessions[captcha_id]
            return False
        
        # Check answer
        try:
            correct_answer = int(captcha_data['answer'])
            user_answer_int = int(user_answer)
            
            if correct_answer == user_answer_int:
                # CAPTCHA passed, trust browser and clean up
                self.trust_browser()
                del self.captcha_sessions[captcha_id]
                return True
            else:
                del self.captcha_sessions[captcha_id]
                return False
        except ValueError:
            del self.captcha_sessions[captcha_id]
            return False
    
    def _cleanup_old_entries(self):
        """Clean up old rate limiting and CAPTCHA entries"""
        current_time = time.time()
        
        # Clean up rate limiting entries
        for key in list(self.request_counts.keys()):
            window_start = current_time - self.rate_limit_window
            self.request_counts[key] = [
                req_time for req_time in self.request_counts[key] 
                if req_time > window_start
            ]
            if not self.request_counts[key]:
                del self.request_counts[key]
        
        # Clean up expired CAPTCHA sessions
        for captcha_id in list(self.captcha_sessions.keys()):
            captcha_data = self.captcha_sessions[captcha_id]
            if current_time - captcha_data['timestamp'] > self.captcha_timeout:
                del self.captcha_sessions[captcha_id]
        
        # Clean up expired trusted browsers
        for browser_fp in list(self.trusted_browsers.keys()):
            if current_time - self.trusted_browsers[browser_fp] > self.browser_trust_duration:
                del self.trusted_browsers[browser_fp]
    
    def get_security_status(self):
        """Get current security status for the client"""
        return {
            'is_trusted': self.is_browser_trusted(),
            'rate_limited': self.check_rate_limit(),
            'browser_fingerprint': session.get('browser_fingerprint', ''),
            'request_count': len(self.request_counts.get(self._get_rate_limit_key(), []))
        }

    # --- reCAPTCHA helpers ---
    def is_recaptcha_configured(self):
        site_key = os.getenv('RECAPTCHA_SITE_KEY', '').strip()
        secret_key = os.getenv('RECAPTCHA_SECRET_KEY', '').strip()
        return bool(site_key and secret_key)

    def verify_recaptcha(self, token, remote_ip=None):
        """Verify a reCAPTCHA token with Google's siteverify API"""
        secret_key = os.getenv('RECAPTCHA_SECRET_KEY', '').strip()
        if not secret_key or not token:
            return False
        try:
            data = {
                'secret': secret_key,
                'response': token
            }
            if remote_ip:
                data['remoteip'] = remote_ip
            response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data, timeout=5)
            result = response.json()
            return bool(result.get('success'))
        except Exception as e:
            logger.warning(f"reCAPTCHA verification error: {str(e)}")
            return False
