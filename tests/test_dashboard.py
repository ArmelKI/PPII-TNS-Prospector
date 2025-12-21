import pytest
from app.models import *
from datetime import date, timedelta

@pytest.fixture
def setup_dashboard_data(app):
    with app.app_context():
        # Nettoyage
        db.session.query(Jalon).delete()
        db.session.query(Projet).delete()
        db.session.query(Client).delete()
        
        # 1. Clients et Intervenants
        c1 = Client(raison_sociale="Client A", mail_client="a@a.com", telephone_client="1", 
                    secteur="IT", date_dernier_contact=date.today(), latitude=0, longitude=0)
        i1 = Intervenant(nom_intervenant="Nom", prenom_intervenant="Prenom", mail_intervenant="i@i.com")
        db.session.add_all([c1, i1])
        db.session.flush()

        # 2. Projets avec différents statuts
        p1 = Projet(nom_projet="P_EN_COURS", statut_projet=StatutProjet.EN_COURS, id_convention=1)
        p2 = Projet(nom_projet="P_BLOQUE", statut_projet=StatutProjet.BLOQUE, id_convention=1)
        p3 = Projet(nom_projet="P_TERMINE", statut_projet=StatutProjet.TERMINE, id_convention=1)
        db.session.add_all([p1, p2, p3])
        db.session.flush()

        # 3. Jalons (Un urgent, un lointain, un passé)
        j1 = Jalon(nom_jalon="Urgent", date_fin_jalon=date.today() + timedelta(days=10), 
                   statut_jalon=StatutJalon.A_VENIR, id_projet=p1.id_projet)
        j2 = Jalon(nom_jalon="Lointain", date_fin_jalon=date.today() + timedelta(days=100), 
                   statut_jalon=StatutJalon.A_VENIR, id_projet=p1.id_projet)
        j3 = Jalon(nom_jalon="Déjà Fait", date_fin_jalon=date.today() + timedelta(days=5), 
                   statut_jalon=StatutJalon.PASSE, id_projet=p1.id_projet)
        
        db.session.add_all([j1, j2, j3])
        db.session.commit()
        yield