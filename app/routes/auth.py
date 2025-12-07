from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_user
from app.forms import LoginForm



auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()

    # Si le formulaire a été submit (méthode POST)
    if form.validate_on_submit():
        return redirect('/')

    return render_template('login.html', form=form)
