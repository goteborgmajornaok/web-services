import json

import requests
from requests import HTTPError

from app.main import config


def api_request(method, api_endpoint, error_message, error_category, query_params=None, headers=None):
    try:
        if method == 'GET':
            r = requests.get(url=api_endpoint, params=query_params, headers=headers)
        elif method == 'POST':
            r = requests.post(url=api_endpoint, params=query_params, headers=headers)
        else:
            raise Exception(config['Errors']['request_bug'])
        if r.status_code != 200:
            raise HTTPError()
    except HTTPError:
        raise Exception(error_message, error_category)

    r.encoding = 'utf-8'
    return r.text


def wordpress_request(method, api_endpoint, query_params=None, headers=None):
    response = api_request(method, api_endpoint, config['Errors']['wp_fail'], 'wordpress', query_params, headers)
    return json.loads(response)


def eventor_request(method, api_endpoint, query_params=None, headers=None):
    return api_request(method, api_endpoint, config['Errors']['eventor_fail'], 'eventor', query_params, headers)
