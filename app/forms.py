from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from .models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class EstimationForm(FlaskForm):
    city = SelectField('City', validators=[DataRequired()], choices=[
        ('Chennai', 'Chennai'), ('Bengaluru', 'Bengaluru'), ('Mumbai', 'Mumbai'), 
        ('Delhi', 'Delhi'), ('Hyderabad', 'Hyderabad'), ('Kolkata', 'Kolkata'), 
        ('Pune', 'Pune'), ('Ahmedabad', 'Ahmedabad'), ('Jaipur', 'Jaipur'), ('Coimbatore', 'Coimbatore')
    ])
    quality = SelectField('Quality', validators=[DataRequired()], choices=[
        ('basic', 'Basic'), ('standard', 'Standard'), ('premium', 'Premium')
    ])
    floors = IntegerField('Floors', validators=[DataRequired(), NumberRange(min=1, max=10)], default=2)
    carpet_ratio = FloatField('Carpet Area Ratio', validators=[DataRequired(), NumberRange(min=0.5, max=0.95)], default=0.72)
    
    blueprint = FileField('Upload Blueprint (PNG/JPG)', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    
    area_sqft = IntegerField('Area (sqft)', validators=[NumberRange(min=0)], default=0)
    rooms_override = IntegerField('Override Rooms', validators=[NumberRange(min=0)], default=0)
    wall_override = IntegerField('Override Wall Length (ft)', validators=[NumberRange(min=0)], default=0)
    is_commercial = BooleanField('Commercial Project')
    
    submit = SubmitField('Predict Cost')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
