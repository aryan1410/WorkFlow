from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from datetime import datetime
from models import Project, Task, ProjectStatus, TaskStatus, Priority, get_project_by_id, get_tasks_by_project_id, get_task_by_id
from app import app

@app.route('/')
def index():
    """Dashboard view showing all projects with progress indicators"""
    projects = current_app.config['PROJECTS']
    
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
    
    return render_template('index.html', 
                         projects=projects,
                         projects_by_course=projects_by_course,
                         total_projects=total_projects,
                         completed_projects=completed_projects,
                         in_progress_projects=in_progress_projects,
                         overdue_projects=overdue_projects,
                         today=datetime.now())

@app.route('/project/new', methods=['GET', 'POST'])
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
        project_id = current_app.config['PROJECT_COUNTER']
        current_app.config['PROJECT_COUNTER'] += 1
        
        project = Project(
            id=project_id,
            title=title,
            description=description,
            course=course,
            deadline=deadline
        )
        
        current_app.config['PROJECTS'].append(project)
        flash(f'Project "{title}" created successfully!', 'success')
        return redirect(url_for('project_detail', project_id=project_id))
    
    return render_template('project_form.html', 
                         title='New Project',
                         project=None)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    """View project details with tasks"""
    project = get_project_by_id(project_id)
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('index'))
    
    tasks = get_tasks_by_project_id(project_id)
    
    # Calculate task statistics
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == TaskStatus.DONE])
    progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return render_template('project_detail.html', 
                         project=project,
                         tasks=tasks,
                         total_tasks=total_tasks,
                         completed_tasks=completed_tasks,
                         progress_percentage=progress_percentage,
                         today=datetime.now())

@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    """Edit an existing project"""
    project = get_project_by_id(project_id)
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
        
        flash(f'Project "{title}" updated successfully!', 'success')
        return redirect(url_for('project_detail', project_id=project_id))
    
    return render_template('project_form.html', 
                         title='Edit Project',
                         project=project)

@app.route('/project/<int:project_id>/delete', methods=['POST'])
def delete_project(project_id):
    """Delete a project and all its tasks"""
    project = get_project_by_id(project_id)
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('index'))
    
    # Remove project
    current_app.config['PROJECTS'] = [p for p in current_app.config['PROJECTS'] if p.id != project_id]
    
    # Remove all associated tasks
    current_app.config['TASKS'] = [t for t in current_app.config['TASKS'] if t.project_id != project_id]
    
    flash(f'Project "{project.title}" deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/project/<int:project_id>/task/new', methods=['POST'])
def new_task(project_id):
    """Create a new task for a project"""
    project = get_project_by_id(project_id)
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
    task_id = current_app.config['TASK_COUNTER']
    current_app.config['TASK_COUNTER'] += 1
    
    task = Task(
        id=task_id,
        project_id=project_id,
        title=title,
        description=description,
        priority=Priority(priority),
        due_date=due_date
    )
    
    current_app.config['TASKS'].append(task)
    flash(f'Task "{title}" created successfully!', 'success')
    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/task/<int:task_id>/update_status', methods=['POST'])
def update_task_status(task_id):
    """Update task status"""
    task = get_task_by_id(task_id)
    if not task:
        flash('Task not found.', 'error')
        return redirect(url_for('index'))
    
    new_status = request.form.get('status')
    if new_status in [s.value for s in TaskStatus]:
        task.status = TaskStatus(new_status)
        task.updated_at = datetime.now()
        flash('Task status updated successfully!', 'success')
    else:
        flash('Invalid status.', 'error')
    
    return redirect(url_for('project_detail', project_id=task.project_id))

@app.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """Delete a task"""
    task = get_task_by_id(task_id)
    if not task:
        flash('Task not found.', 'error')
        return redirect(url_for('index'))
    
    project_id = task.project_id
    current_app.config['TASKS'] = [t for t in current_app.config['TASKS'] if t.id != task_id]
    
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('project_detail', project_id=project_id))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html', error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html', error_message="Internal server error"), 500
