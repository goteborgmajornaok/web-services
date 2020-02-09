import json
from urllib.error import HTTPError

import requests

import db_handler
import definitions

config = definitions.get_config()

headers = {"content-type": "application/json; charset=UTF-8",
           'Authorization': 'Bearer ' + config['WordpressApi']['token']}

api_endpoint = config['WordpressApi']['base_url'] + '/users'


def get_request(query_params):
    try:
        r = requests.get(url=api_endpoint, data=json.dumps(query_params), headers=headers)
    except HTTPError:
        return False, config['Errors']['wp_fail']
    return True, json.loads(r.text)


def users_with_attribute(attr, value):
    success, return_info = get_request({'search': value})
    if not success:
        return False, return_info
    if len(return_info) > 0:
        return False, config['Errors']['user_attr_exists'].format(attr, value)
    return True, ''


def create_user(eventor_id, email, username, password, first_name, last_name):
    email_unique, return_info = users_with_attribute('email', email)
    if not email_unique:
        return False, return_info

    username_unique, return_info = users_with_attribute('användarnamn', username)
    if not username_unique:
        return False, return_info

    query_params = {'username': username,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name,
                    'name': first_name + ' ' + last_name,
                    'email': email
                    }
    try:
        r = requests.post(url=api_endpoint, data=json.dumps(query_params), headers=headers)
    except HTTPError:
        return False, config['Errors']['wp_fail']

    if r.status_code == 201:
        wp_dict = json.loads(r.text)
        db_handler.save_user(eventor_id, wp_dict['id'])

        return True, config['Messages']['created_user'].format(wp_dict['name'], wp_dict['username'])
    else:
        return False, config['Errors']['failed_create_user']
