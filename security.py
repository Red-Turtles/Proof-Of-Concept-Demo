"""
Security module for WildID
Handles session management and basic security features
"""

import hashlib
import json
import random
import secrets
import time
from datetime import timedelta
from flask import request, session
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self, app=None):
        self.app = app
        self.captchas = {}
        self.rate_limit_threshold = 2
        self.rate_limit_window = 600  # seconds
        self.captcha_ttl = 300  # seconds
        self.max_captcha_attempts = 3
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the security manager with Flask app"""
        self.app = app
        
        # Load security configuration
        self.rate_limit_threshold = int(app.config.get('SECURITY_RATE_LIMIT_THRESHOLD', 2))
        self.rate_limit_window = int(app.config.get('SECURITY_RATE_LIMIT_WINDOW_SECONDS', 600))
        self.captcha_ttl = int(app.config.get('SECURITY_CAPTCHA_TTL_SECONDS', 300))
        self.max_captcha_attempts = int(app.config.get('SECURITY_CAPTCHA_MAX_ATTEMPTS', 3))
        
        # Set up session configuration without overriding existing secure settings
        app.config.setdefault('SESSION_TYPE', 'filesystem')
        if not app.config.get('PERMANENT_SESSION_LIFETIME'):
            app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

        if not app.config.get('SECRET_KEY'):
            raise RuntimeError('SECRET_KEY must be configured before initializing SecurityManager.')
        
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
        # Check for forwarded headers (proxies, load balancers, etc.)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Fallback to remote address
        return request.remote_addr

    def _initial_state(self):
        now = time.time()
        return {
            'is_trusted': False,
            'request_count': 0,
            'window_started': now,
            'rate_limited': False,
            'last_captcha_passed': None
        }

    def _get_state(self):
        state = session.get('security_state')
        if not isinstance(state, dict):
            state = self._initial_state()
        else:
            state.setdefault('is_trusted', False)
            state.setdefault('request_count', 0)
            state.setdefault('window_started', time.time())
            state.setdefault('rate_limited', False)
            state.setdefault('last_captcha_passed', None)
        self._save_state(state)
        return state

    def _save_state(self, state):
        session['security_state'] = state
        session.modified = True

    def _reset_window_if_needed(self, state):
        now = time.time()
        window_started = state.get('window_started', now)
        if now - window_started >= self.rate_limit_window:
            state['request_count'] = 0
            state['window_started'] = now
            if not state.get('is_trusted'):
                state['rate_limited'] = False

    def record_request(self, action):
        if action != 'identify':
            return
        state = self._get_state()
        self._reset_window_if_needed(state)

        if not state.get('is_trusted'):
            state['request_count'] = state.get('request_count', 0) + 1
            if state['request_count'] >= self.rate_limit_threshold:
                state['rate_limited'] = True

        self._save_state(state)

    def can_proceed(self, action):
        if action != 'identify':
            return True, None

        state = self._get_state()
        self._reset_window_if_needed(state)

        if state.get('is_trusted'):
            return True, None

        if state.get('rate_limited'):
            return False, 'captcha_required'

        return True, None

    def get_status(self):
        state = self._get_state()
        self._reset_window_if_needed(state)
        self._save_state(state)

        now = time.time()
        window_started = state.get('window_started', now)
        window_expires_in = max(0, int(self.rate_limit_window - (now - window_started)))

        status = {
            'is_trusted': state.get('is_trusted', False),
            'request_count': state.get('request_count', 0),
            'rate_limited': state.get('rate_limited', False),
            'captcha_required': state.get('rate_limited', False),
            'window_expires_in': window_expires_in,
            'rate_limit_threshold': self.rate_limit_threshold
        }
        return status

    def _cleanup_captchas(self):
        now = time.time()
        expired = [captcha_id for captcha_id, data in self.captchas.items() if data['expires_at'] <= now]
        for captcha_id in expired:
            self.captchas.pop(captcha_id, None)

    def create_captcha(self):
        self._cleanup_captchas()

        operands = list(range(1, 10))
        a = random.choice(operands)
        b = random.choice(operands)
        operations = [('+', lambda x, y: x + y), ('-', lambda x, y: x - y), ('×', lambda x, y: x * y)]
        op_symbol, operation = random.choice(operations)

        if op_symbol == '-' and a < b:
            a, b = b, a

        answer = operation(a, b)
        question = f"{a} {op_symbol} {b}"

        captcha_id = secrets.token_urlsafe(8)
        answer_hash = hashlib.sha256(str(answer).encode()).hexdigest()

        self.captchas[captcha_id] = {
            'answer_hash': answer_hash,
            'expires_at': time.time() + self.captcha_ttl,
            'attempts': 0
        }

        state = self._get_state()
        if not state.get('is_trusted'):
            state['rate_limited'] = True
            self._save_state(state)

        return captcha_id, question

    def verify_captcha(self, captcha_id, answer):
        self._cleanup_captchas()

        captcha = self.captchas.get(captcha_id)
        if not captcha:
            return False, 'invalid_captcha'

        if captcha['expires_at'] <= time.time():
            self.captchas.pop(captcha_id, None)
            return False, 'expired_captcha'

        answer_hash = hashlib.sha256(str(answer).strip().encode()).hexdigest()

        if not secrets.compare_digest(answer_hash, captcha['answer_hash']):
            captcha['attempts'] += 1
            if captcha['attempts'] >= self.max_captcha_attempts:
                self.captchas.pop(captcha_id, None)
                return False, 'too_many_attempts'
            return False, 'incorrect_answer'

        # Correct answer
        self.captchas.pop(captcha_id, None)
        state = self._get_state()
        state['is_trusted'] = True
        state['rate_limited'] = False
        state['request_count'] = 0
        state['last_captcha_passed'] = time.time()
        self._save_state(state)

        return True, None
