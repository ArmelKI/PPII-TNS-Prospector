import os
from app import create_app
from app.models import Intervenant

app = create_app()

# Paths for static file directories we want to ensure exist
BASE_DIR = os.path.join(app.root_path, 'static')
DIRS = [
    'uploads/avatars',
    'uploads/documents'
]

def get_dummy_image(text, color="#ccc"):
    """
    Generate a simple SVG image as a string.
    This is handy for placeholder avatars or test images.

    Args:
        text (str): Text to display in the center of the image.
        color (str): Background color for the SVG (default: light gray).

    Returns:
        str: SVG image as a string.
    """
    return f'''<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="{color}"/>
      <text x="50%" y="50%" font-family="Arial" font-size="20" fill="black" dominant-baseline="middle" text-anchor="middle">{text}</text>
    </svg>'''

def create_dummy_pdf(path):
    """
    Create a dummy PDF file (actually just a text file with a .pdf extension).
    This is useful for testing file uploads or downloads.

    Args:
        path (str): Full path where the dummy PDF should be created.
    """
    with open(path, 'w') as f:
        f.write("This is a test document generated automatically.")

with app.app_context():
    # 1. Make sure all required directories exist
    for d in DIRS:
        full_path = os.path.join(BASE_DIR, d)
        os.makedirs(full_path, exist_ok=True)
        print(f"📁 Directory checked/created: {full_path}")

    # 2. Loop through all Intervenant records and generate their files
    intervenants = Intervenant.query.all()
    print(f"🔄 Generating files for {len(intervenants)} intervenants...")

    for i in intervenants:
        # Generate avatar image if the intervenant has a photo_identite path
        if i.photo_identite:
            # For testing, we want simple filenames (e.g., 'avatar_1.svg')
            fpath = os.path.join(app.root_path, 'static', i.photo_identite)
            # If the filename has no extension, add .svg by default for the test
            if not os.path.splitext(fpath)[1]: 
                fpath += ".svg"
                i.photo_identite += ".svg"  # Update the DB field so it matches the file

            # Write the SVG file to disk
            with open(fpath, "w") as f:
                f.write(get_dummy_image(f"ID {i.id_intervenant}"))

        # Generate dummy CV PDF if the intervenant has a CV path
        if i.cv:
            fpath = os.path.join(app.root_path, 'static', i.cv)
            create_dummy_pdf(fpath)

    # Commit any changes to the database (e.g., updated file extensions)
    from app.models import db
    db.session.commit()
    print("✅ Physical files created! Images and documents should now be available.")