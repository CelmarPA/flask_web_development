# config.py

from secrets import token_hex
from typing import Dict, Type
import os

basedir: str = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY: str = token_hex(32)

    MAIL_SERVER: str = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT: int = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS: bool = True
    MAIL_USE_SSL: bool = False

    MAIL_USERNAME: str | None = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD: str | None = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER: str | None = MAIL_USERNAME

    FLASKY_MAIL_SUBJECT_PREFIX = "[Flasky]"
    FLASKY_MAIL_SENDER = MAIL_USERNAME

    FLASKY_ADMIN: str | None = os.environ.get("FLASKY_ADMIN")

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    @staticmethod
    def init_app(app):
        _app = app
        pass


class DevelopmentConfig(Config):

    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = (os.environ.get("DEV_DATABASE_URL") or
                                    f"sqlite:///{os.path.join(basedir, 'data-dev.sqlite')}")


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