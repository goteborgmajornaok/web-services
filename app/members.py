import json
from io import StringIO
from urllib.error import HTTPError
from app import definitions
from app.eventor_parser import extract_info
from app.eventor_request_handler import eventor_request
import xml.etree.cElementTree as ET
import csv
import datetime
from flask import Blueprint, make_response, request, flash, render_template

from app.user_validation import validate_eventor_user
from app.flask_forms import EventorForm

members_app = Blueprint('members', __name__)
config = definitions.get_config()


def fetch_members():
    organisation_id = config['EventorApi']['organisation_id']
    method = config['Member']['eventor_api_method'].format(organisation_id)
    xml_str = eventor_request(method, {'includeContactDetails': True})
    return ET.fromstring(xml_str)


def write_members_csv(f: StringIO):
    f.write(u'\uFEFF')
    cw = csv.writer(f, quoting=csv.QUOTE_ALL)

    parse_settings_file = config['Member']['parse_settings_file']
    with open(parse_settings_file, encoding='utf-8') as f:
        columns_dict = json.load(f)

    root = fetch_members()

    cw.writerow(columns_dict.keys())

    for person in root:
        person_info = extract_info(columns_dict, person)
        cw.writerow(person_info.values())


def get_file_name():
    datetime_str = datetime.datetime.now().strftime('%Y-%m-%d')
    return config['Member']['output_file_name'].format(datetime_str)


def member_records_response():
    f = StringIO()
    try:
        write_members_csv(f)
    except HTTPError:
        return config['Errors']['eventor_fail']

    filename = get_file_name()

    output = make_response(f.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=" + filename
    output.headers["Content-type"] = "text/csv; charset=utf-8"
    return output


@members_app.route('/members', methods=['GET', 'POST'])
def members():
    form = EventorForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        valid_user, return_info = validate_eventor_user(form.username.data, form.password.data)
        if valid_user:
            return member_records_response()

        flash(return_info)

    return render_template('member_records.html', form=form)