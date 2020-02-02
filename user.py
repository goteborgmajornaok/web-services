import json
import requests

import db_handler
import definitions
from flask import Blueprint, request
from eventor_validate import validate

create_user_app = Blueprint('wordpress_create_user', __name__)
config = definitions.get_config()


def create_wp_user(query_params):
    headers = {"content-type": "application/json; charset=UTF-8",
               'Authorization': 'Bearer ' + config['WordpressApi']['token']}

    if any([v is None for v in query_params.values()]):
        return config['Errors']['fields_missing']

    api_endpoint = config['WordpressApi']['base_url'] + '/users'

    return requests.post(url=api_endpoint, data=json.dumps(query_params), headers=headers)


@create_user_app.route('/user', methods=['POST'])
def post_user():
    eventor_user = request.headers.get('EventorUsername')
    eventor_password = request.headers.get('EventorPassword')
    valid_user, eventor_dict = validate(eventor_user, eventor_password)
    if not valid_user:
        return config['Errors']['unauthorized']

    query_params = {'username': request.args.get('Username'),
                    'password': request.args.get('Password'),
                    'first_name': eventor_dict['first_name'],
                    'last_name': eventor_dict['last_name'],
                    'name': eventor_dict['first_name'] + ' ' + eventor_dict['last_name'],
                    'email': request.args.get('Email')
                    }

    r = create_wp_user(query_params)

    if not r.status_code == 201:
        return config['Errors']['failed_create_user']

    wp_dict = json.loads(r.text)
    db_handler.save_user(eventor_dict['id'], wp_dict['id'])

    return config['Messages']['created_user'].format(wp_dict['name'], wp_dict['username'],
                                                     config['Wordpress']['login_url'])
