from datetime import datetime, UTC
from flask import render_template, session, redirect, url_for, current_app
from . import main
from .forms import NameForm
from .. import db
from ..models import User
from ..email import send_email



@main.route("/", methods=["GET", "POST"])
def index():
    return render_template('index.html')


@main.route("/user/<username>")
def user(username: str):
    user: User = User.query.filter_by(username=username).first_or_404()

    return render_template("user.html", user=user)
