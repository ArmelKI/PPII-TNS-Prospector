from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import db, Utilisateur



class LoginForm(FlaskForm):
    usermail = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

# TODO : Ajouter possibilité de set le role
class RegisterForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired()])
    first_name = StringField('Prenom', validators=[DataRequired()])
    usermail = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    password2 = PasswordField('Mot de passe', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    submit = SubmitField('Créer un compte')

    def validate_usermail(self, email):
        user = Utilisateur.query.where(Utilisateur.mail_utilisateur == email.data).scalar()
        if user != None:
            raise ValidationError('Email déjà utiliser.')
