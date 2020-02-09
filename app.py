from flask import Flask
from members import members_app
from user import create_user_app
from definitions import get_config

config = get_config()

main_app = Flask(__name__)
main_app.register_blueprint(members_app)
main_app.register_blueprint(create_user_app)
main_app.config['SECRET_KEY'] = config['Flask']['secret_key']

if __name__ == "__main__":
    main_app.run(debug=True)
