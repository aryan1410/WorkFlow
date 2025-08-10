from datetime import datetime, date
from enum import Enum

class ProjectStatus(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    ON_HOLD = "On Hold"
    COMPLETED = "Completed"

class TaskStatus(Enum):
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"

class Priority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Project:
    def __init__(self, id, title, description, course, status=ProjectStatus.NOT_STARTED, 
                 deadline=None, created_at=None, updated_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.course = course
        self.status = status
        self.deadline = deadline
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'course': self.course,
            'status': self.status.value if isinstance(self.status, ProjectStatus) else self.status,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        project = cls(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            course=data['course'],
            status=ProjectStatus(data['status']) if isinstance(data['status'], str) else data['status'],
            deadline=datetime.fromisoformat(data['deadline']) if data['deadline'] else None,
            created_at=datetime.fromisoformat(data['created_at']) if data['created_at'] else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data['updated_at'] else None
        )
        return project

class Task:
    def __init__(self, id, project_id, title, description="", status=TaskStatus.TODO, 
                 priority=Priority.MEDIUM, due_date=None, created_at=None, updated_at=None):
        self.id = id
        self.project_id = project_id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.due_date = due_date
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value if isinstance(self.status, TaskStatus) else self.status,
            'priority': self.priority.value if isinstance(self.priority, Priority) else self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        task = cls(
            id=data['id'],
            project_id=data['project_id'],
            title=data['title'],
            description=data['description'],
            status=TaskStatus(data['status']) if isinstance(data['status'], str) else data['status'],
            priority=Priority(data['priority']) if isinstance(data['priority'], str) else data['priority'],
            due_date=datetime.fromisoformat(data['due_date']) if data['due_date'] else None,
            created_at=datetime.fromisoformat(data['created_at']) if data['created_at'] else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data['updated_at'] else None
        )
        return task

# Helper functions for in-memory storage
def get_project_by_id(project_id):
    from flask import current_app
    projects = current_app.config['PROJECTS']
    for project in projects:
        if project.id == project_id:
            return project
    return None

def get_tasks_by_project_id(project_id):
    from flask import current_app
    tasks = current_app.config['TASKS']
    return [task for task in tasks if task.project_id == project_id]

def get_task_by_id(task_id):
    from flask import current_app
    tasks = current_app.config['TASKS']
    for task in tasks:
        if task.id == task_id:
            return task
    return None
