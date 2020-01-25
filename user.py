import definitions
from flask import Blueprint, request
from eventor_request_handler import eventor_request

user_app = Blueprint('user', __name__)
config = definitions.get_config()


@user_app.route('/user/validate')
def validate():
    eventor_user = request.headers.get('Username')
    eventor_password = request.headers.get('Password')

    return eventor_request(config['User']['eventor_api_method'],
                           headers={'Username': eventor_user, 'Password': eventor_password})


@user_app.route('/user/add')
def add():
    return 'Not implemented'
