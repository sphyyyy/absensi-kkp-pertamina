from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """Login form with CSRF protection."""

    username = StringField('Username', validators=[
        DataRequired(message='Username wajib diisi.'),
        Length(min=3, max=80),
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password wajib diisi.'),
    ])
