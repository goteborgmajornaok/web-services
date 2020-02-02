from urllib.error import HTTPError
import definitions
from db_handler import check_eventor_id
from eventor_parser import find_value
from eventor_request_handler import eventor_request
import xml.etree.cElementTree as ET
import sqlite3

config = definitions.get_config()


def person_in_organisation(person_info, organisation_id: int):
    return person_info.find('OrganisationId') is not None and int(
        person_info.find('OrganisationId').text) == organisation_id


def person_has_account(person_info):
    person_id = int(person_info.find('PersonId').text)
    return check_eventor_id(person_id)


def validate(eventor_user, eventor_password):
    organisation_id = int(config['EventorApi']['organisation_id'])

    if eventor_user is None or eventor_password is None:
        return config['Errors']['user_missing']

    try:
        person_info_str = eventor_request(config['User']['eventor_api_method'],
                                          headers={'Username': eventor_user, 'Password': eventor_password})
    except HTTPError:
        return config['Errors']['eventor_validate_fail']

    person_info = ET.fromstring(person_info_str)
    valid = person_in_organisation(person_info, organisation_id) and not person_has_account(person_info)

    first_name = find_value([["PersonName", "Given"]], person_info)
    last_name = find_value([["PersonName", "Family"]], person_info)
    id = find_value([["PersonId"]], person_info)
    return valid, {'first_name': first_name, 'last_name': last_name, 'id': id}
