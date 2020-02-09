import json
import requests

import db_handler
import definitions
from flask import Blueprint, request, flash, render_template
from eventor_validate import validate
from user_form import UserForm

create_user_app = Blueprint('wordpress_create_user', __name__)
config = definitions.get_config()


def create_wp_user(query_params):
    headers = {"content-type": "application/json; charset=UTF-8",
               'Authorization': 'Bearer ' + config['WordpressApi']['token']}

    if any([v is None for v in query_params.values()]):
        return config['Errors']['fields_missing']

    api_endpoint = config['WordpressApi']['base_url'] + '/users'

    return requests.post(url=api_endpoint, data=json.dumps(query_params), headers=headers)


def post_user(eventor_user, eventor_password, email, username, password):
    valid_user, var = validate(eventor_user, eventor_password)
    if not valid_user:
        return False, var

    query_params = {'username': username,
                    'password': password,
                    'first_name': var['first_name'],
                    'last_name': var['last_name'],
                    'name': var['first_name'] + ' ' + var['last_name'],
                    'email': email
                    }

    r = create_wp_user(query_params)

    if r.status_code == 201:
        wp_dict = json.loads(r.text)
        db_handler.save_user(var['id'], wp_dict['id'])

        return True, config['Messages']['created_user'].format(wp_dict['name'], wp_dict['username'],
                                                               config['Wordpress']['login_url'])
    else:
        return False, config['Errors']['failed_create_user']


@create_user_app.route('/user', methods=['GET', 'POST'])
def user():
    form = UserForm(request.form)

    if request.method == 'POST':
        if form.validate_on_submit():
            success, message = post_user(form.eventor_user.data, form.eventor_password.data, form.email.data,
                                         form.username.data, form.password.data)
            if success:
                render_template('success.html')
            else:
                flash(message)

    return render_template('create_form.html', form=form)
