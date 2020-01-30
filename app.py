from flask import Flask
from members import members_app
from create_user import create_user_app

main_app = Flask(__name__)
main_app.register_blueprint(members_app)
main_app.register_blueprint(create_user_app)

if __name__ == "__main__":
    main_app.run(debug=True)
