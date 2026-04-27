# config.py

from secrets import token_hex
from typing import Dict, Type
import os

basedir: str = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY: str = token_hex(32)
    # SECRET_KEY: str = os.environ.get("SECRET_KEY") or "hard to guess string"

    MAIL_SERVER: str = os.environ.get("MAIL_SERVER", "smtp.googlemail.com")
    MAIL_PORT: int = int(os.environ.get("MAIL_PORT", 587))
    FLASKY_MAIL_SUBJECT_PREFIX = "[Flasky]"
    FLASKY_MAIL_SENDER = "Flasky Admin <flasky@example.com>"
    FLASKY_ADMIN: str | None = os.environ.get("FLASKY_ADMIN")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    @staticmethod
    def init_app(app):
        _app = app
        pass


class DevelopmentConfig(Config):

    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = (os.environ.get("DEV_DATABASE_URL") or
                                    f"sqlite:///{os.path.join(basedir, 'datadev.sqlite')}")


class TestingConfig(Config):

    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = os.environ.get("TEST_DATABASE_URL") or "sqlite://"


class ProductionConfig(Config):

    SQLALCHEMY_DATABASE_URI: str = (os.environ.get("DATABASE_URL") or
                                    f"sqlite:///{os.path.join(basedir, 'data.sqlite')}")


config: Dict[str, Type[Config]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}