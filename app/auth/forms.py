from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email


class LoginForm(FlaskForm):

    email: StringField = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    password: PasswordField = PasswordField("Password", validators=[DataRequired()])
    remember_me: BooleanField = BooleanField("Keep me logged in")
    submit: SubmitField = SubmitField("Log In")
