import os
import secrets
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def generate_filename(original_filename):
    """Generate a unique filename while preserving extension"""
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    unique_filename = secrets.token_urlsafe(16) + '.' + ext if ext else secrets.token_urlsafe(16)
    return unique_filename


def save_uploaded_file(file, project_id, user_id):
    """Save uploaded file and return file info"""
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        raise ValueError("File type not allowed")
    
    # Generate unique filename
    secure_name = secure_filename(file.filename)
    unique_filename = generate_filename(secure_name)
    
    # Create project-specific directory
    project_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], f'project_{project_id}')
    os.makedirs(project_dir, exist_ok=True)
    
    file_path = os.path.join(project_dir, unique_filename)
    
    # Save file
    file.save(file_path)
    
    # Get file info
    file_size = os.path.getsize(file_path)
    file_type = file.content_type or 'application/octet-stream'
    
    # Create thumbnail for images
    if file_type.startswith('image/'):
        try:
            create_thumbnail(file_path, project_dir)
        except Exception as e:
            print(f"Thumbnail creation failed: {e}")
    
    return {
        'filename': unique_filename,
        'original_filename': secure_name,
        'file_path': file_path,
        'file_size': file_size,
        'file_type': file_type
    }


def create_thumbnail(file_path, project_dir):
    """Create thumbnail for image files"""
    try:
        with Image.open(file_path) as img:
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            
            # Save thumbnail
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            thumb_filename = f"{name}_thumb{ext}"
            thumb_path = os.path.join(project_dir, thumb_filename)
            
            img.save(thumb_path, optimize=True, quality=85)
            return thumb_path
    except Exception as e:
        print(f"Thumbnail creation failed: {e}")
        return None


def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} TB"


def get_file_icon(file_type):
    """Get appropriate icon for file type"""
    if file_type.startswith('image/'):
        return 'image'
    elif file_type.startswith('video/'):
        return 'video'
    elif file_type.startswith('audio/'):
        return 'music'
    elif 'pdf' in file_type:
        return 'file-text'
    elif any(x in file_type for x in ['document', 'word']):
        return 'file-text'
    elif any(x in file_type for x in ['spreadsheet', 'excel']):
        return 'grid'
    elif any(x in file_type for x in ['presentation', 'powerpoint']):
        return 'monitor'
    elif 'zip' in file_type or 'rar' in file_type:
        return 'archive'
    else:
        return 'file'


def log_activity(user_id, action, entity_type, entity_id, description=None, project_id=None):
    """Log user activity"""
    from app import db
    from models import ActivityLog
    
    activity = ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        project_id=project_id
    )
    
    db.session.add(activity)
    db.session.commit()
    return activity