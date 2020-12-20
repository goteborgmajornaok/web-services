import json

from application.request_handler import api_request
from definitions import config


def wordpress_request(method, api_endpoint, query_params=None, headers=None, success_code=200):
    response = api_request(method, api_endpoint, config['Errors']['wp_fail'], 'wordpress', query_params, headers,
                           success_code=success_code)
    return json.loads(response)


def get_token():
    api_endpoint = config['WordpressApi']['token_endpoint']
    query_params = {'username': config['WordpressApi']['username'],
                    'password': config['WordpressApi']['password']}
    headers = {"content-type": "application/json; charset=UTF-8"}

    content = wordpress_request('POST', api_endpoint, query_params, headers)
    return content['token']


def get_headers():
    return {"content-type": "application/json; charset=UTF-8", 'Authorization': 'Bearer ' + get_token()}


def check_existing_user(attr, value):
    api_endpoint = config['WordpressApi']['user_endpoint']
    query_params = {'search': value, 'context': 'edit'}
    headers = get_headers()

    content = wordpress_request('GET', api_endpoint, query_params, headers)

    if len(content) > 0:
        for r in content:
            if attr in r.keys() and r[attr] == value:
                return False
    return True


def check_user(eventor_id, email):
    if not check_existing_user('username', eventor_id):
        raise Exception(config['Errors']['already_registered'], 'wordpress')

    if not check_existing_user('email', email):
        raise Exception(config['Errors']['user_attr_exists'].format('email', email), 'wordpress')


def create_user(eventor_id, email, password, first_name, last_name, role):
    api_endpoint = config['WordpressApi']['user_endpoint']
    query_params = {'username': eventor_id,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name,
                    'name': first_name + ' ' + last_name,
                    'email': email,
                    'nickname': first_name + ' ' + last_name,
                    'roles': role
                    }
    headers = get_headers()
    wordpress_request('POST', api_endpoint, query_params, headers, success_code=201)


def get_users(role=None):
    api_endpoint = config['WordpressApi']['user_endpoint']
    headers = get_headers()
    query_params = None
    if role is not None:
        query_params = {'roles': role}
    return wordpress_request('GET', api_endpoint, query_params, headers)


def update_user(id, query_params):
    api_endpoint = config['WordpressApi']['user_endpoint'] + '/' + id
    headers = get_headers()
    return wordpress_request('POST', api_endpoint, query_params, headers)
