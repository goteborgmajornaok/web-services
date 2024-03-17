from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import EqualTo, Email, DataRequired, Length
from flask_wtf import FlaskForm

from definitions import config


eventor_cfg = config['EventorForm']
site_cfg = config['SiteForm']

class EventorForm(FlaskForm):
    username = StringField(eventor_cfg['user_label'], [DataRequired(message=eventor_cfg['user_warning'])],
                               render_kw={
                                   'placeholder': eventor_cfg['user_placeholder']})
    password = PasswordField(eventor_cfg['password_label'], [DataRequired(message=eventor_cfg['password_warning'])],
                                     render_kw={'placeholder': eventor_cfg['password_placeholder']})
    submit = SubmitField(eventor_cfg['submit_label'])


class UserForm(FlaskForm):
    eventor_user = StringField(eventor_cfg['user_label'], [DataRequired(message=eventor_cfg['user_warning'])],
                               render_kw={
                                   'placeholder': eventor_cfg['user_placeholder']})
    eventor_password = PasswordField(eventor_cfg['password_label'], [DataRequired(message=eventor_cfg['password_warning'])],
                                     render_kw={'placeholder': eventor_cfg['password_placeholder']})
    email = StringField(site_cfg['email_label'],
                        [Email(message=site_cfg['email_format_warning']), DataRequired(message=site_cfg['email_warning'])],
                        render_kw={'placeholder': site_cfg['email_placeholder']})
    password = PasswordField(site_cfg['password_label'], [DataRequired(message=site_cfg['password_warning']),
                                          Length(min=8, max=100, message=site_cfg['password_security_warning'])],
                             render_kw={'placeholder': site_cfg['password_placeholder']})
    confirm_password = PasswordField(site_cfg['confirm_password_label'], [EqualTo('password', message=site_cfg['confirm_password_warning'])],
                                     render_kw={'placeholder': site_cfg['confirm_password_placeholder']})
    submit = SubmitField(site_cfg['submit_label'])
