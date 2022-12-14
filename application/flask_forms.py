from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import EqualTo, Email, DataRequired, Length
from flask_wtf import FlaskForm


class EventorForm(FlaskForm):
    username = StringField('Användarnamn', [DataRequired(message='Ange användarnamn')],
                           render_kw={
                               'placeholder': 'Personnummer (ååmmdd-xxxx) eller IdrottOnline-inlogg (IIDXXXXXXX)'})
    password = PasswordField('Lösenord', [DataRequired(message='Ange lösenord')],
                             render_kw={'placeholder': 'Lösenord Eventor/IdrottOnline'})
    submit = SubmitField('Hämta matrikel')


class UserForm(FlaskForm):
    eventor_user = StringField('Användarnamn', [DataRequired(message='Ange användarnamn')],
                               render_kw={
                                   'placeholder': 'Personummer (ååmmdd-xxxx) eller IdrottOnline-inlogg (IIDXXXXXXX)'})
    eventor_password = PasswordField('Lösenord', [DataRequired(message='Ange lösenord')],
                                     render_kw={'placeholder': 'Lösenord Eventor/IdrottOnline'})
    email = StringField('Email',
                        [Email(message='Ange giltig mailadress'), DataRequired(message='Ange en email-adress')],
                        render_kw={'placeholder': 'Ange email (kan användas till max 1 användare på {{site}})'})
    password = PasswordField('Lösenord', [DataRequired(message='Välj ett lösenord'),
                                          Length(min=8, max=100, message='Lösenordet måste innehålla minst 8 tecken')],
                             render_kw={'placeholder': 'Välj lösenord'})
    confirm_password = PasswordField('Upprepa lösenord', [EqualTo('password', message='Lösenorden matchar inte')],
                                     render_kw={'placeholder': 'Upprepa lösenord'})
    submit = SubmitField('Registrera ny användare')
