from flask import Flask, request, session

app: Flask = Flask(__name__)


@app.route("/")
def index() -> str:
    return "<h1>Hello World!</h1>"


@app.route("/user/<name>")
def user(name: str) -> str:
    return f"<h1>Hello {name}</h1>"


@app.route("/browser")
def browser() -> str:
    user_agent: str = request.headers.get("User-Agent")

    return f"<p>Your browser is {user_agent}</p>"
