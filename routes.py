from flask import render_template, request, redirect, url_for, flash, current_app, session
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app import app, db
from models import Project, Task, ProjectStatus, TaskStatus, Priority, ProjectNote, StudySession, Course, User
from replit_auth import require_login, make_replit_blueprint

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

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
    overdue_projects = len([p for p in projects if p.deadline and p.deadline < datetime.now() and p.status != ProjectStatus.COMPLETED])
    
    # Group projects by course
    projects_by_course = {}
    for project in projects:
        course = project.course or "Uncategorized"
        if course not in projects_by_course:
            projects_by_course[course] = []
        projects_by_course[course].append(project)
    
    # Get recent study sessions
    recent_sessions = StudySession.query.filter_by(user_id=current_user.id)\
        .order_by(desc(StudySession.created_at))\
        .limit(5).all()
    
    # Calculate total study time this week
    week_ago = datetime.now() - timedelta(days=7)
    weekly_study_time = db.session.query(func.sum(StudySession.duration_minutes))\
        .filter(StudySession.user_id == current_user.id)\
        .filter(StudySession.created_at >= week_ago)\
        .scalar() or 0
    
    return render_template('index.html', 
                         projects=projects,
                         projects_by_course=projects_by_course,
                         total_projects=total_projects,
                         completed_projects=completed_projects,
                         in_progress_projects=in_progress_projects,
                         overdue_projects=overdue_projects,
                         recent_sessions=recent_sessions,
                         weekly_study_time=weekly_study_time,
                         today=datetime.now())

@app.route('/project/new', methods=['GET', 'POST'])
@require_login
def new_project():
    """Create a new project"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        course = request.form.get('course', '').strip()
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
            deadline=deadline,
            user_id=current_user.id
        )
        
        db.session.add(project)
        db.session.commit()
        flash(f'Project "{title}" created successfully!', 'success')
        return redirect(url_for('project_detail', project_id=project.id))
    
    return render_template('project_form.html', 
                         title='New Project',
                         project=None)

@app.route('/project/<int:project_id>')
@require_login
def project_detail(project_id):
    """View project details with tasks"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('index'))
    
    tasks = Task.query.filter_by(project_id=project_id).all()
    notes = ProjectNote.query.filter_by(project_id=project_id).order_by(desc(ProjectNote.created_at)).all()
    
    # Calculate task statistics
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == TaskStatus.DONE])
    progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return render_template('project_detail.html', 
                         project=project,
                         tasks=tasks,
                         notes=notes,
                         total_tasks=total_tasks,
                         completed_tasks=completed_tasks,
                         progress_percentage=progress_percentage,
                         today=datetime.now())

@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@require_login
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
        project.updated_at = datetime.now()
        
        db.session.commit()
        flash(f'Project "{title}" updated successfully!', 'success')
        return redirect(url_for('project_detail', project_id=project_id))
    
    return render_template('project_form.html', 
                         title='Edit Project',
                         project=project)

@app.route('/project/<int:project_id>/delete', methods=['POST'])
@require_login
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

@app.route('/project/<int:project_id>/task/new', methods=['POST'])
@require_login
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
@require_login
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
        task.updated_at = datetime.now()
        db.session.commit()
        flash('Task status updated successfully!', 'success')
    else:
        flash('Invalid status.', 'error')
    
    return redirect(url_for('project_detail', project_id=task.project_id))

@app.route('/task/<int:task_id>/delete', methods=['POST'])
@require_login
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
@require_login
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
    
    session = StudySession(
        project_id=project_id,
        user_id=current_user.id,
        duration_minutes=duration,
        description=description
    )
    
    db.session.add(session)
    db.session.commit()
    flash(f'Study session logged: {duration} minutes', 'success')
    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/study-analytics')
@require_login
def study_analytics():
    """View study analytics dashboard"""
    # Get study sessions for the last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
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
@require_login
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
@require_login
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
@require_login
def manage_courses():
    """Manage user courses"""
    courses = Course.query.filter_by(user_id=current_user.id).order_by(Course.year.desc(), Course.semester).all()
    return render_template('courses.html', courses=courses)

@app.route('/course/new', methods=['POST'])
@require_login
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
@require_login
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

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html', error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html', error_message="Internal server error"), 500
