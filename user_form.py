from wtforms import Form, validators, StringField, PasswordField, SubmitField
from wtforms.validators import EqualTo, Email, DataRequired
from flask_wtf import FlaskForm


class UserForm(FlaskForm):
    eventor_user = StringField('Användarnamn', [DataRequired(message='Ange användarnamn')],
                               render_kw={
                                   'placeholder': 'Personummer (ååmmdd-xxxx) eller IdrottOnline-inlogg (IIDXXXXXXX)'})
    eventor_password = PasswordField('Lösenord', [DataRequired(message='Ange lösenord')],
                                     render_kw={'placeholder': 'Lösenord Eventor/IdrottOnline'})
    email = StringField('Email',
                        [Email(message='Ange giltig mailadress'), DataRequired(message='Ange en email-adress')],
                        render_kw={'placeholder': 'Ange email (kan användas till max 1 användare på gmok.se)'})
    username = StringField('Användarnamn',
                           [DataRequired(message='Välj ett lösenord')],
                           render_kw={'placeholder': 'Välj användarnamn (kan ej ändras senare)'})
    password = PasswordField('Lösenord', [DataRequired(message='Välj ett användarnamn')],
                             render_kw={'placeholder': 'Välj lösenord'})
    confirm_password = PasswordField('Upprepa lösenord', [EqualTo('password', message='Lösenorden matchar inte')],
                                     render_kw={'placeholder': 'Upprepa lösenord'})
    submit = SubmitField('Skapa användare')
