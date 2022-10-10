import logging

from application import wordpress_utils
from flask import Blueprint, request, flash, render_template, Markup

from application.eventor_utils import validate_eventor_user
from application.flask_forms import UserForm
from common import KnownError
from definitions import config

create_user_app = Blueprint('wordpress_create_user', __name__)


@create_user_app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm(request.form)

    if request.method == 'POST':
        logging.info(f'Register POST request from {request.remote_addr}')
        if form.validate_on_submit():
            try:
                eventor_user = form.eventor_user.data
                eventor_password = form.eventor_password.data
                # Validate Eventor user
                # Throw exception if user is not valid Eventor user or not member of organization
                eventor_profile = validate_eventor_user(eventor_user, eventor_password)

                email = form.email.data
                # Check Wordpress user
                # Throw exception if user already have Wordpress account
                wordpress_utils.check_user(eventor_profile['id'], email)

                password = form.password.data
                # Create Wordpress user
                wordpress_utils.create_user(eventor_profile['id'], email, password,
                                            eventor_profile['first_name'], eventor_profile['last_name'],
                                            eventor_profile['membership'])

                return render_template('register_success.html', message=config['Messages']['user_created'],
                                       login_url=config['Wordpress']['login_url'])
            except KnownError as e:
                flash(Markup(e.message), category=e.error_type)
    else:
        logging.info(f'Register GET request from {request.remote_addr}')

    return render_template('register_form.html', form=form, organisation=config['General']['name'],
                           site=config['Wordpress']['url'],
                           eventor_forgot_password=config['EventorApi']['lost_password_url'],
                           become_member_url=config['Wordpress']['become_member_url'].rstrip(),
                           guest_member=config['Wordpress']['guest_member']
                           )
