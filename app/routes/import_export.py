from flask import Blueprint, render_template, flash, send_file
from flask_login import login_required
from app.models import *
import csv 
import io
import zipfile 
from sqlalchemy import inspect, text


import_export_bp = Blueprint('import_export', __name__, url_prefix='/import_export')

@import_export_bp.route('/')
# @login_manager # On gerera les perm plus tard
def main():
    return render_template('import_export.html')


@import_export_bp.route('/export-db')
def export_db():
    zip_buffer = io.BytesIO() # fichier virtuel RAM
    engine = db.engine 
    
    with engine.connect() as conn: 
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED ) as zip_file: 
            inspector = inspect(engine)

            for table_name  in inspector.get_table_names():
                result = conn.execute(text(f'SELECT * FROM {table_name}'))
                csv_buffer= io.StringIO()
                writer = csv.writer(csv_buffer)
                writer.writerow(result.keys())
                writer.writerows(result.fetchall())
                zip_file.writestr(f"{table_name}.csv", csv_buffer.getvalue())
                
    zip_buffer.seek(0) # rend le zip lisible par le navigateur 

    return send_file(
        zip_buffer,
        download_name='ma_base_de_données.zip',
        as_attachment=True,
        mimetype='application/zip'
    )

