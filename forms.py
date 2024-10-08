from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserEditForm(FlaskForm):
    """Form for editing users"""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL')
    password = PasswordField('Password', validators=[Length(min=6)])
    netflix = BooleanField('Netflix')
    prime_video = BooleanField('Prime Video')
    disney_plus = BooleanField('Disney Plus')
    hbo_max = BooleanField('HBO Max')
    hulu = BooleanField('Hulu')
    peacock = BooleanField('Peacock')
    paramount_plus = BooleanField('Paramount Plus')
    starz = BooleanField('Starz')
    showtime = BooleanField('Showtime')
    apple_tv = BooleanField('Apple TV')