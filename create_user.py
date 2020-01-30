import json

import requests
import definitions
from flask import Blueprint, request
from eventor_validate import validate
import sqlite3

create_user_app = Blueprint('wordpress_create_user', __name__)
config = definitions.get_config()


@create_user_app.route('/user', methods=['POST'])
def create():
    eventor_user = request.headers.get('EventorUsername')
    eventor_password = request.headers.get('EventorPassword')

    if not validate(eventor_user, eventor_password):
        return config['Errors']['user_cannot_be_created']

    query_params = {'username': request.args.get('Username'), 'password': request.args.get('Password'),
                    #'first_name': request.args.get('FirstName'), 'last_name': request.args.get('LastName'),
                    'email': request.args.get('Email')}

    headers = {"content-type": "application/json; charset=UTF-8",
               'Authorization': 'Bearer ' + config['WordpressApi']['token']}

    if any([v is None for v in query_params.values()]):
        return config['Errors']['fields_missing']

    api_endpoint = config['WordpressApi']['base_url'] + '/users'

    r = requests.post(url=api_endpoint, data=json.dumps(query_params), headers=headers)
    return r
