from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime, UTC
from typing import Tuple


app: Flask = Flask(__name__)
bootstrap: Bootstrap = Bootstrap(app)
moment: Moment = Moment(app)


@app.route("/")
def index() -> str:
    return render_template("index.html", current_time=datetime.now(UTC))


@app.route("/user/<name>")
def user(name: str) -> str:
    return render_template("user.html", name=name)


@app.route("/browser")
def browser() -> str:
    user_agent: str = request.headers.get("User-Agent")

    return f"<p>Your browser is {user_agent}</p>"


@app.errorhandler(404)
def page_not_found(e: Exception) -> Tuple[str, int]:
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e: Exception) -> Tuple[str, int]:
    return render_template("500.html"), 500
