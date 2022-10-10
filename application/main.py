import logging

from flask import Flask

from definitions import config

flaskapp = Flask(__name__)
flaskapp.config['SECRET_KEY'] = config['Flask']['secret_key']

if config.getboolean('Endpoints', 'members'):
    from application.members import members_app

    flaskapp.register_blueprint(members_app)

if config.getboolean('Endpoints', 'register'):
    from application.register import create_user_app

    flaskapp.register_blueprint(create_user_app)

if config.getboolean('Endpoints', 'calendarfeed'):
    from application.calenderfeeds import calendarfeeds_app

    flaskapp.register_blueprint(calendarfeeds_app)

if config.getboolean('Endpoints', 'inventory'):
    from application.user_inventory import user_inventory_app

    flaskapp.register_blueprint(user_inventory_app)


@flaskapp.route("/")
def home_view():
    return ""
