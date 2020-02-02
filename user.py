import json
import requests
import definitions
from flask import Blueprint, request
from eventor_validate import validate
import sqlite3

create_user_app = Blueprint('wordpress_create_user', __name__)
config = definitions.get_config()


def create_wp_user(query_params):
    headers = {"content-type": "application/json; charset=UTF-8",
               'Authorization': 'Bearer ' + config['WordpressApi']['token']}

    if any([v is None for v in query_params.values()]):
        return config['Errors']['fields_missing']

    api_endpoint = config['WordpressApi']['base_url'] + '/users'

    r = requests.post(url=api_endpoint, data=json.dumps(query_params), headers=headers)
    if r.status_code == 201:
        info = json.loads(r.text)
        return config['Messages']['created_user'].format(info['name'], info['username'],
                                                         config['Wordpress']['login_url'])
    else:
        return config['Errors']['failed_create_user']


@create_user_app.route('/user', methods=['POST'])
def post_user():
    eventor_user = request.headers.get('EventorUsername')
    eventor_password = request.headers.get('EventorPassword')
    valid_user, first_name, last_name = validate(eventor_user, eventor_password)
    if not valid_user:
        return config['Errors']['user_cannot_be_created']

    query_params = {'username': request.args.get('Username'),
                    'password': request.args.get('Password'),
                    'first_name': first_name,
                    'last_name': last_name,
                    'name': first_name + ' ' + last_name,
                    'email': request.args.get('Email')
                    }

    return create_wp_user(query_params)
