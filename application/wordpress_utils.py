import json
import logging

from application.request_handler import api_request
from definitions import config, tmp_config, write_tmp


def generate_token():
    api_endpoint = config['WordpressApi']['generate_token_endpoint']
    query_params = {'username': config['WordpressApi']['username'],
                    'password': config['WordpressApi']['password']}
    headers = {"content-type": "application/json; charset=UTF-8"}

    content = wordpress_request('POST', api_endpoint, query_params, headers)
    logging.info('Wordpress token generated')
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
    else:
        logging.info('Reusing Wordpress token')
    return tmp_config.get('WordpressApi', 'token')


def wordpress_request(method, api_endpoint, query_params=None, headers=None, success_codes=(200,)):
    response = api_request(method, api_endpoint, config['Errors']['wp_fail'], 'wordpress', query_params, headers,
                           success_codes=success_codes).text
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
        logging.warning(f'Wordpress user with eventor id {eventor_id} already exists')
        raise Exception(config['Errors']['already_registered'], 'wordpress')

    if not check_existing_user('email', email):
        logging.warning(f'Wordpress user with email {email} already exists')
        raise Exception(config['Errors']['user_attr_exists'].format('email', email), 'wordpress')

    logging.info(f'User with eventor id {eventor_id} not registered at Wordpress site')


def create_user(eventor_id, email, password, first_name, last_name, role):
    logging.info(f'Trying to create Wordpress user for eventor id {eventor_id}')
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
    logging.info(f'Wordpress user created for user with eventor id {eventor_id}')


def get_users(role=None, page=1, per_page=100):
    api_endpoint = config['WordpressApi']['user_endpoint']
    headers = get_headers()
    query_params = None
    if role is not None:
        query_params = {'roles': role, 'page': page, 'per_page': per_page}
    response = wordpress_request('GET', api_endpoint, query_params, headers)
    logging.info(f'List of Wordpress users retrieved')
    return response


def update_user(id, query_params):
    api_endpoint = config['WordpressApi']['user_endpoint'] + '/' + id
    headers = get_headers()
    response = wordpress_request('POST', api_endpoint, query_params, headers)
    logging.info(f'Wordpress user with id {id} updated')
    return response
