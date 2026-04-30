# __init__.py

import click
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_web_development.config import config
from flask_login import LoginManager


bootstrap: Bootstrap = Bootstrap()
mail: Mail = Mail()
moment: Moment = Moment()
login_manager: LoginManager = LoginManager()
login_manager.login_view = "auth.login"
db: SQLAlchemy = SQLAlchemy()

def create_app(config_name: str = "default") -> Flask:
    app: Flask = Flask(__name__)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    db.init_app(app)


    from .main import main
    app.register_blueprint(main)

    @app.cli.command()
    @click.argument('test_names', nargs=-1)
    def test(test_names) -> None:
        """Run the unit tests."""

        import unittest

        if test_names:
            tests = unittest.TestLoader().loadTestsFromNames(test_names)

        else:
            tests = unittest.TestLoader().discover("tests", top_level_dir=".")

        unittest.TextTestRunner(verbosity=2).run(tests)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    return app
