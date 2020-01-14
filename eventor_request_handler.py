import urllib.request as url_req
import definitions

config = definitions.get_config()


def eventor_request(method: str, queries: dict):
    eventor_api_settings = config['EventorApi']
    api_key = eventor_api_settings['apikey']
    url = eventor_api_settings['base_url'] + method

    if len(queries) > 0:
        url += '?'

    for key in queries.keys():
        url += key + '=' + str(queries[key]) + '&'

    url = url[:-1]

    req = url_req.Request(url)

    req.add_header('ApiKey', api_key)

    return url_req.urlopen(req).read().decode('utf-8')
