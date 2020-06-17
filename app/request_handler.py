import requests
from requests import HTTPError

from definitions import config


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
