"""
Authentication module for WildID
Handles passwordless email authentication with magic links
"""

import secrets
from datetime import datetime, timedelta
from flask import session, request
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import logging

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
        
        logger.info("Auth manager initialized")
    
    def generate_magic_link_token(self, email):
        """Generate a secure token for magic link"""
        # Generate a secure random token
        token = secrets.token_urlsafe(32)
        
        # Calculate expiration (15 minutes from now)
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        
        # Store token in database
        login_token = LoginToken(
            email=email.lower().strip(),
            token=token,
            expires_at=expires_at
        )
        
        db.session.add(login_token)
        db.session.commit()
        
        logger.info(f"Generated magic link token for {email}")
        return token
    
    def verify_magic_link_token(self, token):
        """Verify a magic link token and return email if valid"""
        login_token = LoginToken.query.filter_by(token=token).first()
        
        if not login_token:
            logger.warning(f"Invalid token attempted: {token[:10]}...")
            return None
        
        if not login_token.is_valid():
            logger.warning(f"Expired or used token attempted: {token[:10]}...")
            return None
        
        # Mark token as used
        login_token.used = True
        login_token.used_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Valid token verified for {login_token.email}")
        return login_token.email
    
    def send_magic_link(self, email, token, request_host):
        """Send magic link email to user"""
        # Construct magic link URL
        magic_link = f"http://{request_host}/auth/verify?token={token}"
        
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
    
    def create_or_get_user(self, email):
        """Create a new user or get existing user by email"""
        email = email.lower().strip()
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create new user
            user = User(email=email)
            db.session.add(user)
            db.session.commit()
            logger.info(f"New user created: {email}")
        
        return user
    
    def login_user(self, user):
        """Log in a user by setting session data"""
        session['user_id'] = user.id
        session['user_email'] = user.email
        session.permanent = True
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"User logged in: {user.email}")
    
    def logout_user(self):
        """Log out the current user"""
        user_email = session.get('user_email')
        session.pop('user_id', None)
        session.pop('user_email', None)
        
        if user_email:
            logger.info(f"User logged out: {user_email}")
    
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

