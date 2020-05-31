from flask import Flask
from app.members import members_app
from app.create_user import create_user_app
from app.definitions import get_config

config = get_config()

app = Flask(__name__)
app.config['SECRET_KEY'] = config['Flask']['secret_key']
app.register_blueprint(members_app)
app.register_blueprint(create_user_app)


@app.route("/")
def home_view():
        return "<h1>Välkommen till GMOK Eventor Utils</h1>"
