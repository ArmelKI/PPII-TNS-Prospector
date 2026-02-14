from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FieldList, FormField, HiddenField, Label
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from wtforms.widgets import ListWidget, CheckboxInput
from app.models import db, Utilisateur, Role
from app.permissions import permission_table





class LoginForm(FlaskForm):
    usermail = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

class CheckboxItem(FlaskForm):
    checked = BooleanField()
    id = HiddenField()
    label = HiddenField()

class RegisterForm(FlaskForm):
    @staticmethod
    def get_roles() -> list[tuple[str, str]]:
        roles: list[Role] = Role.query.all()
        return [(role.id_role, role.nom_role) for role in roles]

    name = StringField('Nom', validators=[DataRequired()])
    first_name = StringField('Prenom', validators=[DataRequired()])
    usermail = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField()
    perms_fields = FieldList(
        FormField(CheckboxItem),
        label='Permissions'
    )
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    password2 = PasswordField('Mot de passe (confirmation)', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    submit = SubmitField('Créer un compte')

    def __init__(self, *args, **kwargs):
        perms_data = list(enumerate(permission_table))

        super().__init__(*args, **kwargs)
        self.role.choices = self.get_roles()  # Needed to make db call when app_context is available
        if not self.is_submitted():
            for perm in perms_data:
                self.perms_fields.append_entry({
                'id': perm[0],
                'label': perm[1],
                'checked': False
                })

    def validate_usermail(self, email):
        user = Utilisateur.query.where(Utilisateur.mail_utilisateur == email.data).scalar()
        if user is not None:
            raise ValidationError('Email déjà utilisé.')

class UpdateUserForm(FlaskForm):
    @staticmethod
    def get_roles() -> list[tuple[str, str]]:
        roles: list[Role] = Role.query.all()
        return [(role.id_role, role.nom_role) for role in roles]

    role = SelectField()
    perms_fields = FieldList(
        FormField(CheckboxItem),
        label='Permissions'
    )
    submit = SubmitField('Modifier')

    def __init__(self, *args, **kwargs):
        perms_data = list(enumerate(permission_table))

        super().__init__(*args, **kwargs)
        self.role.choices = self.get_roles()  # Needed to make db call when app_context is available
        if not self.is_submitted():
            for perm in perms_data:
                self.perms_fields.append_entry({
                'id': perm[0],
                'label': perm[1],
                'checked': False
                })

class ChangePWForm(FlaskForm):

    old_password = PasswordField('Mot de passe actuel', validators=[DataRequired()])
    password = PasswordField('Nouveau mot de passe', validators=[DataRequired()])
    password2 = PasswordField('Nouveau mot de passe (confirmation)', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    submit = SubmitField('Modifier mot de passe')

    def validate_old_password(self, password):
        if not self.user.check_password(password.data):
            raise ValidationError('Mot de passe incorrecte.')

    def __init__(self, user: Utilisateur, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user  # Needed to make db call when app_context is available

class ChangeEmailForm(FlaskForm):

    usermail = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Nouveau mot de passe', validators=[DataRequired()])
    submit = SubmitField('Modifier email')

    def validate_password(self, password):
        if not self.user.check_password(password.data):
            raise ValidationError('Mot de passe incorrecte.')

    def __init__(self, user: Utilisateur, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user  # Needed to make db call when app_context is available
