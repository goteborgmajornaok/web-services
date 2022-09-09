from definitions import config


def check_api_key(headers):
    auth = headers.get("X-Api-Key")
    return auth == config['ApiSettings']['ApiKey']
