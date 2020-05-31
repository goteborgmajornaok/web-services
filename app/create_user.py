from app import definitions, wp_user_handling
from flask import Blueprint, request, flash, render_template
from app.user_validation import validate_eventor_user
from app.flask_forms import UserForm

create_user_app = Blueprint('wordpress_create_user', __name__)
config = definitions.get_config()


def post_user(eventor_user, eventor_password, email, password):
    valid_user, eventor_profile = validate_eventor_user(eventor_user, eventor_password)
    if not valid_user:
        return False, (eventor_profile, 'eventor')

    result, message = wp_user_handling.create_user(eventor_profile['id'], email, password,
                                                   eventor_profile['first_name'], eventor_profile['last_name'])
    return result, (message, 'wordpress')


@create_user_app.route('/user', methods=['GET', 'POST'])
def user():
    form = UserForm(request.form)

    if request.method == 'POST':
        if form.validate_on_submit():
            result, message = post_user(form.eventor_user.data, form.eventor_password.data, form.email.data,
                                        form.password.data)
            if result:
                return render_template('success.html', message=message)
            else:
                flash(message[0], category=message[1])

    return render_template('create_user_form.html', form=form)
