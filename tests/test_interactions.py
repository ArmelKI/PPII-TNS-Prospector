from app.models import InteractionClient, Client, EtatRelation, db
from datetime import date, timedelta
import pytest
from sqlalchemy.exc import IntegrityError

def test_liste_interactions_display(logged_in_client, app):
    """Vérifie l'affichage de la liste des interactions."""
    with app.app_context():
        # Utilisation de db.session.get pour éviter les doublons si déjà créé
        etat = db.session.get(EtatRelation, 1)
        if not etat:
            etat = EtatRelation(id_etat_relation=1, libelle_relation="Prospect")
            db.session.add(etat)
        
        nouveau_client = Client(
            id_client=1,
            # On remplit les champs obligatoires selon ton modèle
            raison_sociale="Ma Super Entreprise",
            mail_client="test@test.com",
            telephone_client="0102030405",
            secteur="Informatique",
            date_dernier_contact=date.today(),
            latitude=48.8566,
            longitude=2.3522
        )
        db.session.add(nouveau_client)
        db.session.commit()

        inter = InteractionClient(
            id_client=1,
            date_interaction=date.today(),
            detail_interaction="Appel de prospection",
            id_etat_relation=1
        )
        db.session.add(inter)
        db.session.commit()

    response = logged_in_client.get("/interactions/")
    assert response.status_code == 200
    assert b"Appel de prospection" in response.data

def test_liste_interactions_sorting(logged_in_client, app):
    """Vérifie que les interactions sont triées par date décroissante."""
    with app.app_context():
        etat = db.session.get(EtatRelation, 1)
        if not etat:
            etat = EtatRelation(id_etat_relation=1, libelle_relation="Suivi")
            db.session.add(etat)
            
        client_test = Client(
            id_client=2, # ID différent pour éviter les conflits
            raison_sociale="Entreprise Tri",
            mail_client="tri@test.com",
            telephone_client="0000",
            secteur="Test",
            date_dernier_contact=date.today(),
            latitude=0.0,
            longitude=0.0
        )
        db.session.add(client_test)
        db.session.commit()

        date_recent = date.today()
        date_ancien = date.today() - timedelta(days=5)

        inter_ancien = InteractionClient(
            id_client=2, 
            detail_interaction="Interaction Ancienne", 
            date_interaction=date_ancien,
            id_etat_relation=1
        )
        inter_recent = InteractionClient(
            id_client=2, 
            detail_interaction="Interaction Recente", 
            date_interaction=date_recent,
            id_etat_relation=1
        )
        
        db.session.add_all([inter_ancien, inter_recent])
        db.session.commit()

    response = logged_in_client.get("/interactions/")
    assert response.status_code == 200
    
    html = response.data.decode()
    index_recent = html.find("Interaction Recente")
    index_ancien = html.find("Interaction Ancienne")
    
    assert index_recent != -1
    assert index_ancien != -1
    # Dans le HTML, le plus récent doit apparaître AVANT (index plus petit)
    assert index_recent < index_ancien

@pytest.fixture
def base_data(app):
    with app.app_context():
        # Nettoyage pour repartir sur une base saine
        db.session.query(InteractionClient).delete()
        
        client_test = Client(
            id_client=10, 
            raison_sociale="Client Test", 
            mail_client="test@test.com",
            telephone_client="000",
            secteur="Test",
            date_dernier_contact=date.today(),
            latitude=0.0,
            longitude=0.0
        )
        
        etat_test = db.session.get(EtatRelation, 1)
        if not etat_test:
            etat_test = EtatRelation(id_etat_relation=1, libelle_relation="Prospect")
            db.session.add(etat_test)
            
        db.session.add(client_test)
        db.session.commit()
    return {"id_client": 10, "id_etat": 1}

def test_add_interaction_redirects(logged_in_client, base_data):
    """Vérifie la redirection vers la fiche client après ajout."""
    response = logged_in_client.post("/interactions/add", data={
        "id_client": 10,
        "detail": "Test Redirection",
        "id_etat_relation": 1
    })
    
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/clients/10")

def test_add_interaction_db_persistence(logged_in_client, app, base_data):
    """Vérifie que l'interaction est bien enregistrée en base."""
    logged_in_client.post("/interactions/add", data={
        "id_client": 10,
        "detail": "Verification SQL",
        "id_etat_relation": 1
    })
    
    with app.app_context():
        inter = InteractionClient.query.filter_by(detail_interaction="Verification SQL").first()
        assert inter is not None
        assert inter.id_client == 10
        assert inter.date_interaction == date.today()

def test_add_interaction_missing_client_fails(logged_in_client, app, base_data):
    """Vérifie le comportement en cas de client manquant."""
    # On s'attend à ce que l'appel lève une IntegrityError à cause du id_client=None
    from sqlalchemy.exc import IntegrityError
    
    with pytest.raises(IntegrityError):
        logged_in_client.post(
            "/interactions/add", 
            data={"detail": "Sans client"}
        )