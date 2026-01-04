from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import db, Utilisateur, Role



class LoginForm(FlaskForm):
    usermail = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

class RegisterForm(FlaskForm):
    @staticmethod
    def get_roles() -> list[tuple[str, str]]:
        roles: list[Role] = Role.query.all()
        return [(role.id_role, role.nom_role) for role in roles]

    name = StringField('Nom', validators=[DataRequired()])
    first_name = StringField('Prenom', validators=[DataRequired()])
    usermail = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField()
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    password2 = PasswordField('Mot de passe', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    submit = SubmitField('Créer un compte')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role.choices = self.get_roles()  # Needed to make db call when app_context is available

    def validate_usermail(self, email):
        user = Utilisateur.query.where(Utilisateur.mail_utilisateur == email.data).scalar()
        if user is not None:
            raise ValidationError('Email déjà utilisé.')
