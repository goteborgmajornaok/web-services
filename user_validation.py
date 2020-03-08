from urllib.error import HTTPError
import definitions
from eventor_parser import find_value
from eventor_request_handler import eventor_request
import xml.etree.cElementTree as ET

config = definitions.get_config()

organisation_id = int(config['EventorApi']['organisation_id'])


def person_in_organisation(person_info, organisation_id: int):
    roles = person_info.findall('Role')
    for r in roles:
        role_org = r.find('OrganisationId')
        if role_org is not None and int(role_org.text) == organisation_id:
            return True
    return False


def validate_eventor_user(eventor_user, eventor_password):
    try:
        person_info_str = eventor_request(config['User']['authenticate_method'],
                                          headers={'Username': eventor_user, 'Password': eventor_password})
    except HTTPError:
        return False, config['Errors']['eventor_fail']

    person_info = ET.fromstring(person_info_str)
    if not person_in_organisation(person_info, organisation_id):
        return False, config['Errors']['not_in_club']

    first_name = find_value([["PersonName", "Given"]], person_info)
    last_name = find_value([["PersonName", "Family"]], person_info)
    id = find_value([["PersonId"]], person_info)
    return True, {'first_name': first_name, 'last_name': last_name, 'id': id}
