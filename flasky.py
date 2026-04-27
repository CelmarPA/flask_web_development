import os
from flask import Flask
from app import create_app, db
from app.models import User, Role
from flask_migrate import Migrate


app: Flask = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate: Migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context() -> dict:
    return dict(db=db, User=User, Role=Role)
