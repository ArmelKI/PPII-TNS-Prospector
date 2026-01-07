from flask import Blueprint, render_template, flash, send_file, request, redirect, url_for
from flask_login import login_required
from app.models import *
import csv 
import io
import zipfile 
from sqlalchemy import inspect, text, MetaData, Boolean
from app.permissions import manage_intervenants_required


import_export_bp = Blueprint('import_export', __name__, url_prefix='/import_export')

@import_export_bp.route('/')
@manage_intervenants_required
def main():
    return render_template('import_export.html')

@import_export_bp.route('/export-db')
@manage_intervenants_required
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


@import_export_bp.route('/import-db',methods=['POST'])
@manage_intervenants_required
def import_db(): 
    """
    Importe le fichier zip donner en entree contenant toutes les donnees
    """
    
    if 'file' not in request.files:
        return "Aucun fichier trouvé", 400
    file = request.files['file']
    if file.filename == '':
        return "Aucun fichier sélectionné", 400
    
    engine = db.engine
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    try:
        with engine.begin() as conn:
            # On désactive la vérifcication sur les clés étrangères pour l'ordre d'insertion
            conn.execute(text("SET session_replication_role = 'replica';"))
            
            with zipfile.ZipFile(file) as z:
                for filename in z.namelist():
                    if not filename.endswith('.csv'):
                        continue
                    
                    table_name = filename.replace('.csv', '')
                    
                    if table_name in metadata.tables:
                        table = metadata.tables[table_name]
                        
                        # 2. On vide la table
                        conn.execute(table.delete())
                        
                        # 3. Lecture du CSV
                        with z.open(filename) as f:
                            csv_file = io.TextIOWrapper(f, encoding='utf-8')
                            reader = csv.DictReader(csv_file)
                            
                            data_to_insert = []
                            for row in reader:
                                # Nettoyage des clés du CSV (enlève les espaces invisibles potentiels)
                                row_clean_keys = {k.strip(): v for k, v in row.items()}
                                
                                clean_row = {}
                                
                                # STRATÉGIE INVERSÉE : On boucle sur les colonnes de la DB
                                # (C'est la source de vérité)
                                for column in table.columns:
                                    col_name = column.name
                                    
                                    
                                    if col_name in row_clean_keys:
                                        value = row_clean_keys[col_name]
                                        
                                        # Gestion NULL
                                        if value == '':
                                            clean_row[col_name] = None
                                        
                                        # Gestion BOOLEAN
                                        elif isinstance(column.type, Boolean):
                                            val_str = str(value).lower()
                                            if val_str == 'true':
                                                clean_row[col_name] = True
                                            elif val_str == 'false':
                                                clean_row[col_name] = False
                                            else:
                                                # cas  pour 1 ou 0 
                                                clean_row[col_name] = bool(int(value)) if value.isdigit() else False
                                        
                                        
                                        else:
                                            clean_row[col_name] = value
                                
                                
                                if clean_row:
                                    data_to_insert.append(clean_row)
                            
                          
                            if data_to_insert:
                                conn.execute(table.insert(), data_to_insert)

            # On reactive la vérification 
            conn.execute(text("SET session_replication_role = 'origin';"))
        flash("Import réussi (Structure DB prioritaire) !", "success")
        return redirect(url_for('import_export.main'))

    except Exception as e:
        # Affiche l'erreur complète pour le debug
        import traceback
        traceback.print_exc()
        return f"Erreur : {str(e)}", 500
     



    