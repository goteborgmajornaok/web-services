import json
import xml.etree.cElementTree as ET
from datetime import date

from app.request_handler import api_request
from definitions import config

organisation_id = int(config['EventorApi']['organisation_id'])


def eventor_request(method, api_endpoint, query_params: dict = None, headers: dict = None):
    return api_request(method, api_endpoint, config['Errors']['eventor_fail'], 'eventor', query_params, headers)


def club_activities(start_date: date, end_date: date):
    query_params = {'from': start_date.strftime('%Y-%m-%d'),
                    'to': end_date.strftime('%Y-%m-%d'),
                    'organisationId': organisation_id}

    headers = {'ApiKey': config['EventorApi']['apikey']}
    xml_str = eventor_request('GET', config['EventorApi']['activities_endpoint'], query_params, headers)
    return ET.fromstring(xml_str)


def events(start_date: date, end_date: date, classification_ids: list, organisations_ids: list):
    query_params = {'fromDate': start_date.strftime('%Y-%m-%d'),
                    'toDate': end_date.strftime('%Y-%m-%d'),
                    'classificationIds': ','.join(map(str, classification_ids)),
                    'organisationIds': ','.join(map(str, organisations_ids))}

    headers = {'ApiKey': config['EventorApi']['apikey']}
    xml_str = eventor_request('GET', config['EventorApi']['events_endpoint'], query_params, headers)
    return ET.fromstring(xml_str)


def org_name(id):
    headers = {'ApiKey': config['EventorApi']['apikey']}
    xml_str = eventor_request('GET', config['EventorApi']['organisation_endpoint'].format(id), headers=headers)
    root = ET.fromstring(xml_str)
    return root.find('Name').text


def extract_info(columns_dict: dict, person: ET.Element):
    person_info_dict = {column: '' for column in columns_dict.keys()}

    for column_name, column_dict in columns_dict.items():
        person_info_dict[column_name] = find_value(column_dict['path'], person)
        if 'length' in column_dict.keys():
            person_info_dict[column_name] = person_info_dict[column_name][:int(column_dict['length'])]

    return person_info_dict


def person_in_organisation(person_info, organisation_id: int):
    roles = person_info.findall('Role')
    for r in roles:
        role_org = r.find('OrganisationId')
        if role_org is not None and int(role_org.text) == organisation_id:
            return True
    return False


def fetch_members():
    api_endpoint = config['EventorApi']['members_endpoint']
    query_params = {'includeContactDetails': 'true'}
    headers = {'ApiKey': config['EventorApi']['apikey']}
    xml_str = eventor_request('GET', api_endpoint, query_params=query_params, headers=headers)

    return ET.fromstring(xml_str)


def get_membership(person_info):
    organisation_id = person_info.find('OrganisationId')
    if organisation_id is None or organisation_id.text != config['EventorApi']['organisation_id']:
        return 'tranings***REMOVED***'
    return '***REMOVED***'


def find_value(path: list, person: ET.Element):
    element = person
    element_path = path[0]
    for child in element_path:
        element = element.find(child)
        if element is None:
            return ''

    if len(path) == 1:
        return element.text

    values = [value for key, value in element.attrib.items() if key in path[1]]

    return ', '.join(values)


def validate_eventor_user(eventor_user, eventor_password):
    headers = {'Username': eventor_user, 'Password': eventor_password}
    person_info_str = eventor_request('GET', config['EventorApi']['authenticate_endpoint'],
                                      headers=headers)

    person_info = ET.fromstring(person_info_str)
    # Check if Eventor user is member of organization
    if not person_in_organisation(person_info, organisation_id):
        raise Exception(config['Errors']['not_in_club'], 'eventor')

    # Create dict with essential person info
    eventor_info_dict = dict()
    eventor_info_dict['first_name'] = find_value([["PersonName", "Given"]], person_info)
    eventor_info_dict['last_name'] = find_value([["PersonName", "Family"]], person_info)
    eventor_info_dict['id'] = find_value([["PersonId"]], person_info)
    eventor_info_dict['membership'] = get_membership(person_info)

    return eventor_info_dict


def get_members_matrix():
    parse_settings_file = config['Member']['parse_settings_file']
    with open(parse_settings_file, encoding='utf-8') as f:
        columns_dict = json.load(f)

    # Fetch XML with current members
    root = fetch_members()

    array = [list(columns_dict.keys())]

    for i, person in enumerate(root):
        person_info = extract_info(columns_dict, person)
        array.append(list(person_info.values()))

    return array
