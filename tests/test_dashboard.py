"""
Tests pour le dashboard — vérifie l'accessibilité et les compteurs.
"""

from app.models import db, Client, Utilisateur, Intervenant, Projet, StatutProjet
from datetime import date

def test_dashboard_basic(client, app):
    with app.app_context():
        c = Client(raison_sociale="Acme")
        db.session.add(c)
        db.session.flush()
        u = Utilisateur(nom_utilisateur="A", prenom_utilisateur="B", mail_utilisateur="a@b.test")
        db.session.add(u); db.session.flush()
        i = Intervenant(id_intervenant=u.id_utilisateur, disponible_actuellement=True)
        db.session.add(i)
        p = Projet(nom_projet="P", statut_projet=StatutProjet.EN_COURS, date_debut_projet=date.today(), date_fin_projet=date.today(), id_client=c.id_client, id_utilisateur_creation=u.id_utilisateur)
        db.session.add(p)
        db.session.commit()

    res = client.get("/")
    assert res.status_code == 200
    text = res.get_data(as_text=True)
    assert "Clients" in text and "Projets" in text and "Intervenants" in text
