import json
from io import StringIO
import definitions
from eventor_request_handler import eventor_request
import xml.etree.cElementTree as ET
import csv
import datetime
from flask import Blueprint, make_response, request

members_app = Blueprint('members', __name__)
config = definitions.get_config()


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


def extract_info(columns_dict: dict, person: ET.Element):
    person_info_dict = {column: '' for column in columns_dict.keys()}

    for column, path in columns_dict.items():
        person_info_dict[column] = find_value(path, person)

    return person_info_dict


def fetch_members():
    organisation_id = config['EventorApi']['organisation_id']
    method = config['Members']['eventor_api_method'].format(organisation_id)
    xml_str = eventor_request(method, {'includeContactDetails': True})
    return ET.fromstring(xml_str)


def write_members_csv(f: StringIO):
    f.write(u'\uFEFF')
    cw = csv.writer(f, quoting=csv.QUOTE_ALL)

    parse_settings_file = definitions.ROOT_DIR + '\\' + config['FetchMemberRecords']['parse_settings_file']
    with open(parse_settings_file, encoding='utf-8') as f:
        columns_dict = json.load(f)

    root = fetch_members()

    cw.writerow(columns_dict.keys())

    for person in root:
        person_info = extract_info(columns_dict, person)
        cw.writerow(person_info.values())


def get_file_name():
    datetime_str = datetime.datetime.now().strftime('%Y-%m-%d')
    return config['FetchMemberRecords']['output_file_name'].format(datetime_str)


@members_app.route('/members')
def members():
    if request.headers.get('ApiKey') != config['ApiSettings']['apikey']:
        return config['Errors']['wrong_api_key']

    f = StringIO()
    write_members_csv(f)
    filename = get_file_name()

    output = make_response(f.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=" + filename
    output.headers["Content-type"] = "text/csv; charset=utf-8"

    return output
