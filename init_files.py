import os
from app import create_app
from app.models import Intervenant, db

app = create_app()

BASE_DIR = os.path.join(app.root_path, 'static')
DIRS = [
    'uploads/avatars',
    'uploads/documents'
]

def get_dummy_svg(text, color="#e0e0e0"):
    """
    Generates a simple placeholder image (SVG) with centered text.
    
    Args:
        text (str): The text to display inside the image (e.g., user initials).
        color (str): The background color of the rectangle.
        
    Returns:
        str: The complete SVG code as a string.
    """
    return f'''<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="{color}"/>
      <text x="50%" y="50%" font-family="Arial" font-size="20" 
            fill="#555" dominant-baseline="middle" text-anchor="middle">
        {text}
      </text>
    </svg>'''

def create_dummy_pdf(path):
    """
    Creates a dummy PDF file at the specified path.
    
    Note: It's technically a text file with a .pdf extension, 
    but it's enough to test if the browser can download/open the file link.
    """
    with open(path, 'w') as f:
        f.write("This is a dummy document generated automatically by the init_files.py script.")

with app.app_context():
    print("📁 Checking storage directories...")
    
    for d in DIRS:
        full_path = os.path.join(BASE_DIR, d)
        os.makedirs(full_path, exist_ok=True)

    intervenants = Intervenant.query.all()
    print(f"🔄 Generating missing files for {len(intervenants)} intervenants...")

    count_img = 0
    count_pdf = 0

    for i in intervenants:

        if not i.photo_identite:
            filename = f"avatar_{i.id_intervenant}.svg"
            i.photo_identite = f"uploads/avatars/{filename}"
        
        rel_path = i.photo_identite.replace('\\', '/')
        full_path_img = os.path.join(app.root_path, 'static', rel_path)
        
        if not os.path.exists(full_path_img):
            os.makedirs(os.path.dirname(full_path_img), exist_ok=True)
            with open(full_path_img, "w") as f:
                initials = f"{i.utilisateur.prenom_utilisateur[0]}{i.utilisateur.nom_utilisateur[0]}" if i.utilisateur else "??"
                f.write(get_dummy_svg(initials))
            count_img += 1

        if not i.cv or i.cv == "uploads/documents/dummy.pdf":
            filename = f"cv_{i.id_intervenant}.pdf"
            i.cv = f"uploads/documents/{filename}"
        
        rel_path_cv = i.cv.replace('\\', '/')
        full_path_cv = os.path.join(app.root_path, 'static', rel_path_cv)

        if not os.path.exists(full_path_cv):
            os.makedirs(os.path.dirname(full_path_cv), exist_ok=True)
            create_dummy_pdf(full_path_cv)
            count_pdf += 1

    db.session.flush()

    db.session.commit()
    
    print(f"✅ Success! {count_img} images and {count_pdf} PDFs generated.")
    print("👉 Avatars and documents should now be visible on the website.")