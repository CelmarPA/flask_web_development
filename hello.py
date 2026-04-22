from flask import Flask, request, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime, UTC
from typing import Tuple
from secrets import token_hex
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


app: Flask = Flask(__name__)
app.config["SECRET_KEY"] = token_hex(32)

bootstrap: Bootstrap = Bootstrap(app)
moment: Moment = Moment(app)


class NameForm(FlaskForm):
    name: StringField = StringField("What is your name?", validators=[DataRequired()])
    submit: SubmitField = SubmitField("Submit")


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    form: NameForm = NameForm()

    if form.validate_on_submit():
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
