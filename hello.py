from flask import Flask, request, render_template

app: Flask = Flask(__name__)


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

