from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap

app: Flask = Flask(__name__)
bootstrap: Bootstrap = Bootstrap(app)


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/user/<name>")
def user(name: str) -> str:
    return render_template("user.html", name=name)


@app.route("/browser")
def browser() -> str:
    user_agent: str = request.headers.get("User-Agent")

    return f"<p>Your browser is {user_agent}</p>"

