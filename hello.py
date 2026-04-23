from flask import Flask, request, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, DynamicMapped
from datetime import datetime, UTC
from typing import Tuple
from secrets import token_hex
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os


basedir: str = os.path.abspath(os.path.dirname(__file__))

app: Flask = Flask(__name__)
app.config["SECRET_KEY"]= token_hex(32)
app.config["SQLALCHEMY_DATABASE_URI"]= f"sqlite:///{os.path.join(basedir, 'data.sqlite')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["FLASKY_ADMIN"] = os.environ.get("FLASKY_ADMIN")
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')
app.config["FLASKY_MAIL_SUBJECT_PREFIX"] = "[Flasky]"
app.config["FLASKY_EMAIL_SENDER"] = "Flasky Admin <flasky@example.com>"

bootstrap: Bootstrap = Bootstrap(app)
moment: Moment = Moment(app)
db: SQLAlchemy = SQLAlchemy(app)

migrate: Migrate = Migrate(app, db)
mail: Mail = Mail(app)


def send_email(to: str, subject: str, template: str, **kwargs) -> None:
    msg: Message = Message(app.config["FLASKY_MAIL_SUBJECT_PREFIX"] + subject,
                           sender=app.config["FLASKY_EMAIL_SENDER"], recipients=[to])

    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)

    mail.send(msg)


class NameForm(FlaskForm):
    name: StringField = StringField("What is your name?", validators=[DataRequired()])
    submit: SubmitField = SubmitField("Submit")


class Role(db.Model):

    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    users: DynamicMapped[list["User"]] = relationship(backref="role", lazy="dynamic")

    def __repr__(self):
        return f"<Role {self.name!r}>"


class User(db.Model):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"),nullable=True)

    def __repr__(self):
        return f"<User {self.username!r}>"


@app.shell_context_processor
def make_shell_context() -> dict:
    return dict(db=db, User=User, Role=Role)


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    form: NameForm = NameForm()

    if form.validate_on_submit():
        user: str = User.query.filter_by(username=form.name.data).first()

        if user is None:
            user: User = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session["known"] = False

            if app.config["FLASKY_ADMIN"]:
                send_email(app.config["FLASKY_ADMIN"], "New User", "mail/new_user", user=user)

        else:
            session["known"] = True

        session["name"] = form.name.data
        form.name.data = ""

        return redirect(url_for("index"))

    return render_template("index.html", form=form, name=session.get("name"),
                           known=session.get("known", False), current_time=datetime.now(UTC))


@app.route("/user/<name>")
def user(name: str) -> str:
    return render_template("user.html", name=name)


@app.route("/browser")
def browser() -> str:
    user_agent: str = request.headers.get("User-Agent")

    return f"<p>Your browser is {user_agent}</p>"


@app.errorhandler(404)
def page_not_found(e: Exception) -> Tuple[str, int]:
    _e: Exception = e
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e: Exception) -> Tuple[str, int]:
    _e: Exception = e
    return render_template("500.html"), 500
