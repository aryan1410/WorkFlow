# Academic Project Tracker

## Overview

Academic Project Tracker is a comprehensive Flask-based web application designed to help students manage their academic projects and tasks with advanced collaborative features. The application provides a dashboard for tracking project progress, deadlines, and task completion across different courses. It features an intuitive interface for creating, editing, and organizing projects with associated tasks, status tracking, deadline management, file uploads, team collaboration, email verification, and progress analytics.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templating with Flask for server-side rendering
- **UI Framework**: Bootstrap 5 with dark theme support for responsive design
- **Icons**: Feather Icons for consistent iconography
- **JavaScript**: Vanilla JavaScript for client-side interactions and form validation
- **Styling**: Custom CSS overrides on top of Bootstrap for application-specific styling

### Backend Architecture
- **Web Framework**: Flask as the lightweight WSGI web application framework
- **Application Structure**: Modular design with separate files for routes, models, and app configuration
- **Session Management**: Flask sessions with configurable secret key for security
- **Data Models**: Object-oriented approach with Python classes for Projects and Tasks
- **Status Management**: Enums for consistent status and priority handling (ProjectStatus, TaskStatus, Priority)

### Data Storage Solution
- **Storage Type**: PostgreSQL database with SQLAlchemy ORM
- **Data Persistence**: Full database persistence with relationship management
- **User Data Isolation**: All user data (projects, tasks, courses, study sessions) linked to authenticated users
- **Model Architecture**: SQLAlchemy models with proper foreign key relationships and cascading deletes
- **Database Features**: Indexes on email fields, enum constraints for status fields, timestamp tracking
- **File Storage**: Local file system storage with organized project-based directory structure
- **Collaborative Data**: ProjectCollaborator, ProjectComment, ProjectFile, and ActivityLog models for team features
- **Permission Controls**: Database-level access control with user role validation

### Authentication and Authorization
- **Authentication System**: Custom user authentication with Flask-Login
- **User Registration**: Email-based registration with encrypted password storage
- **Password Security**: Werkzeug password hashing with strength validation requirements
- **Email Verification**: Token-based email verification system (placeholder implementation)
- **Session Management**: Flask sessions with CSRF protection via Flask-WTF
- **Access Control**: User-specific data isolation - users can only access their own projects and data
- **Forms Security**: All forms protected with CSRF tokens and server-side validation

### Application Features
- **Project Management**: CRUD operations for academic projects with course categorization
- **Task Management**: Hierarchical task system linked to projects with priority levels
- **Status Tracking**: Multiple status states for both projects and tasks
- **Dashboard Analytics**: Project statistics and progress visualization
- **Deadline Management**: Date-based deadline tracking with overdue detection
- **Course Organization**: Projects grouped by academic course or category
- **File Upload System**: Secure file upload with size limits, type validation, and thumbnail generation for images
- **Collaborative Features**: Multi-user project collaboration with role-based permissions (owner, collaborator, viewer)
- **Email Verification**: SendGrid-powered email verification system for user registration
- **Comment System**: Project-based discussion threads for team communication
- **Activity Logging**: Comprehensive audit trail of all project activities and changes
- **Advanced Search**: Full-text search across projects, tasks, files, and collaborators
- **Permission Management**: Granular access control for project viewing and editing

## External Dependencies

### Frontend Dependencies
- **Bootstrap 5**: CSS framework loaded via CDN for responsive UI components
- **Feather Icons**: Icon library loaded via CDN for consistent iconography
- **Bootstrap JavaScript**: For interactive components like modals and alerts

### Backend Dependencies
- **Flask**: Core web framework for Python
- **Flask-Login**: User session management and authentication
- **Flask-WTF**: Form handling and CSRF protection with file upload support
- **Flask-SQLAlchemy**: Database ORM for PostgreSQL
- **Werkzeug**: Password hashing and security utilities
- **email-validator**: Email address validation
- **itsdangerous**: Secure token generation for email verification
- **SendGrid**: Email delivery service for verification and notifications
- **Pillow**: Image processing for thumbnail generation and file handling
- **Python Standard Library**: datetime, enum, os, logging, secrets modules for core functionality

### Development Dependencies
- **Flask Debug Mode**: Enabled for development with automatic reloading
- **Python Logging**: Configured for debugging and error tracking

### Infrastructure
- **Deployment**: Configured for Replit environment with host='0.0.0.0' and port=5000
- **Environment Variables**: Support for SESSION_SECRET environment variable
- **Static Assets**: CSS and JavaScript files served via Flask static file handling

Note: The application currently uses in-memory storage and lacks persistent database integration, making it suitable for development and testing but requiring database implementation for production use.