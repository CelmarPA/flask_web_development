from flask import Flask

app: Flask = Flask(__name__)


@app.route("/")
def index() -> str:
    return "<h1>Hello World!</h1>"


@app.route("/user/<name>")
def user(name: str) -> str:
    return f"<h1>Hello {name}</h1>"

