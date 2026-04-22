from flask import Flask, request, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC
from typing import Tuple
from secrets import token_hex
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os


basedir: str = os.path.abspath(os.path.dirname(__file__))

app: Flask = Flask(__name__)
app.config["SECRET_KEY"]: str = token_hex(32)
app.config["SQLALCHEMY_DATABASE_URI"]: str = f"sqlite:///{os.path.join(basedir, 'data.sqlite')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]: bool = False

bootstrap: Bootstrap = Bootstrap(app)
moment: Moment = Moment(app)
db: SQLAlchemy = SQLAlchemy(app)


class NameForm(FlaskForm):
    name: StringField = StringField("What is your name?", validators=[DataRequired()])
    submit: SubmitField = SubmitField("Submit")


class Role(db.Model):

    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    users: Mapped[list["User"]] = relationship(backref="role")

    def __repr__(self):
        return f"<Role {self.name!r}>"


class User(db.Model):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))

    def __repr__(self):
        return f"<User {self.username!r}>"


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    form: NameForm = NameForm()

    if form.validate_on_submit():
        old_name: str = session.get("name")

        if old_name is not None and old_name != form.name.data:
            flash("Looks like you have changed your name!")

        session["name"]: str = form.name.data

        return redirect(url_for("index"))

    return render_template("index.html", form=form, name=session.get("name"),
                           current_time=datetime.now(UTC))


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
