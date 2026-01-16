from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session, abort
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.orm import joinedload
from urllib.parse import urlsplit
from app.forms import LoginForm, RegisterForm, UpdateUserForm, ChangePWForm, ChangeEmailForm
from app.models import db, Utilisateur
from app.permissions import manage_users_required, encode_perms, list_perm
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import id_token
import os, string, secrets

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

CLIENT_CONFIG = {
    "web": {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

# The authorization URL and redirect URL must match the ones you specified when you created the OAuth client ID
AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    # If the user is already logged in, we skip the page
    if current_user.is_authenticated:
        return redirect('/')

    form = LoginForm()
    user = None

    # Special account check
    if form.is_submitted() and form.usermail.data in current_app.config['special_accounts_mails']:
        pass

    # If the form wasn't sent correctly
    elif not form.validate_on_submit():
        return render_template('login.html', form=form)

    # Validity check
    if user is None:   # Not equal to None when special account
        user: Utilisateur = Utilisateur.query.where(Utilisateur.mail_utilisateur == form.usermail.data).scalar()
    if user is None or not user.check_password(form.password.data):
        flash("Invalid username or password", "danger")
        return redirect(url_for('auth.login_page'))

    login_user(user, remember=form.remember_me.data)
    # Redirection management
    next_page = request.args.get('next')
    # URL sanitizer
    if not next_page or urlsplit(next_page).netloc != '':
        next_page = '/'
    flash(f'Utilisateur⋅trice {user.prenom_utilisateur} {user.nom_utilisateur} connecté⋅e', "success")
    return redirect(next_page)

@auth_bp.route("/login_google")
def login_google():
    flow = Flow.from_client_config(
        CLIENT_CONFIG, 
        scopes=["https://www.googleapis.com/auth/userinfo.email", "openid"]
    )
    # L'URL doit être celle enregistrée dans la console Google
    flow.redirect_uri = url_for('auth.callback', _external=True)
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='select_account')

    session['oauth_state'] = state # Utilise le même nom que dans callback
    return redirect(authorization_url)

@auth_bp.route("/callback")
def callback():
    flow = Flow.from_client_config(CLIENT_CONFIG, scopes=["https://www.googleapis.com/auth/userinfo.email", "openid"])
    flow.redirect_uri = url_for('auth.callback', _external=True)
    
    # Validation du state
    flow.fetch_token(authorization_response=request.url)
    
    if not session.get('oauth_state') == request.args.get('state'):
        abort(500) # State mismatch

    credentials = flow.credentials
    # Récupérer les infos de l'utilisateur (email) via l'id_token
    info = id_token.verify_oauth2_token(credentials.id_token, Request(), CLIENT_CONFIG['web']['client_id'])
    
    email = info.get('email')
    user = Utilisateur.query.filter_by(mail_utilisateur=email).first()

    if not user:
        prenom_nom = email.split("@")[0]
        prenom_lower, nom_lower = prenom_nom.split(".")[0], prenom_nom.split(".")[1]
        prenom, nom = prenom_lower[0].upper() + prenom_lower[1:], nom_lower[0].upper() + nom_lower[1:]
        user = Utilisateur(
            mail_utilisateur=email,
            prenom_utilisateur=prenom,
            nom_utilisateur=nom,
            id_role=2, # Role par défaut (ex: invité)
            permission=encode_perms([]) # Aucune permission par défaut
        )

        token_impossible = secrets.token_urlsafe(32)
        user.set_password(token_impossible)
        # On ne définit pas de mot de passe (connexion Google uniquement)
        db.session.add(user)
        db.session.commit()
        flash("Compte créé automatiquement avec Google.", "info")
    
    login_user(user)
    return redirect("/")

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Utilisateur⋅trice déconnecté⋅e', 'info')
    return redirect(url_for('auth.login_page'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@manage_users_required
def register_page():
    form = RegisterForm()

    # If the form wasn't sent correctly
    if not form.validate_on_submit():
        return render_template('register.html', form=form)

    # Evil data parsing
    perms = [int(perm_field.data['id']) for perm_field in form.perms_fields if perm_field.data['checked']]

    new_user = Utilisateur(
        prenom_utilisateur=form.first_name.data,
        nom_utilisateur=form.name.data,
        mail_utilisateur=form.usermail.data,
        permission=encode_perms(perms),
        id_role=form.role.data
    )
    new_user.set_password(form.password.data)

    db.session.add(new_user)
    db.session.commit()

    flash(f'Utilisateur⋅trice {form.first_name.data} {form.name.data} a été créé⋅e.', "success")
    return redirect(url_for('auth.register_page'))

@auth_bp.route('/users')
@manage_users_required
def list_users():
    all_users = Utilisateur.query.order_by(Utilisateur.nom_utilisateur, Utilisateur.prenom_utilisateur).options(joinedload(Utilisateur.role)).all()
    return render_template('users.html', users=all_users, list_perm=list_perm)

@auth_bp.route('/update', methods=['GET', 'POST'])
@manage_users_required
def update_user():
    form = UpdateUserForm()

    user_id = request.args.get('id')
    user: Utilisateur = Utilisateur.query.get_or_404(user_id)

    if not form.validate_on_submit():
        return render_template('modifier_utilisateur.html', form=form, user=user)

    perms = [int(perm_field.data['id']) for perm_field in form.perms_fields if perm_field.data['checked']]

    user.permission = encode_perms(perms)
    user.id_role = form.role.data

    db.session.flush()
    db.session.commit()

    return redirect(url_for('auth.list_users'))

@auth_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    pw_form = ChangePWForm(current_user)
    email_form = ChangeEmailForm(current_user)

    if pw_form.validate_on_submit():
        current_user.set_password(pw_form.password.data)
        db.session.flush()
        db.session.commit()
        flash('Mot de passe mis à jour.', 'success')
    elif email_form.validate_on_submit():
        current_user.usermail = email_form.usermail.data
        db.session.flush()
        db.session.commit()
        flash('Email de passe mis à jour.', 'success')
    else:
        return render_template('account.html', pw_form=pw_form, email_form=email_form)

    return redirect(url_for('auth.account', form=pw_form, email_form=email_form))

@auth_bp.post('/delete/<int:id>')
@manage_users_required
def delete(id: int):
    user = Utilisateur.query.get_or_404(id)
    flash(f'Utilisateur⋅trice {user.prenom_utilisateur} {user.nom_utilisateur} supprimé⋅e', "success")
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("auth.list_users"))
