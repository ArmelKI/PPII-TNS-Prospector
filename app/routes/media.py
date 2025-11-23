# app/routes/media.py
import os
from flask import Blueprint, current_app, request, redirect, url_for, flash, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from app.models import db, Intervenant, Utilisateur
from datetime import datetime

media_bp = Blueprint("media", __name__, url_prefix="/media")

# Configuration : accepter ces extensions
ALLOWED_EXT = {"png","jpg","jpeg","gif","pdf","doc","docx","ppt","pptx"}

def allowed(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in ALLOWED_EXT

def uploads_dir():
    base = current_app.static_folder or "static"
    path = os.path.join(base, "uploads")
    os.makedirs(path, exist_ok=True)
    return path

@media_bp.route("/upload/profile_photo/<int:id>", methods=["POST"])
def upload_profile_photo(id):
    file = request.files.get("photo")
    if not file or file.filename == "":
        return jsonify({"error":"no file"}), 400
    if not allowed(file.filename):
        return jsonify({"error":"type not allowed"}), 400

    filename = secure_filename(f"user_{id}_photo_{int(datetime.utcnow().timestamp())}_{file.filename}")
    saved = os.path.join(uploads_dir(), filename)
    file.save(saved)

    # On suppose que Utilisateur a photo_url (string)
    user = Utilisateur.query.get_or_404(id)
    user.photo_url = f"uploads/{filename}"
    db.session.commit()
    return jsonify({"ok": True, "url": url_for('static', filename=user.photo_url)}), 200

@media_bp.route("/upload/document/<int:id>", methods=["POST"])
def upload_document(id):
    """
    Upload document (cv / certificat) pour un intervenant.
    form: file, doc_type
    """
    file = request.files.get("document")
    doc_type = request.form.get("doc_type", "other")
    if not file or file.filename == "":
        return jsonify({"error":"no file"}), 400
    if not allowed(file.filename):
        return jsonify({"error":"type not allowed"}), 400

    filename = secure_filename(f"interv_{id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
    saved = os.path.join(uploads_dir(), filename)
    file.save(saved)

    # create document row (if you created table documents in DB)
    # Using raw SQL to avoid modifying models.py; your DBA will add an ORM table if desired.
    sql = """
    INSERT INTO documents (id_intervenant, filename, file_url, doc_type)
    VALUES (:id_interv, :fn, :url, :dt)
    """
    db.session.execute(sql, {"id_interv": id, "fn": file.filename, "url": f"uploads/{filename}", "dt": doc_type})
    db.session.commit()
    return jsonify({"ok": True, "url": url_for('static', filename=f"uploads/{filename}")}), 200

@media_bp.route("/uploads/<path:filename>")
def get_upload(filename):
    # sécurité : serve via static folder (here we simply redirect)
    return send_from_directory(uploads_dir(), filename)
