from flask import Flask
from members import members_app
main_app = Flask(__name__)
main_app.register_blueprint(members_app)

if __name__ == "__main__":
    main_app.run(debug=True)