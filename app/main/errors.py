from flask import render_template
from . import main
from typing import Tuple


@main.app_errorhandler(404)
def page_not_found(e: Exception) -> Tuple[str, int]:
    _e: Exception = e

    return render_template("404.html"), 404


@main.app_errorhandler(500)
def internal_server_error(e: Exception) -> Tuple[str, int]:
    _e: Exception = e

    return render_template("500.html"), 500
