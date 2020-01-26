from urllib.error import HTTPError
import definitions
from flask import Blueprint, request
from eventor_request_handler import eventor_request
import xml.etree.cElementTree as ET

eventor_validate_app = Blueprint('eventor_validate', __name__)
config = definitions.get_config()

def person_in_organisation(person_info_str, organisation_id: int):
    person_info = ET.fromstring(person_info_str)
    return str(person_info.find('OrganisationId') is not None and int(
        person_info.find('OrganisationId').text) == organisation_id)


@eventor_validate_app.route('/personInOrganisation/<int:organisation_id>')
def validate(organisation_id: int):
    eventor_user = request.headers.get('Username')
    eventor_password = request.headers.get('Password')

    try:
        person_info_str = eventor_request(config['User']['eventor_api_method'],
                                          headers={'Username': eventor_user, 'Password': eventor_password})
        return person_in_organisation(person_info_str, organisation_id)
    except HTTPError:
        return config['Errors']['eventor_validate_fail']
