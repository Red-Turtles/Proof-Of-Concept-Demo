"""
Authentication module for WildID
Handles passwordless email authentication with magic links
"""

import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from flask import session, request
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import logging
import re

from models import db, User, LoginToken

logger = logging.getLogger(__name__)
mail = Mail()

class AuthManager:
    def __init__(self, app=None):
        self.app = app
        self.token_serializer = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the auth manager with Flask app"""
        self.app = app
        
        # Initialize mail
        mail.init_app(app)
        
        # Create token serializer
        self.token_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        self.remember_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='remember-token')
        
        logger.info("Auth manager initialized")
    
    def _hash_token(self, token):
        return hashlib.sha256(token.encode()).hexdigest()

    def _build_magic_link(self, token):
        base_url = self.app.config.get('MAGIC_LINK_BASE_URL')
        preferred_scheme = self.app.config.get('PREFERRED_URL_SCHEME', 'https')

        if base_url:
            base_url = base_url.rstrip('/')
        else:
            server_name = self.app.config.get('SERVER_NAME')
            if server_name:
                base_url = f"{preferred_scheme}://{server_name.rstrip('/')}"
            else:
                host = request.host
                allowed_hosts = self.app.config.get('ALLOWED_HOSTS', [])
                if not host:
                    raise ValueError('Unable to determine request host for magic link')

                hostname = host.split(':')[0]
                port = host.split(':')[1] if ':' in host else None

                if allowed_hosts and hostname not in allowed_hosts:
                    raise ValueError('Host header not allowed for magic link generation')

                port_suffix = f":{port}" if port else ''
                base_url = f"{preferred_scheme}://{hostname}{port_suffix}"

        query = urlencode({'token': token})
        return f"{base_url}/auth/verify?{query}"

    def generate_magic_link_token(self, email):
        """Generate a secure token for magic link"""
        # Generate a secure random token
        token = secrets.token_urlsafe(32)
        
        # Calculate expiration (15 minutes from now)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        # Store token in database
        login_token = LoginToken(
            email=email.lower().strip(),
            token=self._hash_token(token),
            expires_at=expires_at
        )
        
        db.session.add(login_token)
        db.session.commit()
        
        logger.info(f"Generated magic link token for {email}")
        return token
    
    def verify_magic_link_token(self, token):
        """Verify a magic link token and return email if valid"""
        token_hash = self._hash_token(token)
        login_token = LoginToken.query.filter_by(token=token_hash).first()

        # Backwards compatibility with previous plaintext tokens
        if not login_token:
            legacy_token = LoginToken.query.filter_by(token=token).first()
            if legacy_token:
                logger.warning('Legacy plaintext login token verified - upgrading to hashed storage')
                legacy_token.token = self._hash_token(token)
                db.session.commit()
                login_token = legacy_token
        
        if not login_token:
            logger.warning(f"Invalid token attempted: {token[:10]}...")
            return None
        
        if not login_token.is_valid():
            logger.warning(f"Expired or used token attempted: {token[:10]}...")
            return None
        
        # Mark token as used
        login_token.used = True
        login_token.used_at = datetime.now(timezone.utc)
        db.session.commit()
        
        logger.info(f"Valid token verified for {login_token.email}")
        return login_token.email
    
    def send_magic_link(self, email, token):
        """Send magic link email to user"""
        # Construct magic link URL
        try:
            magic_link = self._build_magic_link(token)
        except ValueError as exc:
            logger.error(f"Failed to build magic link URL: {exc}")
            return False
        
        # For development, also log the link
        if self.app.config.get('ENV') == 'development' or self.app.config.get('DEBUG'):
            logger.info(f"Magic link for {email}: {magic_link}")
            print(f"\n{'='*60}")
            print(f"🔗 MAGIC LINK FOR {email}")
            print(f"{'='*60}")
            print(f"{magic_link}")
            print(f"{'='*60}\n")
        
        try:
            # Send email
            msg = Message(
                subject="Sign in to WildID",
                sender=self.app.config.get('MAIL_DEFAULT_SENDER', 'noreply@wildid.app'),
                recipients=[email]
            )
            
            msg.body = f"""
Hello!

Click the link below to sign in to WildID:

{magic_link}

This link will expire in 15 minutes and can only be used once.

If you didn't request this link, you can safely ignore this email.

Best regards,
The WildID Team
            """
            
            msg.html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #4CAF50; color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Sign in to WildID</h2>
        <p>Hello!</p>
        <p>Click the button below to sign in to your WildID account:</p>
        <a href="{magic_link}" class="button">Sign In to WildID</a>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #666;">{magic_link}</p>
        <p>This link will expire in 15 minutes and can only be used once.</p>
        <div class="footer">
            <p>If you didn't request this link, you can safely ignore this email.</p>
            <p>Best regards,<br>The WildID Team</p>
        </div>
    </div>
</body>
</html>
            """
            
            mail.send(msg)
            logger.info(f"Magic link email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send magic link email to {email}: {str(e)}")
            return False
    
    def _generate_unique_username(self, email):
        seed = email.split('@')[0]
        base = re.sub(r'[^a-z0-9]+', '', seed.lower())
        if not base:
            base = 'wildid'

        candidate = base
        suffix = 2
        while User.query.filter_by(username=candidate).first():
            candidate = f"{base}{suffix}"
            suffix += 1
        return candidate

    def create_or_get_user(self, email):
        """Create a new user or get existing user by email"""
        email = email.lower().strip()
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create new user
            user = User(email=email)
            user.username = self._generate_unique_username(email)
            db.session.add(user)
            db.session.commit()
            logger.info(f"New user created: {email}")
        elif not user.username:
            user.username = self._generate_unique_username(email)
            db.session.commit()
        
        return user
    
    def login_user(self, user, update_last_login=True):
        """Log in a user by setting session data"""
        session['user_id'] = user.id
        session['user_email'] = user.email
        session.permanent = True
        session.modified = True
        
        if update_last_login:
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
        
        logger.info(f"User logged in: {user.email}")
    
    def logout_user(self):
        """Log out the current user"""
        user_email = session.get('user_email')
        session.pop('user_id', None)
        session.pop('user_email', None)
        session.modified = True
        
        if user_email:
            logger.info(f"User logged out: {user_email}")

    def set_remember_cookie(self, response, user):
        token = self.remember_serializer.dumps({
            'user_id': user.id,
            'email': user.email
        })
        response.set_cookie(
            self.app.config.get('REMEMBER_COOKIE_NAME', 'wildid_remember'),
            token,
            max_age=self.app.config.get('REMEMBER_COOKIE_DURATION', 60 * 60 * 24 * 30),
            secure=self.app.config.get('REMEMBER_COOKIE_SECURE', False),
            httponly=True,
            samesite=self.app.config.get('REMEMBER_COOKIE_SAMESITE', 'Lax')
        )

    def clear_remember_cookie(self, response):
        response.delete_cookie(self.app.config.get('REMEMBER_COOKIE_NAME', 'wildid_remember'))

    def _load_user_from_remember_cookie(self):
        token = request.cookies.get(self.app.config.get('REMEMBER_COOKIE_NAME', 'wildid_remember'))
        if not token:
            return None

        try:
            data = self.remember_serializer.loads(
                token,
                max_age=self.app.config.get('REMEMBER_COOKIE_DURATION', 60 * 60 * 24 * 30)
            )
        except (BadSignature, SignatureExpired):
            return None

        user_id = data.get('user_id')
        if not user_id:
            return None

        return User.query.get(user_id)

    def ensure_user_from_remember_cookie(self):
        if session.get('user_id'):
            return

        user = self._load_user_from_remember_cookie()
        if user and user.is_active:
            self.login_user(user, update_last_login=False)
    
    def get_current_user(self):
        """Get the currently logged in user"""
        user_id = session.get('user_id')
        
        if not user_id:
            return None
        
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            # Clear invalid session
            self.logout_user()
            return None
        
        return user
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return self.get_current_user() is not None
    
    def require_auth(self):
        """Decorator helper to require authentication"""
        return self.is_authenticated()

