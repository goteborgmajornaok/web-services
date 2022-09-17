from flask import Flask

from application.members import members_app
from application.register import create_user_app
from application.calenderfeeds import calendarfeeds_app
from application.user_inventory import user_inventory_app
from definitions import config

flaskapp = Flask(__name__)
flaskapp.config['SECRET_KEY'] = config['Flask']['secret_key']
flaskapp.register_blueprint(members_app)
flaskapp.register_blueprint(create_user_app)
flaskapp.register_blueprint(calendarfeeds_app)
flaskapp.register_blueprint(user_inventory_app)


@flaskapp.route("/")
def home_view():
    return ""
