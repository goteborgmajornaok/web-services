import xml.etree.cElementTree as ET


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

    for column_name, column_dict in columns_dict.items():
        person_info_dict[column_name] = find_value(column_dict['path'], person)
        if 'length' in column_dict.keys():
            person_info_dict[column_name] = person_info_dict[column_name][:int(column_dict['length'])]

    return person_info_dict
