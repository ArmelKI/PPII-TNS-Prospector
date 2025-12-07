from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user
from app.forms import LoginForm
from app.models import Utilisateur



auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    # Si l'utilisateur est déjà connecté, on saute la page
    if current_user.is_authenticated:
        return redirect('/')

    form = LoginForm()

    # Si le formulaire n'a pas été envoyé correctement
    if not form.validate_on_submit():
        return render_template('login.html', form=form)

    # On vérifie les données fournies
    user: Utilisateur = Utilisateur.query.where(Utilisateur.mail_utilisateur == form.usermail.data).scalar()
    if user is None or not user.check_password(form.password.data):
        flash("Invalid username or password")
        return redirect(url_for('auth.login_page'))

    login_user(user, remember=form.remember_me.data)
    flash(f'Utilisateur {user.prenom_utilisateur} {user.nom_utilisateur} connecté')
    return redirect('/')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login_page'))
