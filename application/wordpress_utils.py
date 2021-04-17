import json
import base64

from application.request_handler import api_request
from definitions import config, tmp_config, write_tmp


def generate_token():
    api_endpoint = config['WordpressApi']['generate_token_endpoint']
    query_params = {'username': config['WordpressApi']['username'],
                    'password': config['WordpressApi']['password']}
    headers = {"content-type": "application/json; charset=UTF-8"}

    content = wordpress_request('POST', api_endpoint, query_params, headers)
    return content['token']


def validate_token(token):
    api_endpoint = config['WordpressApi']['validate_token_endpoint']
    headers = {"content-type": "application/json; charset=UTF-8", 'Authorization': 'Bearer ' + token}

    content = wordpress_request('POST', api_endpoint, None, headers, success_codes=(200, 403))
    return content['data']['status'] == 200


def get_token():
    latest_token = tmp_config['WordpressApi']['token']
    if not validate_token(latest_token):
        new_token = generate_token()
        tmp_config.set('WordpressApi', 'token', new_token)
        write_tmp()
    return tmp_config.get('WordpressApi', 'token')


def wordpress_request(method, api_endpoint, query_params=None, headers=None, success_codes=(200,)):
    response = api_request(method, api_endpoint, config['Errors']['wp_fail'], 'wordpress', query_params, headers,
                           success_codes=success_codes)
    return json.loads(response)


def get_headers():
    token = get_token()
    return {"content-type": "application/json; charset=UTF-8", 'Authorization': 'Bearer ' + token}


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
    wordpress_request('POST', api_endpoint, query_params, headers, success_codes=(201,))


def get_users(role=None, page=1, per_page=100):
    api_endpoint = config['WordpressApi']['user_endpoint']
    headers = get_headers()
    query_params = None
    if role is not None:
        query_params = {'roles': role, 'page': page, 'per_page': per_page}
    return wordpress_request('GET', api_endpoint, query_params, headers)


def update_user(id, query_params):
    api_endpoint = config['WordpressApi']['user_endpoint'] + '/' + id
    headers = get_headers()
    return wordpress_request('POST', api_endpoint, query_params, headers)
