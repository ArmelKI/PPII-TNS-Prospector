from flask import Blueprint, render_template, flash
from flask_login import login_required
from app.models import *



import_export_bp = Blueprint('import_export', __name__, url_prefix='/import_export')

@import_export_bp.route('/')
def main():
    return render_template('import_export.html')
