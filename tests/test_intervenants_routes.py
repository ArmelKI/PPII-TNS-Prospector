"""
Tests pour intervenants — vérifie liste, ajout minimal (via DB), export CSV
"""

from app.models import db, Utilisateur, Intervenant, Competence

def test_list_empty(client):
    res = client.get("/intervenants/")
    assert res.status_code == 200
    # le template affiche le titre
    assert "Liste des Intervenants" in res.get_data(as_text=True)

def test_create_and_list(client, app):
    with app.app_context():
        u = Utilisateur(nom_utilisateur="Test", prenom_utilisateur="User", mail_utilisateur="t@u.test")
        db.session.add(u)
        db.session.flush()
        i = Intervenant(id_intervenant=u.id_utilisateur, disponible_actuellement=True, nombre_heures_disponibles=8)
        db.session.add(i)
        c = Competence(nom_competence="python")
        db.session.add(c)
        db.session.flush()
        i.competences.append(c)
        db.session.commit()

    res = client.get("/intervenants/")
    assert res.status_code == 200
    text = res.get_data(as_text=True)
    assert "Test" in text or "User" in text

def test_export_csv(client, app):
    with app.app_context():
        u = Utilisateur(nom_utilisateur="X", prenom_utilisateur="Y", mail_utilisateur="x@y.test")
        db.session.add(u); db.session.flush()
        i = Intervenant(id_intervenant=u.id_utilisateur, disponible_actuellement=False)
        db.session.add(i); db.session.commit()

    res = client.get("/intervenants/export")
    assert res.status_code == 200
    text = res.get_data(as_text=True)
    assert "ID" in text and "Nom" in text or "Prénom" in text
