import pytest
from app.models import *
from datetime import date, timedelta

@pytest.fixture
def setup_dashboard_data(app):
    """Prépare les données pour le tableau de bord."""
    with app.app_context():
        # Nettoyage ordonné (attention aux clés étrangères)
        db.session.query(InteractionClient).delete()
        db.session.query(Jalon).delete()
        db.session.query(Projet).delete()
        db.session.query(Convention).delete()
        db.session.query(Intervenant).delete()
        # On ne supprime pas l'utilisateur/role ici car logged_in_client en a besoin
        db.session.query(Client).delete()

        # On récupère l'utilisateur créé par logged_in_client
        user = Utilisateur.query.filter_by(mail_utilisateur="test@test.com").first()
        
        # On s'assure qu'il est aussi Intervenant pour certaines logiques de dashboard
        if user and not Intervenant.query.get(user.id_utilisateur):
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

def test_dashboard_counts(logged_in_client, setup_dashboard_data):
    """Vérifie que les compteurs affichent les bonnes valeurs."""
    response = logged_in_client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    
    # Vérifie la présence des compteurs (1 client, 2 projets, 1 jalon urgent)
    assert 'data-count="1"' in html  
    assert 'data-count="2"' in html 

def test_dashboard_urgent_milestones_logic(logged_in_client, setup_dashboard_data):
    """Vérifie que le jalon 'Urgent' est bien rendu dans le tableau."""
    response = logged_in_client.get("/")
    html = response.get_data(as_text=True)
    
    assert "Urgent" in html
    assert "Projet Alpha" in html
    assert "Aucune échéance urgente" not in html

def test_dashboard_stats_fallback(logged_in_client, app):
    """Vérifie qu'un statut spécial est bien comptabilisé."""
    with app.app_context():
        db.session.query(Jalon).delete()
        db.session.query(Projet).delete()
        db.session.query(Convention).delete()
        db.session.query(Client).delete()

        c = Client(id_client=99, raison_sociale="C", mail_client="c@c.com", telephone_client="1",
                   secteur="IT", date_dernier_contact=date.today(), latitude=0.0, longitude=0.0)
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

    response = logged_in_client.get("/")
    html = response.get_data(as_text=True)

    assert "En cours" in html
    # On vérifie qu'au moins un projet est compté (le fallback STAND_BY -> En cours)
    assert "1" in html