from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_user, logout_user
from urllib.parse import urlsplit
from app.forms import LoginForm, RegisterForm
from app.models import db, Utilisateur
from app.permissions import manage_users_required, encode_perms



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
