"""
app.py est le point d'entrée pour exécution locale

Ce fichier importe la factory create_app et lance l'application.
Ne contient pas de logique métier.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug=True uniquement en dev local
    app.run(host="0.0.0.0", port=8000, debug=True)
