from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Create Account')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('This email is already registered. Please choose a different one.')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if not user:
            raise ValidationError('No account found with that email address.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Reset Password')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.')
    ])
    password2 = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Change Password')


class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Update Profile')


class FileUploadForm(FlaskForm):
    file = FileField('Choose File', validators=[
        FileRequired(),
        FileAllowed(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 
                    'ppt', 'pptx', 'xls', 'xlsx', 'zip', 'rar', 'py', 'js', 'html', 'css'],
                   'Invalid file type!')
    ])
    description = TextAreaField('Description (optional)', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Upload File')


class CollaboratorInviteForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[
        ('collaborator', 'Collaborator - Can edit and manage tasks'),
        ('viewer', 'Viewer - Can only view project details')
    ], default='collaborator')
    message = TextAreaField('Invitation Message (optional)', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Send Invitation')


class CommentForm(FlaskForm):
    content = TextAreaField('Add a comment', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Post Comment')


class SearchForm(FlaskForm):
    query = StringField('Search projects, tasks, or collaborators...', validators=[DataRequired()])
    filter_type = SelectField('Filter', choices=[
        ('all', 'All'),
        ('projects', 'Projects'),
        ('tasks', 'Tasks'),
        ('collaborators', 'Collaborators'),
        ('files', 'Files')
    ], default='all')
    submit = SubmitField('Search')