import enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

db = SQLAlchemy()

class Intervenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    competences = db.Column(db.String(255), nullable=False)
    disponibilite = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Intervenant {self.nom}>"
    

class StatutProjet(enum.Enum):
    PAS_COMMENCE = "Pas commencé"
    EN_COURS = "En cours"
    TERMINE = "Terminé"
    BLOQUE = "Bloqué"
    STAND_BY = "Stand-By"

class StatutJalon(enum.Enum):
    A_VENIR = "À venir"
    ACTUEL = "Actuel"
    PASSE = "Passé"

class StatutTache(enum.Enum):
    PAS_COMMENCE = "Pas commencé"
    EN_COURS = "En cours"
    TERMINE = "Terminé"
    BLOQUE = "Bloqué"
    STAND_BY = "Stand-By"

class Utilisateur(db.Model):
    id_utilisateur = db.Column(db.Integer, primary_key=True)
    prenom_utilisateur = db.Column(db.String(255), nullable=False)
    nom_utilisateur = db.Column(db.String(255), nullable=False)
    mail_utilisateur = db.Column(db.String(255), nullable=False, unique=True)
    mdp_utilisateur = db.Column(db.String(255), nullable=True)

    clients_ajoutes = db.relationship("Client", back_populates="utilisateur_ajout")

    def __repr__(self):
        return f"Utilisateur {self.nom_utilisateur} {self.prenom_utilisateur}"

class Client(db.Model):
    id_client = db.Column(db.Integer, primary_key=True)
    raison_sociale = db.Column(db.String(255), nullable=False)
    mail_client = db.Column(db.String(255))
    telephone_client = db.Column(db.String(12))
    secteur = db.Column(db.String)
    dernier_contact = db.Column(db.Date)
    id_utilisateur_ajout = db.Column(db.Integer, db.ForeignKey("utilisateurs.id_utilisateur"))
    latitude = db.Column(db.Float(8))
    longitude = db.Column(db.Float(8))

    utilisateur_ajout = db.relationship("Utilisateur", back_populates="clients_ajoutes")


    def __repr__(self):
        return f"Client {self.raison_sociale}"