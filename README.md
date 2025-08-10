# Academic Project Tracker

A comprehensive Flask-based web application designed to help students organize, manage, and track their academic projects with advanced collaborative features, study analytics, and productivity tools.

![Academic Project Tracker](https://img.shields.io/badge/Flask-2.3+-blue.svg) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-green.svg) ![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg) ![Python](https://img.shields.io/badge/Python-3.11+-yellow.svg)

## 🎯 Application Overview

The Academic Project Tracker is built for students who need a centralized platform to manage their academic workload effectively. Whether you're working on individual assignments or collaborating on group projects, this application provides the tools you need to stay organized, track progress, and maintain productivity throughout your academic journey.

### Key Use Cases
- **Project Management**: Organize academic projects by course with detailed tracking
- **Task Management**: Break down projects into manageable tasks with priority levels
- **Team Collaboration**: Work with classmates on group projects with role-based permissions
- **Study Analytics**: Track study sessions and analyze productivity patterns
- **File Management**: Upload and organize project-related files securely
- **Progress Monitoring**: Visualize project completion and study habits

## ✨ Features

### 📚 Core Project Management
- **Project Organization**: Create and manage academic projects categorized by course
- **Task Hierarchy**: Break down projects into tasks with priority levels (High, Medium, Low)
- **Status Tracking**: Monitor progress with project states (Planning, In Progress, Completed, On Hold)
- **Deadline Management**: Set and track project and task deadlines with overdue detection
- **Course Integration**: Organize projects by academic courses for better structure

### 🤝 Collaboration Features
- **Multi-User Projects**: Invite classmates to collaborate on group projects
- **Role-Based Permissions**: Assign roles (Owner, Collaborator, Viewer) with appropriate access levels
- **Project Comments**: Built-in discussion threads for team communication
- **Activity Logging**: Comprehensive audit trail of all project activities and changes
- **File Sharing**: Upload and share project files with team members

### 📊 Study Analytics & Productivity
- **Study Timer**: Built-in timer with real-time tracking for focused study sessions
- **Session Management**: Start, pause, and stop study sessions with automatic duration calculation
- **Analytics Dashboard**: Visualize study patterns with interactive Chart.js charts
- **Weekly Insights**: Track study habits over time with weekly breakdown charts
- **Project Time Analysis**: See time distribution across different projects
- **Progress Statistics**: Monitor total study time, session count, and average session length

### 📁 File Management
- **Secure File Upload**: Upload project files with size limits and type validation
- **Image Thumbnails**: Automatic thumbnail generation for image files
- **Organized Storage**: Files organized by project with structured directory system
- **File Access Control**: Permission-based file access for collaborative projects

### 🔍 Advanced Search
- **Full-Text Search**: Search across projects, tasks, files, and collaborators
- **Filtered Results**: Filter search results by content type (projects, tasks, files)
- **Smart Matching**: Search project titles, descriptions, course names, and task content

### 🔐 Authentication & Security
- **Custom User Authentication**: Secure registration and login system
- **Password Security**: Werkzeug-powered password hashing with strength validation
- **Session Management**: Flask sessions with CSRF protection
- **Email Verification**: Simplified registration process (verification removed for ease of use)
- **Data Isolation**: User-specific data access with proper authorization checks

## 🛠 Technology Stack

### Backend Framework
- **Flask 2.3+**: Lightweight WSGI web application framework
- **Python 3.11+**: Modern Python with type hints and performance improvements
- **Gunicorn**: Production-ready WSGI HTTP server

### Database & ORM
- **PostgreSQL 15+**: Robust relational database with advanced features
- **SQLAlchemy 2.0+**: Modern Python SQL toolkit and ORM
- **Flask-SQLAlchemy**: Flask integration for SQLAlchemy

### Frontend Technologies
- **Jinja2**: Server-side templating engine
- **Bootstrap 5.3**: Modern CSS framework with dark theme support
- **Feather Icons**: Lightweight icon library for consistent UI
- **Chart.js 4.0+**: Interactive charts for analytics visualization
- **Vanilla JavaScript**: Client-side interactions without heavy frameworks

### Authentication & Forms
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling with CSRF protection and file upload support
- **Werkzeug Security**: Password hashing and security utilities
- **Email-Validator**: Email address validation

### File Handling & Image Processing
- **Pillow (PIL)**: Python Imaging Library for thumbnail generation
- **Secure File Upload**: Size limits, type validation, and organized storage

### Development & Deployment
- **Flask Debug Mode**: Development server with auto-reload
- **Python Logging**: Comprehensive error tracking and debugging
- **Replit Integration**: Optimized for Replit deployment environment

## 📁 Repository Structure

```
academic-project-tracker/
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css          # Custom stylesheet overrides
│   └── js/
│       └── app.js             # Client-side JavaScript
├── templates/                  # Jinja2 templates
│   ├── auth/                  # Authentication templates
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── forgot_password.html
│   │   └── verification_required.html
│   ├── base.html              # Base template with navigation
│   ├── index.html             # Dashboard/home page
│   ├── landing.html           # Landing page for logged-out users
│   ├── project_detail.html    # Project detail view
│   ├── enhanced_project_detail.html # Enhanced project view with collaboration
│   ├── project_form.html      # Project creation/editing form
│   ├── courses.html           # Course management
│   ├── profile.html           # User profile page
│   ├── search.html            # Search results page
│   ├── study_analytics.html   # Analytics dashboard
│   ├── study_timer.html       # Study timer interface
│   └── 403.html              # Error page
├── uploads/                   # File upload storage directory
├── app.py                     # Flask application factory
├── main.py                    # Application entry point
├── routes.py                  # URL routes and view functions
├── models.py                  # Database models and schemas
├── auth.py                    # Authentication routes and logic
├── forms.py                   # WTForms form definitions
├── utils.py                   # Utility functions and helpers
├── replit.md                  # Project documentation and preferences
├── pyproject.toml            # Python dependencies and project metadata
├── uv.lock                   # Dependency lock file
├── .replit                   # Replit configuration
└── README.md                 # This file
```

### Key Files Explained

#### Core Application Files
- **`app.py`**: Flask application factory with database initialization
- **`main.py`**: Application entry point that imports the Flask app
- **`routes.py`**: All URL routes and view functions for the application
- **`models.py`**: SQLAlchemy database models and relationships
- **`auth.py`**: Authentication routes including login, register, logout
- **`forms.py`**: WTForms definitions for all application forms
- **`utils.py`**: Helper functions and utilities used across the application

#### Template Structure
- **`templates/base.html`**: Master template with navigation, flash messages, and layout
- **`templates/index.html`**: Dashboard showing project overview and recent activity
- **`templates/project_detail.html`**: Detailed project view with tasks and collaboration
- **`templates/study_analytics.html`**: Analytics dashboard with charts and statistics
- **`templates/study_timer.html`**: Real-time study timer interface

#### Configuration Files
- **`pyproject.toml`**: Python project configuration and dependencies
- **`.replit`**: Replit-specific configuration for hosting
- **`replit.md`**: Project documentation and user preferences

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- PostgreSQL 15 or higher
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd academic-project-tracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # or using uv
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   export DATABASE_URL="postgresql://username:password@localhost/academic_tracker"
   export SESSION_SECRET="your-secret-key-here"
   ```

4. **Initialize the database**
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

5. **Run the application**
   ```bash
   python main.py
   # or for production
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

6. **Access the application**
   - Open your browser to `http://localhost:5000`
   - Register a new account or login with existing credentials

### Quick Start Guide

1. **Create Your First Project**
   - Click "New Project" in the navigation
   - Fill in project details, select a course, and set deadline
   - Add tasks to break down the project work

2. **Start a Study Session**
   - Navigate to "Study Timer" from the More menu
   - Select a project and click "Start Session"
   - Use the timer to track focused study time

3. **Collaborate with Classmates**
   - From any project, click "Manage Collaborators"
   - Invite team members by email with appropriate permissions
   - Use comments to communicate and activity logs to track changes

4. **Analyze Your Progress**
   - Visit "Study Analytics" to see your productivity patterns
   - Review weekly study charts and project time breakdowns
   - Monitor your study habits and session statistics

## 🎨 User Interface

The application features a modern, responsive design built with Bootstrap 5 and a dark theme optimized for extended study sessions. Key UI elements include:

- **Responsive Navigation**: Collapsible navbar with user menu and feature access
- **Dashboard Cards**: Quick overview of projects, tasks, and recent activity
- **Interactive Charts**: Study analytics with hoverable data points and tooltips
- **Modal Dialogs**: Seamless forms for adding collaborators, comments, and tasks
- **Progress Indicators**: Visual progress bars for project completion
- **File Thumbnails**: Image previews for uploaded project files
- **Real-time Timer**: Large, easy-to-read study session timer

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Flask session secret key
- `SENDGRID_API_KEY`: Email service API key (optional)

### File Upload Settings
- Maximum file size: 16MB
- Allowed file types: Documents, images, archives
- Storage location: `uploads/` directory
- Thumbnail generation: Automatic for image files

### Database Configuration
- Connection pooling with 300-second recycle
- Pre-ping enabled for connection health checks
- Automatic table creation on startup

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with proper documentation
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines
- Follow PEP 8 Python style guidelines
- Add docstrings to all functions and classes
- Update README.md for significant feature additions
- Test thoroughly before submitting pull requests

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋 Support

If you encounter any issues or have questions:

1. Check the existing issues in the repository
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce
4. For feature requests, provide clear use cases and benefits

## 🔮 Future Enhancements

- **Mobile App**: React Native companion app for mobile access
- **Calendar Integration**: Sync with Google Calendar and other calendar services
- **Advanced Analytics**: More detailed productivity insights and recommendations
- **Export Features**: PDF reports and data export functionality
- **Integration APIs**: Connect with learning management systems
- **Notification System**: Email and push notifications for deadlines and updates
- **Template System**: Project templates for common assignment types
- **Time Blocking**: Integration with time management methodologies

---

Built with ❤️ for students, by students. Happy studying! 📚