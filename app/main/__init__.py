from flask import Blueprint


main: Blueprint = Blueprint("main", __name__)


from . import views, errors