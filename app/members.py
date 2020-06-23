import json
from io import StringIO

from requests import HTTPError

import datetime
from flask import Blueprint, request, flash, render_template
import flask_excel as excel

from app.eventor_utils import validate_eventor_user, get_members_matrix
from app.flask_forms import EventorForm
from definitions import config

members_app = Blueprint('members', __name__)


def get_file_name():
    datetime_str = datetime.datetime.now().strftime('%Y-%m-%d')
    return config['Member']['output_file_name'].format(datetime_str)


def member_records_response():
    try:
        members_matrix = get_members_matrix()
    except HTTPError:
        raise Exception(config['Errors']['eventor_fail'], 'eventor')
    filename = get_file_name()
    try:
        print(members_matrix)
        response = excel.make_response_from_array(members_matrix, "xls", file_name=filename)
        print(response)
        return response
    except IOError:
        raise Exception(config['Errors']['io_error'], 'eventor')


@members_app.route('/members', methods=['GET', 'POST'])
def members():
    form = EventorForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        try:
            # validate user
            validate_eventor_user(form.username.data, form.password.data)
            return member_records_response()
        except Exception as e:
            flash(e.args[0], category=e.args[1])

    return render_template('member_records.html', form=form)
