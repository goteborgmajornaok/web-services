from flask import Flask
from members import members_app
from create_user import create_user_app
from definitions import get_config

config = get_config()

app = Flask(__name__)
app.config['SECRET_KEY'] = config['Flask']['secret_key']
app.register_blueprint(members_app)
app.register_blueprint(create_user_app)


#if __name__ == "__main__":
#    main_app.run(debug=True)
