from urllib.error import HTTPError
import definitions
from flask import Blueprint, request
from eventor_request_handler import eventor_request
import xml.etree.cElementTree as ET
import sqlite3

eventor_validate_app = Blueprint('eventor_validate', __name__)
config = definitions.get_config()


def person_in_organisation(person_info_str, organisation_id: int):
    person_info = ET.fromstring(person_info_str)
    return person_info.find('OrganisationId') is not None and int(
        person_info.find('OrganisationId').text) == organisation_id


def person_has_account(person_info_str):
    person_info = ET.fromstring(person_info_str)
    person_id = int(person_info.find('PersonId').text)

    conn = sqlite3.connect('gmok-utils.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(ID) FROM USERS WHERE EVENTOR_PERSON_ID == ?", (person_id,))
    records = cursor.fetchall()

    return records[0][0] > 0


@eventor_validate_app.route('/personInOrganisation/<int:organisation_id>')
def validate(organisation_id: int):
    eventor_user = request.headers.get('Username')
    eventor_password = request.headers.get('Password')

    try:
        person_info_str = eventor_request(config['User']['eventor_api_method'],
                                          headers={'Username': eventor_user, 'Password': eventor_password})
    except HTTPError:
        return config['Errors']['eventor_validate_fail']

    if person_in_organisation(person_info_str, organisation_id) and not person_has_account(person_info_str):
        return 'True'
    return 'False'
