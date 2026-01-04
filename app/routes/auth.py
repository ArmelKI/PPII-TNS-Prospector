from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user
from urllib.parse import urlsplit
from app.forms import LoginForm, RegisterForm
from app.models import db, Utilisateur



auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    # If the user is already logged in, we skip the page
    if current_user.is_authenticated:
        return redirect('/')

    form = LoginForm()

    # If the form wasn't sent correctly
    if not form.validate_on_submit():
        return render_template('login.html', form=form)

    # Validity check
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
    flash(f'Utilisateur {user.prenom_utilisateur} {user.nom_utilisateur} connecté', "success")
    return redirect(next_page)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login_page'))

# TODO : Réserver la page register aux personnes autorisées

@auth_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    # If the user is already logged in, we skip the page
    if current_user.is_authenticated:
        return redirect('/')

    form = RegisterForm()

    # If the form wasn't sent correctly
    if not form.validate_on_submit():
        return render_template('register.html', form=form)

    new_user = Utilisateur(
        prenom_utilisateur=form.first_name.data,
        nom_utilisateur=form.name.data,
        mail_utilisateur=form.usermail.data,
        permission=0,
        id_role=1 # XXX Valeur par défaut
    )
    new_user.set_password(form.password.data)

    db.session.add(new_user)
    db.session.commit()

    flash(f'Utilisateur {form.first_name.data} {form.name.data} a été créé.', "success")
    return redirect(url_for('auth.register_page'))
