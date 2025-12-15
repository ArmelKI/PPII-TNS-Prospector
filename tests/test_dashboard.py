"""
Tests pour le dashboard — vérifie l'accessibilité et les compteurs.
"""

from app.models import db, Client, Utilisateur, Intervenant, Projet, StatutProjet
from datetime import date

def test_dashboard_basic(client, app):
    with app.app_context():
        c = Client(
            id_client=1,
            raison_sociale="Acme",
            mail_client="acme@example.com",
            telephone_client="0123456789",
            secteur="Industrie",
            date_dernier_contact=date.today(),
            latitude=48.8566,
            longitude=2.3522
        )
        db.session.add(c)
        db.session.flush()
        u = Utilisateur()
        db.session.add(u)
        db.session.flush()
        i = Intervenant()
        db.session.add(i)
        p = Projet()
        db.session.add(p)
        db.session.commit()

    res = client.get("/")
    assert res.status_code == 200
    text = res.get_data(as_text=True)
    assert "Clients" in text and "Projets" in text and "Intervenants" in text
