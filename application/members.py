import logging
from io import BytesIO
from requests import HTTPError
import pyexcel as pe
import datetime
from flask import Blueprint, request, flash, render_template, make_response

from application.eventor_utils import validate_eventor_user, get_members_matrix
from application.flask_forms import EventorForm
from common import KnownError
from definitions import config

members_app = Blueprint('members', __name__)


def get_file_name():
    datetime_str = datetime.datetime.now().strftime('%Y-%m-%d')
    return datetime_str + ' ' + config['Member']['output_file_name'] + '.xls'


def member_records_response():
    try:
        members_matrix = get_members_matrix()
    except HTTPError as e:
        logging.error(e)
        raise KnownError(config['Messages']['eventor_fail'], 'eventor')

    try:
        io = BytesIO()
        sheet = pe.Sheet(members_matrix)
        io = sheet.save_to_memory("xls", io)
    except Exception as e:
        logging.error(e)
        raise KnownError(config['Messages']['file_creation_error'], 'eventor')

    filename = get_file_name()
    try:
        output = make_response(io.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=" + filename
        return output
    except IOError as e:
        logging.error(e, e.args)
        raise KnownError(config['Messages']['io_error'], 'eventor')


@members_app.route('/members', methods=['GET', 'POST'])
def members():
    form = EventorForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        logging.info(f'Members POST request from {request.remote_addr}')
        try:
            # validate user
            validate_eventor_user(form.username.data, form.password.data)
            return member_records_response()
        except KnownError as e:
            flash(str(e), category=e.error_type[1])
    elif request.method == 'GET':
        logging.info(f'Members GET request from {request.remote_addr}')

    return render_template('member_records.html', form=form, organisation=config['General']['name'],
                           site=config['Wordpress']['url'],
                           eventor_forgot_password=config['EventorApi']['lost_password_url'])
