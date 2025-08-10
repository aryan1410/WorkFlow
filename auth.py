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
    """Send verification email using SendGrid"""
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        sg = SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        
        message = Mail(
            from_email='noreply@academictracker.app',
            to_emails=user_email,
            subject='Verify Your Academic Project Tracker Account',
            html_content=f'''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #333;">Welcome to Academic Project Tracker!</h2>
                <p>Thank you for registering. Please verify your email address by clicking the button below:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">Verify Email Address</a>
                </div>
                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666;">{verification_url}</p>
                <p style="color: #666; font-size: 14px;">This link will expire in 1 hour for security reasons.</p>
            </div>
            '''
        )
        
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        print(f"Email sending failed: {e}")
        # Fallback: print to console for development
        print(f"Verification email for {user_email}: {verification_url}")
        return True


def send_password_reset_email(user_email, reset_url):
    """Send password reset email using SendGrid"""
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        sg = SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        
        message = Mail(
            from_email='noreply@academictracker.app',
            to_emails=user_email,
            subject='Reset Your Academic Project Tracker Password',
            html_content=f'''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #333;">Password Reset Request</h2>
                <p>You requested to reset your password. Click the button below to create a new password:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background-color: #dc3545; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">Reset Password</a>
                </div>
                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666;">{reset_url}</p>
                <p style="color: #666; font-size: 14px;">This link will expire in 1 hour for security reasons.</p>
                <p style="color: #666; font-size: 14px;">If you didn't request this, please ignore this email.</p>
            </div>
            '''
        )
        
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        print(f"Email sending failed: {e}")
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