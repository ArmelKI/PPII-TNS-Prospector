import json
from app.models import db, Client

def test_all_clients_returns_list(client, app):
    with app.app_context():
        db.create_all()
        c = Client(
            id_client=0, 
            raison_sociale="Entreprise très modale",
            mail_client = "entreprise@test.ts",
            telephone_client = "7777777",
            secteur = "modalite",
            date_dernier_contact = "2024-02-01",
            latitude = 77777777,
            longitude = 77777777)
        db.session.add(c) # on crée un client qu'on ajoute à la base de test pour s'assurer que tout marche bien
        db.session.commit()
