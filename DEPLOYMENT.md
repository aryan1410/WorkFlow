# Deployment Guide for Academic Project Tracker

This document provides comprehensive deployment instructions and dependency information for the Academic Project Tracker application.

## 📦 Dependencies

### Core Dependencies

The application uses the following Python packages (refer to `pyproject.toml` for exact versions):

#### Web Framework
- **Flask** - Lightweight WSGI web application framework
- **Flask-Login** - User session management and authentication
- **Flask-SQLAlchemy** - Flask integration for SQLAlchemy ORM
- **Flask-WTF** - Form handling with CSRF protection and file uploads

#### Database
- **SQLAlchemy** - Python SQL toolkit and Object Relational Mapper
- **psycopg2-binary** - PostgreSQL adapter for Python

#### Forms and Validation
- **WTForms** - Flexible forms validation and rendering library
- **email-validator** - Email address validation

#### Security and Utilities
- **Werkzeug** - WSGI utility library with password hashing
- **itsdangerous** - Secure token generation and data signing

#### Image Processing
- **Pillow (PIL)** - Python Imaging Library for thumbnail generation

#### Email Services (Optional)
- **sendgrid** - Email delivery service for notifications

#### Production Server
- **gunicorn** - Python WSGI HTTP Server for UNIX

### Installing Dependencies

#### Using UV (Recommended for Replit)
```bash
uv sync
```

#### Using pip
```bash
pip install -r requirements.txt
```

#### Manual Installation
```bash
pip install flask flask-login flask-sqlalchemy flask-wtf
pip install sqlalchemy psycopg2-binary
pip install wtforms email-validator
pip install werkzeug itsdangerous
pip install pillow sendgrid gunicorn
```

## 🚀 Deployment Options

### 1. Replit Deployment (Recommended)

The application is optimized for Replit deployment:

1. **Fork/Import the repository** to your Replit account
2. **Configure environment variables** in Replit Secrets:
   - `DATABASE_URL`: PostgreSQL connection string
   - `SESSION_SECRET`: Random secret key for Flask sessions
   - `SENDGRID_API_KEY`: (Optional) For email functionality

3. **Run the application**:
   - The `.replit` file is already configured
   - Click "Run" or use the command: `gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app`

4. **Database Setup**:
   - PostgreSQL is automatically provisioned in Replit
   - Tables are created automatically on first run

### 2. Heroku Deployment

1. **Create a Heroku app**:
   ```bash
   heroku create your-app-name
   ```

2. **Add PostgreSQL addon**:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set SESSION_SECRET="your-secret-key-here"
   heroku config:set SENDGRID_API_KEY="your-sendgrid-key" # optional
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

### 3. DigitalOcean App Platform

1. **Create new app** from GitHub repository
2. **Configure build settings**:
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `gunicorn --bind 0.0.0.0:$PORT main:app`
3. **Add database**: PostgreSQL managed database
4. **Set environment variables** in app settings

### 4. AWS Elastic Beanstalk

1. **Install EB CLI**:
   ```bash
   pip install awsebcli
   ```

2. **Initialize application**:
   ```bash
   eb init
   eb create production
   ```

3. **Configure database**: RDS PostgreSQL instance
4. **Set environment variables** in EB console

### 5. Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
```

Build and run:
```bash
docker build -t academic-tracker .
docker run -p 5000:5000 academic-tracker
```

### 6. VPS/Traditional Server

For Ubuntu/Debian servers:

1. **Install system dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip postgresql nginx
   ```

2. **Set up PostgreSQL**:
   ```bash
   sudo -u postgres createdb academic_tracker
   sudo -u postgres createuser tracker_user
   ```

3. **Install Python dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Configure Nginx** (optional, for reverse proxy):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Run with systemd** (production):
   Create `/etc/systemd/system/academic-tracker.service`:
   ```ini
   [Unit]
   Description=Academic Project Tracker
   After=network.target
   
   [Service]
   User=www-data
   WorkingDirectory=/path/to/app
   ExecStart=/usr/local/bin/gunicorn --bind 0.0.0.0:5000 main:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

## 🔧 Configuration

### Required Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
  - Format: `postgresql://username:password@host:port/database`
  - Example: `postgresql://tracker:password123@localhost:5432/academic_tracker`

- `SESSION_SECRET`: Flask session secret key
  - Generate: `python -c "import secrets; print(secrets.token_hex(32))"`

### Optional Environment Variables

- `SENDGRID_API_KEY`: For email functionality
- `FLASK_ENV`: Set to `production` for production deployment
- `FLASK_DEBUG`: Set to `False` for production

### Database Configuration

The application automatically creates all required tables on startup. For production deployments:

1. **Ensure PostgreSQL is running** and accessible
2. **Create database** with appropriate user permissions
3. **Set DATABASE_URL** environment variable
4. **Run application** - tables will be created automatically

### File Upload Configuration

- **Upload Directory**: `uploads/` (created automatically)
- **Max File Size**: 16MB (configurable in code)
- **Allowed Extensions**: Documents, images, archives
- **Permissions**: Ensure write permissions on upload directory

## 🛡️ Security Considerations

### Production Checklist

- [ ] Set `FLASK_DEBUG=False`
- [ ] Use strong `SESSION_SECRET`
- [ ] Configure HTTPS/SSL
- [ ] Set up database backups
- [ ] Configure log rotation
- [ ] Implement rate limiting
- [ ] Set up monitoring
- [ ] Regular security updates

### Recommended Security Headers

Add these headers via reverse proxy (Nginx/Apache):

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

## 📊 Monitoring and Maintenance

### Log Files
- **Application logs**: Check Flask/Gunicorn logs
- **Database logs**: Monitor PostgreSQL logs
- **Web server logs**: Nginx/Apache access logs

### Performance Monitoring
- Database connection pooling (already configured)
- Static file serving (configure web server)
- Application metrics (consider APM tools)

### Backup Strategy
- **Database backups**: Regular PostgreSQL dumps
- **File uploads**: Backup `uploads/` directory
- **Configuration**: Version control environment configs

## 🔄 Updates and Maintenance

### Updating the Application
1. **Backup database and files**
2. **Pull latest code changes**
3. **Update dependencies**: `uv sync` or `pip install -r requirements.txt`
4. **Restart application server**
5. **Test functionality**

### Database Migrations
The application uses SQLAlchemy's `create_all()` method. For schema changes:
1. **Backup existing data**
2. **Update models in `models.py`**
3. **Restart application** (tables updated automatically)
4. **For complex migrations**, consider using Flask-Migrate

---

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check DATABASE_URL format
   - Verify PostgreSQL is running
   - Confirm user permissions

2. **File Upload Issues**
   - Check upload directory permissions
   - Verify disk space
   - Review file size limits

3. **Session Issues**
   - Ensure SESSION_SECRET is set
   - Check session configuration
   - Verify cookie settings

4. **Import Errors**
   - Confirm all dependencies installed
   - Check Python version compatibility
   - Verify virtual environment activation

### Getting Help

- Check application logs first
- Review this deployment guide
- Consult Flask and PostgreSQL documentation
- Create issues in the repository for bugs

---

This deployment guide covers most common scenarios. Choose the deployment method that best fits your infrastructure and requirements.