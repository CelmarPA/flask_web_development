from flask import Blueprint


auth: Blueprint = Blueprint("auth", __name__)


from . import views
