import definitions
from flask import Blueprint, request, flash, render_template
from eventor_validate import validate
from user_form import UserForm
import wp_user_handling

create_user_app = Blueprint('wordpress_create_user', __name__)
config = definitions.get_config()


def post_user(eventor_user, eventor_password, email, username, password):
    valid_user, return_info = validate(eventor_user, eventor_password)
    if not valid_user:
        return False, (return_info, 'eventor')

    result, message = wp_user_handling.create_user(return_info['id'], email, username, password,
                                                   return_info['first_name'], return_info['last_name'])
    return result, (message, 'wordpress')


@create_user_app.route('/user', methods=['GET', 'POST'])
def user():
    form = UserForm(request.form)

    if request.method == 'POST':
        if form.validate_on_submit():
            result, message = post_user(form.eventor_user.data, form.eventor_password.data, form.email.data,
                                        form.username.data, form.password.data)
            if result:
                return render_template('success.html', message=message)
            else:
                flash(message[0], category=message[1])

    return render_template('create_form.html', form=form)
