"""
app.py est le point d'entrée pour exécution locale

Ce fichier importe la factory create_app et lance l'application.
Ne contient pas de logique métier.
"""

from app import create_app
from sqlalchemy.exc import OperationalError, IntegrityError, ProgrammingError

# Wait for db to be ready
created = False
while not created:
    try:
        app = create_app(testing=False)
        created = True
    except OperationalError:
        print('\n\n\n\n\n⚠️⚠️⚠️ Waiting for db connection...\n\n\n\n\n')
    except (IntegrityError, ProgrammingError):
        print('\n\n\n\n\n⚠️⚠️⚠️ The DB seams to be brocken\n\n\n\n\n')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
