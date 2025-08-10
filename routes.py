from flask import render_template, request, redirect, url_for, flash, session, send_file, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime, timedelta
from sqlalchemy import func, desc, or_, and_
import os

from app import app, db
from models import (Project, Task, ProjectStatus, TaskStatus, Priority, ProjectNote, StudySession, Course, User,
                   ProjectFile, ProjectCollaborator, ProjectComment, ActivityLog)
from auth import generate_verification_url, verify_email_token, send_verification_email, validate_password_strength
from forms import (LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm, ChangePasswordForm, ProfileForm,
                  FileUploadForm, CollaboratorInviteForm, CommentForm, SearchForm)
from utils import save_uploaded_file, format_file_size, get_file_icon, log_activity


@app.route('/')
def index():
    """Dashboard view - shows landing page for logged out users, dashboard for logged in users"""
    if not current_user.is_authenticated:
        return render_template('landing.html')
    
    # Get user's projects
    projects = Project.query.filter_by(user_id=current_user.id).all()
    
    # Calculate project statistics
    total_projects = len(projects)
    completed_projects = len([p for p in projects if p.status == ProjectStatus.COMPLETED])
    in_progress_projects = len([p for p in projects if p.status == ProjectStatus.IN_PROGRESS])
    overdue_projects = len([p for p in projects if p.deadline and p.deadline < datetime.utcnow() and p.status != ProjectStatus.COMPLETED])
    
    # Group projects by course
    projects_by_course = {}
    for project in projects:
        course = project.course or "Uncategorized"
        if course not in projects_by_course:
            projects_by_course[course] = []
        projects_by_course[course].append(project)
    
    # Get recent study sessions
    recent_sessions = StudySession.query.filter_by(user_id=current_user.id)\
        .order_by(desc(StudySession.created_at)).limit(5).all()
    
    return render_template('index.html',
                         projects=projects,
                         projects_by_course=projects_by_course,
                         total_projects=total_projects,
                         completed_projects=completed_projects,
                         in_progress_projects=in_progress_projects,
                         overdue_projects=overdue_projects,
                         recent_sessions=recent_sessions,
                         today=datetime.utcnow())


# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Validate password strength
        is_strong, message = validate_password_strength(form.password.data)
        if not is_strong:
            flash(message, 'error')
            return render_template('auth/register.html', form=form)
        
        # Create new user
        user = User(
            email=form.email.data.lower(),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            is_verified=True
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in to your account.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# Email verification routes removed for simplicity


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password form"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        # For now, just show a message
        flash('Password reset functionality will be available soon. Please contact support.', 'info')
        return redirect(url_for('login'))
    
    return render_template('auth/forgot_password.html', form=form)


# Project Management Routes
@app.route('/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    """Create a new project"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        course = request.form.get('course', '').strip()
        status = request.form.get('status', ProjectStatus.NOT_STARTED.value)
        deadline_str = request.form.get('deadline', '').strip()
        
        # Validation
        if not title:
            flash('Project title is required.', 'error')
            return render_template('project_form.html', 
                                 title='New Project',
                                 project=None,
                                 form_data=request.form)
        
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str)
            except ValueError:
                flash('Invalid deadline format.', 'error')
                return render_template('project_form.html', 
                                     title='New Project',
                                     project=None,
                                     form_data=request.form)
        
        # Create new project
        project = Project(
            title=title,
            description=description,
            course=course,
            status=ProjectStatus(status),
            deadline=deadline,
            user_id=current_user.id
        )
        
        db.session.add(project)
        db.session.commit()
        
        # Log activity
        log_activity(current_user.id, 'created', 'project', project.id, 
                    f'Created project "{title}"', project.id)
        
        flash(f'Project "{title}" created successfully!', 'success')
        return redirect(url_for('project_detail', project_id=project.id))
    
    return render_template('project_form.html', 
                         title='New Project',
                         project=None)


@app.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    """View project details with tasks, files, collaborators, and comments"""
    project = Project.query.get_or_404(project_id)
    
    # Check if user can access this project
    if not project.can_user_access(current_user):
        flash('You do not have permission to view this project.', 'error')
        return redirect(url_for('index'))
    
    tasks = Task.query.filter_by(project_id=project_id).all()
    notes = ProjectNote.query.filter_by(project_id=project_id).order_by(desc(ProjectNote.created_at)).all()
    files = ProjectFile.query.filter_by(project_id=project_id).order_by(desc(ProjectFile.uploaded_at)).all()
    comments = ProjectComment.query.filter_by(project_id=project_id).order_by(ProjectComment.created_at).all()
    collaborators = project.get_collaborators()
    
    # Calculate task statistics
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == TaskStatus.DONE])
    progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Get recent activity
    recent_activity = ActivityLog.query.filter_by(project_id=project_id)\
        .order_by(desc(ActivityLog.created_at)).limit(10).all()
    
    # Forms
    file_form = FileUploadForm()
    comment_form = CommentForm()
    invite_form = CollaboratorInviteForm()
    
    # Format file sizes
    for file in files:
        file.formatted_size = format_file_size(file.file_size)
        file.icon = get_file_icon(file.file_type)
    
    return render_template('project_detail.html', 
                         project=project,
                         tasks=tasks,
                         notes=notes,
                         files=files,
                         comments=comments,
                         collaborators=collaborators,
                         recent_activity=recent_activity,
                         total_tasks=total_tasks,
                         completed_tasks=completed_tasks,
                         progress_percentage=progress_percentage,
                         file_form=file_form,
                         comment_form=comment_form,
                         invite_form=invite_form,
                         today=datetime.utcnow())


# Continue with other project routes...
@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """Edit an existing project"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        course = request.form.get('course', '').strip()
        status = request.form.get('status', ProjectStatus.NOT_STARTED.value)
        deadline_str = request.form.get('deadline', '').strip()
        
        # Validation
        if not title:
            flash('Project title is required.', 'error')
            return render_template('project_form.html', 
                                 title='Edit Project',
                                 project=project,
                                 form_data=request.form)
        
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str)
            except ValueError:
                flash('Invalid deadline format.', 'error')
                return render_template('project_form.html', 
                                     title='Edit Project',
                                     project=project,
                                     form_data=request.form)
        
        # Update project
        project.title = title
        project.description = description
        project.course = course
        project.status = ProjectStatus(status)
        project.deadline = deadline
        project.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log activity
        log_activity(current_user.id, 'updated', 'project', project_id, 
                    f'Updated project "{title}"', project_id)
        
        flash(f'Project "{title}" updated successfully!', 'success')
        return redirect(url_for('project_detail', project_id=project_id))
    
    return render_template('project_form.html', 
                         title='Edit Project',
                         project=project)


@app.route('/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    """Delete a project and all its tasks"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('index'))
    
    # Delete project (cascades to tasks and notes)
    project_title = project.title
    db.session.delete(project)
    db.session.commit()
    
    flash(f'Project "{project_title}" deleted successfully!', 'success')
    return redirect(url_for('index'))


# Task Management Routes
@app.route('/project/<int:project_id>/task/new', methods=['POST'])
@login_required
def new_task(project_id):
    """Create a new task for a project"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('index'))
    
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    priority = request.form.get('priority', Priority.MEDIUM.value)
    due_date_str = request.form.get('due_date', '').strip()
    
    if not title:
        flash('Task title is required.', 'error')
        return redirect(url_for('project_detail', project_id=project_id))
    
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.fromisoformat(due_date_str)
        except ValueError:
            flash('Invalid due date format.', 'error')
            return redirect(url_for('project_detail', project_id=project_id))
    
    # Create new task
    task = Task(
        project_id=project_id,
        title=title,
        description=description,
        priority=Priority(priority),
        due_date=due_date
    )
    
    db.session.add(task)
    db.session.commit()
    flash(f'Task "{title}" created successfully!', 'success')
    return redirect(url_for('project_detail', project_id=project_id))


@app.route('/task/<int:task_id>/update_status', methods=['POST'])
@login_required
def update_task_status(task_id):
    """Update task status"""
    task = Task.query.join(Project).filter(
        Task.id == task_id,
        Project.user_id == current_user.id
    ).first()
    
    if not task:
        flash('Task not found.', 'error')
        return redirect(url_for('index'))
    
    new_status = request.form.get('status')
    if new_status in [s.value for s in TaskStatus]:
        task.status = TaskStatus(new_status)
        task.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Task status updated successfully!', 'success')
    else:
        flash('Invalid status.', 'error')
    
    return redirect(url_for('project_detail', project_id=task.project_id))


@app.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete a task"""
    task = Task.query.join(Project).filter(
        Task.id == task_id,
        Project.user_id == current_user.id
    ).first()
    
    if not task:
        flash('Task not found.', 'error')
        return redirect(url_for('index'))
    
    project_id = task.project_id
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('project_detail', project_id=project_id))


# Study Session Routes
@app.route('/project/<int:project_id>/study', methods=['POST'])
@login_required
def log_study_session(project_id):
    """Log a study session for a project"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('index'))
    
    duration = request.form.get('duration', type=int)
    description = request.form.get('description', '').strip()
    
    if not duration or duration <= 0:
        flash('Please enter a valid study duration.', 'error')
        return redirect(url_for('project_detail', project_id=project_id))
    
    study_session = StudySession(
        project_id=project_id,
        user_id=current_user.id,
        duration_minutes=duration,
        description=description
    )
    
    db.session.add(study_session)
    db.session.commit()
    flash(f'Study session logged: {duration} minutes', 'success')
    return redirect(url_for('project_detail', project_id=project_id))


@app.route('/study-analytics')
@login_required
def study_analytics():
    """View study analytics dashboard"""
    # Get study sessions for the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    sessions = StudySession.query.filter(
        StudySession.user_id == current_user.id,
        StudySession.created_at >= thirty_days_ago
    ).order_by(desc(StudySession.created_at)).all()
    
    # Calculate analytics
    total_time = sum(s.duration_minutes for s in sessions)
    total_sessions = len(sessions)
    
    # Group by project
    project_time = {}
    for session in sessions:
        project = session.project_id
        if project not in project_time:
            project_time[project] = 0
        project_time[project] += session.duration_minutes
    
    return render_template('study_analytics.html',
                         sessions=sessions,
                         total_time=total_time,
                         total_sessions=total_sessions,
                         project_time=project_time)


# Project Notes Routes
@app.route('/project/<int:project_id>/note/new', methods=['POST'])
@login_required
def add_project_note(project_id):
    """Add a note to a project"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('index'))
    
    content = request.form.get('content', '').strip()
    if not content:
        flash('Note content is required.', 'error')
        return redirect(url_for('project_detail', project_id=project_id))
    
    note = ProjectNote(
        project_id=project_id,
        content=content
    )
    
    db.session.add(note)
    db.session.commit()
    flash('Note added successfully!', 'success')
    return redirect(url_for('project_detail', project_id=project_id))


@app.route('/note/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_project_note(note_id):
    """Delete a project note"""
    note = ProjectNote.query.join(Project).filter(
        ProjectNote.id == note_id,
        Project.user_id == current_user.id
    ).first()
    
    if not note:
        flash('Note not found.', 'error')
        return redirect(url_for('index'))
    
    project_id = note.project_id
    db.session.delete(note)
    db.session.commit()
    
    flash('Note deleted successfully!', 'success')
    return redirect(url_for('project_detail', project_id=project_id))


# Course Management Routes
@app.route('/courses')
@login_required
def manage_courses():
    """Manage user courses"""
    courses = Course.query.filter_by(user_id=current_user.id).order_by(Course.year.desc(), Course.semester).all()
    return render_template('courses.html', courses=courses)


@app.route('/course/new', methods=['POST'])
@login_required
def add_course():
    """Add a new course"""
    name = request.form.get('name', '').strip()
    code = request.form.get('code', '').strip()
    semester = request.form.get('semester', '').strip()
    year = request.form.get('year', type=int)
    instructor = request.form.get('instructor', '').strip()
    credits = request.form.get('credits', type=int)
    
    if not name:
        flash('Course name is required.', 'error')
        return redirect(url_for('manage_courses'))
    
    course = Course(
        name=name,
        code=code,
        semester=semester,
        year=year,
        instructor=instructor,
        credits=credits,
        user_id=current_user.id
    )
    
    db.session.add(course)
    db.session.commit()
    flash('Course added successfully!', 'success')
    return redirect(url_for('manage_courses'))


# Profile and Settings
@app.route('/profile')
@login_required
def profile():
    """View user profile and statistics"""
    # Get user statistics
    total_projects = Project.query.filter_by(user_id=current_user.id).count()
    completed_projects = Project.query.filter_by(
        user_id=current_user.id,
        status=ProjectStatus.COMPLETED
    ).count()
    
    total_tasks = db.session.query(Task).join(Project).filter(
        Project.user_id == current_user.id
    ).count()
    
    completed_tasks = db.session.query(Task).join(Project).filter(
        Project.user_id == current_user.id,
        Task.status == TaskStatus.DONE
    ).count()
    
    total_study_time = db.session.query(func.sum(StudySession.duration_minutes)).filter_by(
        user_id=current_user.id
    ).scalar() or 0
    
    return render_template('profile.html',
                         total_projects=total_projects,
                         completed_projects=completed_projects,
                         total_tasks=total_tasks,
                         completed_tasks=completed_tasks,
                         total_study_time=total_study_time)


# File management routes
@app.route('/project/<int:project_id>/upload', methods=['POST'])
@login_required
def upload_file(project_id):
    """Upload file to project"""
    project = Project.query.get_or_404(project_id)
    
    if not project.can_user_edit(current_user):
        flash('You do not have permission to upload files to this project.', 'error')
        return redirect(url_for('project_detail', project_id=project_id))
    
    form = FileUploadForm()
    if form.validate_on_submit():
        try:
            file_info = save_uploaded_file(form.file.data, project_id, current_user.id)
            if file_info:
                # Save file record to database
                project_file = ProjectFile(
                    filename=file_info['filename'],
                    original_filename=file_info['original_filename'],
                    file_size=file_info['file_size'],
                    file_type=file_info['file_type'],
                    file_path=file_info['file_path'],
                    project_id=project_id,
                    uploaded_by=current_user.id
                )
                
                db.session.add(project_file)
                db.session.commit()
                
                # Log activity
                log_activity(current_user.id, 'uploaded', 'file', project_file.id,
                           f'Uploaded file "{file_info["original_filename"]}"', project_id)
                
                flash(f'File "{file_info["original_filename"]}" uploaded successfully!', 'success')
            else:
                flash('File upload failed.', 'error')
                
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An error occurred while uploading the file.', 'error')
            print(f"Upload error: {e}")
    
    return redirect(url_for('project_detail', project_id=project_id))


@app.route('/project/<int:project_id>/file/<int:file_id>/download')
@login_required
def download_file(project_id, file_id):
    """Download project file"""
    project = Project.query.get_or_404(project_id)
    if not project.can_user_access(current_user):
        flash('You do not have permission to access this project.', 'error')
        return redirect(url_for('index'))
    
    file = ProjectFile.query.filter_by(id=file_id, project_id=project_id).first_or_404()
    
    try:
        return send_file(file.file_path, 
                        download_name=file.original_filename,
                        as_attachment=True)
    except FileNotFoundError:
        flash('File not found.', 'error')
        return redirect(url_for('project_detail', project_id=project_id))


@app.route('/project/<int:project_id>/file/<int:file_id>/delete', methods=['POST'])
@login_required
def delete_file(project_id, file_id):
    """Delete project file"""
    project = Project.query.get_or_404(project_id)
    if not project.can_user_edit(current_user):
        flash('You do not have permission to delete files from this project.', 'error')
        return redirect(url_for('project_detail', project_id=project_id))
    
    file = ProjectFile.query.filter_by(id=file_id, project_id=project_id).first_or_404()
    
    try:
        # Delete physical file
        if os.path.exists(file.file_path):
            os.remove(file.file_path)
        
        # Delete database record
        db.session.delete(file)
        db.session.commit()
        
        # Log activity
        log_activity(current_user.id, 'deleted', 'file', file_id,
                   f'Deleted file "{file.original_filename}"', project_id)
        
        flash('File deleted successfully!', 'success')
    except Exception as e:
        flash('An error occurred while deleting the file.', 'error')
        print(f"Delete error: {e}")
    
    return redirect(url_for('project_detail', project_id=project_id))


# Collaboration routes
@app.route('/project/<int:project_id>/invite', methods=['POST'])
@login_required
def invite_collaborator(project_id):
    """Invite collaborator to project"""
    project = Project.query.get_or_404(project_id)
    
    # Only owner can invite collaborators
    if project.user_id != current_user.id:
        flash('Only the project owner can invite collaborators.', 'error')
        return redirect(url_for('project_detail', project_id=project_id))
    
    form = CollaboratorInviteForm()
    if form.validate_on_submit():
        # Find user by email
        invited_user = User.query.filter_by(email=form.email.data).first()
        if not invited_user:
            flash('User with this email address not found.', 'error')
            return redirect(url_for('project_detail', project_id=project_id))
        
        # Check if already a collaborator
        existing = ProjectCollaborator.query.filter_by(
            project_id=project_id, user_id=invited_user.id).first()
        if existing:
            flash('This user is already a collaborator on this project.', 'error')
            return redirect(url_for('project_detail', project_id=project_id))
        
        # Create collaboration invitation
        collaboration = ProjectCollaborator(
            project_id=project_id,
            user_id=invited_user.id,
            role=form.role.data,
            status='pending'
        )
        
        db.session.add(collaboration)
        db.session.commit()
        
        # Log activity
        log_activity(current_user.id, 'invited', 'collaborator', invited_user.id,
                   f'Invited {invited_user.email} as {form.role.data}', project_id)
        
        flash(f'Invitation sent to {form.email.data}!', 'success')
    
    return redirect(url_for('project_detail', project_id=project_id))


@app.route('/collaboration/<int:collab_id>/accept')
@login_required
def accept_collaboration(collab_id):
    """Accept collaboration invitation"""
    collaboration = ProjectCollaborator.query.get_or_404(collab_id)
    
    if collaboration.user_id != current_user.id:
        flash('You can only accept your own invitations.', 'error')
        return redirect(url_for('index'))
    
    collaboration.status = 'accepted'
    collaboration.accepted_at = datetime.utcnow()
    db.session.commit()
    
    # Log activity
    log_activity(current_user.id, 'accepted', 'collaboration', collab_id,
               f'Accepted collaboration invitation', collaboration.project_id)
    
    flash('Collaboration invitation accepted!', 'success')
    return redirect(url_for('project_detail', project_id=collaboration.project_id))


@app.route('/collaboration/<int:collab_id>/decline')
@login_required
def decline_collaboration(collab_id):
    """Decline collaboration invitation"""
    collaboration = ProjectCollaborator.query.get_or_404(collab_id)
    
    if collaboration.user_id != current_user.id:
        flash('You can only decline your own invitations.', 'error')
        return redirect(url_for('index'))
    
    collaboration.status = 'declined'
    db.session.commit()
    
    flash('Collaboration invitation declined.', 'info')
    return redirect(url_for('index'))


# Comment routes
@app.route('/project/<int:project_id>/comment', methods=['POST'])
@login_required
def add_comment(project_id):
    """Add comment to project"""
    project = Project.query.get_or_404(project_id)
    
    if not project.can_user_access(current_user):
        flash('You do not have permission to comment on this project.', 'error')
        return redirect(url_for('project_detail', project_id=project_id))
    
    form = CommentForm()
    if form.validate_on_submit():
        comment = ProjectComment(
            content=form.content.data,
            project_id=project_id,
            user_id=current_user.id
        )
        
        db.session.add(comment)
        db.session.commit()
        
        # Log activity
        log_activity(current_user.id, 'commented', 'project', project_id,
                   'Added a comment', project_id)
        
        flash('Comment added successfully!', 'success')
    
    return redirect(url_for('project_detail', project_id=project_id))


# Search routes
@app.route('/search')
@login_required
def search():
    """Search projects, tasks, and collaborators"""
    form = SearchForm()
    results = {
        'projects': [],
        'tasks': [],
        'collaborators': [],
        'files': []
    }
    
    if request.args.get('query'):
        query = request.args.get('query')
        filter_type = request.args.get('filter_type', 'all')
        
        # Search projects user owns or collaborates on
        accessible_projects = db.session.query(Project.id).filter(
            or_(
                Project.user_id == current_user.id,
                Project.id.in_(
                    db.session.query(ProjectCollaborator.project_id)
                    .filter(and_(
                        ProjectCollaborator.user_id == current_user.id,
                        ProjectCollaborator.status == 'accepted'
                    ))
                )
            )
        ).subquery()
        
        if filter_type in ['all', 'projects']:
            results['projects'] = Project.query.filter(
                and_(
                    Project.id.in_(accessible_projects),
                    or_(
                        Project.title.ilike(f'%{query}%'),
                        Project.description.ilike(f'%{query}%'),
                        Project.course.ilike(f'%{query}%')
                    )
                )
            ).all()
        
        if filter_type in ['all', 'tasks']:
            results['tasks'] = Task.query.filter(
                and_(
                    Task.project_id.in_(accessible_projects),
                    or_(
                        Task.title.ilike(f'%{query}%'),
                        Task.description.ilike(f'%{query}%')
                    )
                )
            ).all()
        
        if filter_type in ['all', 'files']:
            results['files'] = ProjectFile.query.filter(
                and_(
                    ProjectFile.project_id.in_(accessible_projects),
                    ProjectFile.original_filename.ilike(f'%{query}%')
                )
            ).all()
    
    return render_template('search.html', form=form, results=results, query=query if 'query' in locals() else '')


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html', error_message="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html', error_message="Internal server error"), 500