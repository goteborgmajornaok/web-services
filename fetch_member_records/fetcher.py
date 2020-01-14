import json
import definitions
from eventor_request_handler import eventor_request
import xml.etree.cElementTree as ET
import csv
import datetime

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

    if len(values) == 1 and values[0].isdigit():
        return '="{}"'.format(values[0])

    return ', '.join(values)


def extract_info(columns_dict: dict, person: ET.Element):
    person_info_dict = {column: '' for column in columns_dict.keys()}

    for column, path in columns_dict.items():
        person_info_dict[column] = find_value(path, person)

    return person_info_dict


def fetch_members():
    organisation_id = config['EventorApi']['organisation_id']
    method = config['FetchMemberRecords']['api_method'].format(organisation_id)
    xml_str = eventor_request(method, {'includeContactDetails': True})
    return ET.fromstring(xml_str)


def xml_to_csv(root: ET, outfile: str):
    parse_settings_file = definitions.ROOT_DIR + '\\' + config['FetchMemberRecords']['parse_settings_file']
    with open(parse_settings_file, encoding='utf-8') as f:
        columns_dict = json.load(f)

    with open(outfile, encoding='utf-8', mode='w', newline='') as f:
        f.write(u'\ufeff')
        csv_writer = csv.writer(f, delimiter=',')

        csv_writer.writerow(columns_dict.keys())

        for person in root:
            person_info = extract_info(columns_dict, person)
            csv_writer.writerow(person_info.values())


datetime_str = datetime.datetime.now().strftime('%Y-%m-%d')
xml_to_csv(fetch_members(), '{} Matrikel GMOK.csv'.format(datetime_str))
