import enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

db = SQLAlchemy()

# Tables d'associations (pour les relations plusieurs-à-plusieurs)
# Un projet peut avoir plusieurs intervenants et un intervenant peut travailler sur plusieurs projets
# Humainement un intervenant peut peut-être pas travailler sur plusieurs projets en même temps, il peut en effectuer deux de suite par exemple

intervenant_projet = db.Table(
    "intervenant_projet",
    db.Column("id_intervenant", db.Integer, db.ForeignKey("intervenants.id_intervenant", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    db.Column("id_projet", db.Integer, db.ForeignKey("projets.id_projet", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
)

class StatutProjet(enum.Enum):
    # les statuts de projets, de tâches et de jalons sont des types énumérés, et non pas des tables
    # par conséquent on n'ajoute pas de dunder tablename

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

class Role(db.Model):
    __tablename__ = "roles"

    id_role = db.Column(db.Integer, primary_key=True)
    nom_role = db.Column(db.String, nullable=False)

class Utilisateur(db.Model):
    __tablename__ = "utilisateurs"

    id_utilisateur = db.Column(db.Integer, primary_key=True)
    prenom_utilisateur = db.Column(db.String(255), nullable=False)
    nom_utilisateur = db.Column(db.String(255), nullable=False)
    mail_utilisateur = db.Column(db.String(255), nullable=False, unique=True)
    mdp_utilisateur = db.Column(db.String(255), nullable=True)
    id_role = db.Column(db.Integer, db.ForeignKey("roles.id_role"))

    role = db.relationship("Role", backref="utilisateurs")

    def __repr__(self):
        return f"Utilisateur {self.nom_utilisateur} {self.prenom_utilisateur}"

class Client(db.Model):
    __tablename__ = "clients"

    id_client = db.Column(db.Integer, primary_key=True)
    raison_sociale = db.Column(db.String(255), nullable=False)
    mail_client = db.Column(db.String(255))
    telephone_client = db.Column(db.String(12))
    secteur = db.Column(db.String)
    dernier_contact = db.Column(db.Date)
    latitude = db.Column(db.Float(8))
    longitude = db.Column(db.Float(8))

    def __repr__(self):
        return f"Client {self.raison_sociale}"

class Etat_Relation(db.Model):
    __tablename__ = "relations"

    id_etat_relation = db.Column(db.Integer, primary_key=True)
    nom_relation = db.Column(db.String)

class Interaction_Client():
    # Attention, ce n'est pas une table de correspondance entre deux autres tables
    # elle permet de faire figurer, à un instant t, l'état de la relation entre TNS et le client
    __tablename__ = "interaction_client"

    id_interaction = db.Column(db.Integer, primary_key=True)
    id_client = db.Column(db.Integer)
    date_interaction = db.Column(db.Date)
    detail_interaction = db.Column(db.String)
    id_etat_relation = db.Column(db.Integer, db.ForeignKey("etats_relation.id_etat_relation"))



class Intervenant(db.Model):
    __tablename__ = "intervenants"

    id_intervenant = db.Column(db.Integer, db.ForeignKey("utilisateurs.id_utilisateur"), primary_key=True)
    disponible_actuellement = db.Column(db.Boolean, nullable=False)
    nombre_heures_disponibles = db.Column(db.Float(8))

    utilisateur = db.relationship("Utilisateur", backref="intervenant")
    projets = db.relationship("Projet", secondary=intervenant_projet, back_populates="intervenants")

    def __repr__(self):
        return f"Intervenant {self.utilisateur.nom_utilisateur}"


class Projet(db.Model):
    __tablename__ = "projets"

    id_projet = db.Column(db.Integer, primary_key=True)
    nom_projet = db.Column(db.String(255), nullable = False)
    statut_projet = db.Column(Enum(StatutProjet, name="statut_projet"), nullable=False)
    date_debut_projet = db.Column(db.Date, nullable = False)
    date_fin_projet = db.Column(db.Date, nullable=False)
    id_client = db.Column(db.Integer, db.ForeignKey("clients.id_client"))
    id_utilisateur_creation = db.Column(db.Integer, db.ForeignKey("utilisateurs.id_utilisateur"))

    client = db.relationship("Client", backref="projet")
    utilisateur_creation = db.relationship("Utilisateur", backref="projets_créés")

    intervenants = db.relationship("Intervenant", secondary=intervenant_projet, back_populates="projets")

    def __repr__(self):
        return f"Projet {self.nom_projet}"
    



class Intervenant(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    competences = db.Column(db.String(255), nullable=False)
    disponibilite = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Intervenant {self.nom}>"
