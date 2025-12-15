import os
import secrets
from werkzeug.utils import secure_filename
from flask import current_app

def save_file(file, folder_name="documents"):
    """
    Saves an uploaded file to a specific folder and returns its relative path for database storage.

    Args:
        file: The file object to save (usually from a Flask request).
        folder_name (str): The subfolder under 'uploads' to store the file (e.g., 'documents', 'avatars').

    Returns:
        str or None: The relative path to the saved file (e.g., 'uploads/documents/my_cv_123.pdf'),
        or None if no file was provided.
    """
    if not file:
        return None  # No file to save, just return None

    # Make the filename safe for the filesystem (removes special chars, etc.)
    filename = secure_filename(file.filename)

    # Add a random hex to the filename to avoid name collisions
    random_hex = secrets.token_hex(4)
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{random_hex}{ext}"

    # Build the absolute path to the upload folder
    # This ensures files go into 'static/uploads/<folder_name>'
    upload_path = os.path.join(current_app.root_path, 'static', 'uploads', folder_name)
    os.makedirs(upload_path, exist_ok=True)  # Create the folder if it doesn't exist

    # Save the file to disk
    full_path = os.path.join(upload_path, new_filename)
    file.save(full_path)

    # Return the relative path (used for storing in the database or generating URLs)
    return f"uploads/{folder_name}/{new_filename}"