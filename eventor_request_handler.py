import urllib.request as url_req
import definitions

config = definitions.get_config()


def eventor_request(method: str, params: dict = None, headers: dict = None):
    eventor_api_settings = config['EventorApi']
    url = eventor_api_settings['base_url'] + method

    if params is not None and len(params) > 0:
        url += '?'
        for key in params.keys():
            url += key + '=' + str(params[key]) + '&'
        url = url[:-1]

    req = url_req.Request(url)
    req.add_header('ApiKey', eventor_api_settings['apikey'])

    if headers is not None and len(headers) > 0:
        for header, value in headers.items():
            req.add_header(header, value)

    return url_req.urlopen(req).read().decode('utf-8')
