from app.eventor_parser import find_value
import xml.etree.cElementTree as ET

from app.main import config
from app.request_handler import eventor_request

organisation_id = int(config['EventorApi']['organisation_id'])


def person_in_organisation(person_info, organisation_id: int):
    roles = person_info.findall('Role')
    for r in roles:
        role_org = r.find('OrganisationId')
        if role_org is not None and int(role_org.text) == organisation_id:
            return True
    return False


def validate_eventor_user(eventor_user, eventor_password):
    headers = {'Username': eventor_user, 'Password': eventor_password}
    person_info_str = eventor_request('GET', config['EventorApi']['authenticate_endpoint'],
                                      headers=headers)

    person_info = ET.fromstring(person_info_str)
    # Check if Eventor user is member of organization
    if not person_in_organisation(person_info, organisation_id):
        raise Exception(config['Errors']['not_in_club'], 'eventor')

    # Create dict with essential person info
    person_info_dict = dict()
    person_info_dict['first_name'] = find_value([["PersonName", "Given"]], person_info)
    person_info_dict['last_name'] = find_value([["PersonName", "Family"]], person_info)
    person_info_dict['id'] = find_value([["PersonId"]], person_info)

    return person_info_dict
