from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, PasswordField
from wtforms.validators import InputRequired, Optional, Email

class RegisterForm(FlaskForm):
    """Registration Form to authorize a new user"""

    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[Email(), InputRequired()])

class LoginForm(FlaskForm):
    """Login Form to authenicate an user"""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class FeedbackForm(FlaskForm):
    """Feedback Form"""

    title = StringField("Title", validators=[InputRequired()])
    content = StringField("Feedback", validators=[InputRequired()])