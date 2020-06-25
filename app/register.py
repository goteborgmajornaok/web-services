from app import wordpress_utils
from flask import Blueprint, request, flash, render_template, Markup

from app.eventor_utils import validate_eventor_user
from app.flask_forms import UserForm
from definitions import config

create_user_app = Blueprint('wordpress_create_user', __name__)


def create_message(first_name, last_name):
    name = first_name + ' ' + last_name
    return config['Messages']['created_user'].format(name)


@create_user_app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm(request.form)

    if request.method == 'POST':
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

                message = create_message(eventor_profile['first_name'], eventor_profile['last_name'])

                return render_template('register_success.html', message=message)
            except Exception as e:
                flash(Markup(e.args[0]), category=e.args[1])

    return render_template('register_form.html', form=form)
