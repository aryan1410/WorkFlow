import os
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import flash, redirect, request, render_template, url_for, session
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from email_validator import validate_email, EmailNotValidError

from app import app, db
from models import User


# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Email verification setup
serializer = URLSafeTimedSerializer(app.secret_key)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)


def generate_verification_url(email):
    """Generate email verification URL"""
    token = serializer.dumps(email, salt='email-verification')
    return url_for('verify_email', token=token, _external=True)


def verify_email_token(token, max_age=3600):
    """Verify email verification token (1 hour expiry)"""
    try:
        email = serializer.loads(token, salt='email-verification', max_age=max_age)
        return email
    except (SignatureExpired, BadSignature):
        return None


def generate_reset_token():
    """Generate password reset token"""
    return secrets.token_urlsafe(32)


def send_verification_email(user_email, verification_url):
    """Send verification email - placeholder for now"""
    # This is where you would integrate with SendGrid or another email service
    # For now, we'll just print the URL (in production, send actual email)
    print(f"Verification email for {user_email}: {verification_url}")
    return True


def send_password_reset_email(user_email, reset_url):
    """Send password reset email - placeholder for now"""
    # This is where you would integrate with SendGrid or another email service
    print(f"Password reset email for {user_email}: {reset_url}")
    return True


def verify_email_required(f):
    """Decorator to require email verification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and not current_user.is_verified:
            flash('Please verify your email address to access this feature.', 'warning')
            return redirect(url_for('verification_required'))
        return f(*args, **kwargs)
    return decorated_function


def validate_email_address(email):
    """Validate email address format"""
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter."
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number."
    
    return True, "Password is strong."