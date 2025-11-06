import enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

db = SQLAlchemy()

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

# Tables d'associations (pour les relations plusieurs-à-plusieurs)
# Un projet peut avoir plusieurs intervenants et un intervenant peut travailler sur plusieurs projets
# Humainement un intervenant peut peut-être pas travailler sur plusieurs projets en même temps, il peut en effectuer deux de suite par exemple

intervenant_projet = db.Table(
    "intervenant_projet",
    db.Column("id_intervenant", db.Integer, db.ForeignKey("intervenants.id_intervenant", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    db.Column("id_projet", db.Integer, db.ForeignKey("projets.id_projet", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
)

intervenant_competence = db.Table(
    "intervenant_competence",
    db.Column("id_intervenant", db.Integer, db.ForeignKey("intervenants.id_intervenant", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    db.Column("id_competence", db.Integer, db.ForeignKey("competences.id_competence", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
)


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
    projets_crees = db.relationship("Projet", back_populates="utilisateur_creation")
    intervenant = db.relationship("Intervenant", uselist=False, back_populates="utilisateur")

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

    projets = db.relationship("Projet", back_populates="client")
    interactions = db.relationship("InteractionClient", back_populates="client")

    def __repr__(self):
        return f"Client {self.raison_sociale}"

class EtatRelation(db.Model):
    __tablename__ = "etats_relation"

    id_etat_relation = db.Column(db.Integer, primary_key=True)
    nom_relation = db.Column(db.Text, nullable=False)

    interactions = db.relationship("InteractionClient", back_populates="etat_relation")

class InteractionClient(db.Model):
    # Attention, ce n'est pas une table de correspondance entre deux autres tables
    # elle permet de faire figurer, à un instant t, l'état de la relation entre TNS et le client
    __tablename__ = "interaction_client"

    id_interaction = db.Column(db.Integer, primary_key=True)
    id_client = db.Column(db.Integer, db.ForeignKey("clients.id_client", ondelete="SET NULL", onupdate="CASCADE"))
    date_interaction = db.Column(db.Date, nullable=False)
    detail_interaction = db.Column(db.Text)
    id_etat_relation = db.Column(db.Integer, db.ForeignKey("etats_relation.id_etat_relation", ondelete="SET NULL", onupdate="CASCADE"))

    client = db.relationship("Client", back_populates="interactions")
    etat_relation = db.relationship("EtatRelation", back_populates="interactions")

class Competence(db.Model):
    __tablename__ = "competences"

    id_competence = db.Column(db.Integer, primary_key=True)
    nom_competence = db.Column(db.String(255), nullable=False)

    intervenants = db.relationship("Intervenant", secondary=intervenant_competence, back_populates="competences")


class Intervenant(db.Model):
    __tablename__ = "intervenants"

    id_intervenant = db.Column(db.Integer, db.ForeignKey("utilisateurs.id_utilisateur", ondelete="CASCADE"), primary_key=True)
    disponible_actuellement = db.Column(db.Boolean, nullable=False)
    nombre_heures_disponibles = db.Column(db.Float(8))

    utilisateur = db.relationship("Utilisateur", back_populates="intervenant")
    competences = db.relationship("Competence", secondary=intervenant_competence, back_populates="intervenants")
    projets = db.relationship("Projet", secondary=intervenant_projet, back_populates="intervenants")
    taches = db.relationship("Tache", back_populates="intervenant_tache")

    def __repr__(self):
        return f"Intervenant {self.utilisateur.nom_utilisateur}"



class Projet(db.Model):
    __tablename__ = "projets"

    id_projet = db.Column(db.Integer, primary_key=True)
    nom_projet = db.Column(db.String(255), nullable = False)
    statut_projet = db.Column(Enum(StatutProjet, name="statut_projet"), nullable=False)
    date_debut_projet = db.Column(db.Date, nullable = False)
    date_fin_projet = db.Column(db.Date, nullable=False)
    id_client = db.Column(db.Integer, db.ForeignKey("clients.id_client", ondelete="SET NULL", onupdate="CASCADE"))
    id_utilisateur_creation = db.Column(db.Integer, db.ForeignKey("utilisateurs.id_utilisateur", ondelete="SET NULL", onupdate="CASCADE"))

    client = db.relationship("Client", back_populates="projets")
    utilisateur_creation = db.relationship("Utilisateur", back_populates="projets_crees")
    jalons = db.relationship("JalonProjet", back_populates="projet")
    intervenants = db.relationship("Intervenant", secondary=intervenant_projet, back_populates="projets")

    def __repr__(self):
        return f"Projet {self.nom_projet}"
    

class JalonProjet(db.Model):
    __tablename__ = "jalon_projet"

    id_jalon = db.Column(db.Integer, primary_key=True)
    id_projet = db.Column(db.Integer, db.ForeignKey("projets.id_projet", ondelete="SET NULL", onupdate="CASCADE"))
    nom_jalon = db.Column(db.String(255), nullable=False)
    statut_jalon = db.Column(Enum(StatutJalon, name="statut_jalon"))
    date_debut_jalon = db.Column(db.Date)
    date_fin_jalon = db.Column(db.Date)

    projet = db.relationship("Projet", back_populates="jalons")
    taches = db.relationship("Tache", back_populates="jalon")

class Tache(db.Model):
    __tablename__ = "taches"

    id_tache = db.Column(db.Integer, primary_key=True)
    id_jalon = db.Column(db.Integer, db.ForeignKey("jalon_projet.id_jalon", ondelete="SET NULL", onupdate="CASCADE"))
    nom_tache = db.Column(db.Text)
    description_tache = db.Column(db.Text)
    statut_tache = db.Column(Enum(StatutTache, name="statut_tache"), nullable=False)
    date_delai_tache = db.Column(db.Date)
    id_intervenant_tache = db.Column(db.Integer, db.ForeignKey("intervenants.id_intervenant", ondelete="SET NULL", onupdate="CASCADE"))

    jalon = db.relationship("JalonProjet", back_populates="taches")
    intervenant_tache = db.relationship("Intervenant", back_populates="taches")

    def __repr__(self):
        return f"<Tache {self.nom_tache}>"