# Academic Project Tracker

## Overview

Academic Project Tracker is a Flask-based web application designed to help students manage their academic projects and tasks. The application provides a dashboard for tracking project progress, deadlines, and task completion across different courses. It features an intuitive interface for creating, editing, and organizing projects with associated tasks, status tracking, and deadline management.

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
- **Storage Type**: In-memory storage using Flask application configuration
- **Data Structure**: Lists stored in app.config for projects and tasks with auto-incrementing counters
- **Data Persistence**: No persistent database - data resets on application restart (MVP approach)
- **Model Serialization**: Built-in to_dict() and from_dict() methods for data conversion

### Authentication and Authorization
- **Current State**: No authentication system implemented
- **Session Security**: Basic session management with secret key configuration
- **Access Control**: Open access to all features without user restrictions

### Application Features
- **Project Management**: CRUD operations for academic projects with course categorization
- **Task Management**: Hierarchical task system linked to projects with priority levels
- **Status Tracking**: Multiple status states for both projects and tasks
- **Dashboard Analytics**: Project statistics and progress visualization
- **Deadline Management**: Date-based deadline tracking with overdue detection
- **Course Organization**: Projects grouped by academic course or category

## External Dependencies

### Frontend Dependencies
- **Bootstrap 5**: CSS framework loaded via CDN for responsive UI components
- **Feather Icons**: Icon library loaded via CDN for consistent iconography
- **Bootstrap JavaScript**: For interactive components like modals and alerts

### Backend Dependencies
- **Flask**: Core web framework for Python
- **Python Standard Library**: datetime, enum, os, logging modules for core functionality

### Development Dependencies
- **Flask Debug Mode**: Enabled for development with automatic reloading
- **Python Logging**: Configured for debugging and error tracking

### Infrastructure
- **Deployment**: Configured for Replit environment with host='0.0.0.0' and port=5000
- **Environment Variables**: Support for SESSION_SECRET environment variable
- **Static Assets**: CSS and JavaScript files served via Flask static file handling

Note: The application currently uses in-memory storage and lacks persistent database integration, making it suitable for development and testing but requiring database implementation for production use.