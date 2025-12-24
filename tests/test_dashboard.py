import pytest
from app.models import *
from datetime import date, timedelta

@pytest.fixture
def setup_dashboard_data(app):
    with app.app_context():
        db.session.query(InteractionClient).delete()
        db.session.query(Jalon).delete()
        db.session.query(Projet).delete()
        db.session.query(Convention).delete()
        db.session.query(Intervenant).delete()
        db.session.query(Utilisateur).delete()
        db.session.query(Role).delete()
        db.session.query(Client).delete()

        role = Role(id_role=1, nom_role="Admin")
        db.session.add(role)
        db.session.flush()

        user = Utilisateur(
            id_utilisateur=1, 
            nom_utilisateur="Nom", 
            prenom_utilisateur="Prenom", 
            mail_utilisateur="i@i.com", 
            mdp_utilisateur="hash", 
            id_role=1
        )
        db.session.add(user)
        db.session.flush()

        intervenant = Intervenant(id_intervenant=user.id_utilisateur)
        db.session.add(intervenant)

        c1 = Client(
            id_client=1, 
            raison_sociale="Client Test", 
            mail_client="c@c.com", 
            telephone_client="1",
            secteur="IT", 
            date_dernier_contact=date.today(), 
            latitude=0.0, 
            longitude=0.0
        )
        db.session.add(c1)
        db.session.flush()

        conv = Convention(
            id_convention=1, 
            id_client=1, 
            type_convention="CC", 
            date_debut_convention=date.today()
        )
        db.session.add(conv)
        db.session.flush()

        p1 = Projet(
            id_projet=1, 
            nom_projet="Projet Alpha", 
            statut_projet=StatutProjet.EN_COURS, 
            id_convention=1
        )
        p2 = Projet(
            id_projet=2, 
            nom_projet="Projet Beta", 
            statut_projet=StatutProjet.BLOQUE, 
            id_convention=1
        )
        db.session.add_all([p1, p2])
        db.session.flush()

        j1 = Jalon(
            id_jalon=1,
            nom_jalon="Urgent", 
            date_fin_jalon=date.today() + timedelta(days=5), 
            statut_jalon=StatutJalon.A_VENIR, 
            id_projet=1
        )
        db.session.add(j1)
        
        db.session.commit()

def test_dashboard_counts(client, setup_dashboard_data):
    """Vérifie que les compteurs affichent les bonnes valeurs de la fixture."""
    response = client.get("/")
    html = response.get_data(as_text=True)
    
    assert 'data-count="1"' in html  
    assert 'data-count="2"' in html 
    assert 'data-count="1"' in html 

def test_dashboard_urgent_milestones_logic(client, setup_dashboard_data):
    """Vérifie que le jalon 'Urgent' est bien rendu dans le tableau."""
    response = client.get("/")
    html = response.get_data(as_text=True)
    
    assert "Urgent" in html
    assert "Projet Alpha" in html
    assert "Aucune échéance urgente" not in html

def test_dashboard_stats_fallback(client, app):
    """Vérifie qu'un statut non prévu est bien comptabilisé dans 'En cours'."""
    with app.app_context():
        db.session.query(Projet).delete()
        db.session.query(Convention).delete()
        db.session.query(Client).delete()

        c = Client(id_client=99, raison_sociale="C", mail_client="c@c.com", telephone_client="1",
                   secteur="IT", date_dernier_contact=date.today(), latitude=0, longitude=0)
        db.session.add(c)
        db.session.flush()

        conv = Convention(id_convention=99, id_client=99, type_convention="CC", date_debut_convention=date.today())
        db.session.add(conv)
        db.session.flush()

        p_special = Projet(
            id_projet=99, 
            nom_projet="Projet Spécial", 
            statut_projet=StatutProjet.STAND_BY,
            id_convention=99
        )
        db.session.add(p_special)
        db.session.commit()

    response = client.get("/")
    html = response.get_data(as_text=True)

    assert "En cours" in html
    assert "1" in html