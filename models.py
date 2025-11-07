"""
Database models for WildID
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class User(db.Model):
    """User model for passwordless authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    identifications = db.relationship('Identification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Identification(db.Model):
    """Model to store animal identification history"""
    __tablename__ = 'identifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Identification data
    species = db.Column(db.String(255))
    common_name = db.Column(db.String(255))
    animal_type = db.Column(db.String(100))
    conservation_status = db.Column(db.String(100))
    confidence = db.Column(db.String(50))
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Image data (stored as base64)
    image_data = db.Column(db.Text)
    image_mime = db.Column(db.String(50))
    
    # Full result JSON for reference
    result_json = db.Column(db.Text)
    
    # User feedback
    user_feedback = db.Column(db.String(20))  # 'correct', 'incorrect', or None
    feedback_comment = db.Column(db.Text)  # Optional user comment
    feedback_at = db.Column(db.DateTime)  # When feedback was given
    
    def __repr__(self):
        return f'<Identification {self.id}: {self.common_name or self.species}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'species': self.species,
            'common_name': self.common_name,
            'animal_type': self.animal_type,
            'conservation_status': self.conservation_status,
            'confidence': self.confidence,
            'description': self.description,
            'notes': self.notes,
            'image_data': self.image_data,
            'image_mime': self.image_mime
        }
    
    def get_result_json(self):
        """Parse and return result JSON"""
        if self.result_json:
            try:
                return json.loads(self.result_json)
            except:
                return {}
        return {}


class UserBadge(db.Model):
    """Badges earned by users for achievements"""
    __tablename__ = 'user_badges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    badge_key = db.Column(db.String(64), nullable=False)
    badge_name = db.Column(db.String(120), nullable=False)
    badge_description = db.Column(db.String(255))
    badge_icon = db.Column(db.String(8), nullable=False, default='🏅')
    awarded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    metadata_json = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'badge_key', name='uq_user_badge'),
    )

    def __repr__(self):
        return f'<UserBadge {self.badge_key} for user {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'badge_key': self.badge_key,
            'badge_name': self.badge_name,
            'badge_description': self.badge_description,
            'badge_icon': self.badge_icon,
            'awarded_at': self.awarded_at.isoformat() if self.awarded_at else None,
            'metadata': self.metadata_json
        }

class LoginToken(db.Model):
    """Model to store magic link tokens for passwordless login"""
    __tablename__ = 'login_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    used = db.Column(db.Boolean, default=False, nullable=False)
    used_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<LoginToken {self.email}>'
    
    def is_valid(self):
        """Check if token is still valid"""
        return not self.used and datetime.utcnow() < self.expires_at

