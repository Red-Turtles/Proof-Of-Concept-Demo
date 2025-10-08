"""
Production WSGI entrypoint for the Flask app with hardened defaults.
This file provides a plug-and-play wrapper without modifying existing app code.
"""

import os
from app import app as flask_app
from flask_cors import CORS


def configure_security(app):
    # Respect existing headers set in app.py; only set if missing
    @app.after_request
    def _ensure_security_headers(response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'DENY')
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        # Keep a conservative CSP if not already present
        response.headers.setdefault('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com; style-src 'self' 'unsafe-inline' https://unpkg.com; img-src 'self' data: https://*.tile.openstreetmap.org;")
        return response

    # Cookies hardening via config (no code changes to original app)
    app.config.setdefault('SESSION_COOKIE_HTTPONLY', True)
    app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')
    # If running behind TLS/ingress, allow overriding via env
    session_cookie_secure = os.getenv('SESSION_COOKIE_SECURE', 'true').lower() == 'true'
    app.config['SESSION_COOKIE_SECURE'] = session_cookie_secure


def configure_cors(app):
    # Restrict CORS to explicit origins if provided; otherwise default to none
    allowed_origins = os.getenv('ALLOWED_ORIGINS')
    if allowed_origins:
        origins = [o.strip() for o in allowed_origins.split(',') if o.strip()]
        CORS(app, resources={r"/api/*": {"origins": origins}}, supports_credentials=True)
    else:
        # Disable broad CORS; only allow same-origin by not enabling CORS on API
        pass


def create_app():
    app = flask_app
    # Ensure debug is disabled in production runtime
    app.config.setdefault('ENV', 'production')
    app.config['DEBUG'] = False

    # Ensure a strong secret key is present; do not overwrite if already set
    if not app.config.get('SECRET_KEY') or app.config['SECRET_KEY'].startswith('dev-secret-key'):
        env_secret = os.getenv('SECRET_KEY')
        if env_secret:
            app.config['SECRET_KEY'] = env_secret

    configure_security(app)
    configure_cors(app)
    return app


application = create_app()

