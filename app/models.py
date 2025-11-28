import enum
import sqlalchemy as sa
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum as SAEnum, CheckConstraint, Numeric

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
    db.Column("id_projet", db.Integer, db.ForeignKey("projets.id_projet", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    db.Column("date_debut_intervention", db.Date),
    db.Column("date_fin_intervention", db.Date)
)

intervenant_competence = db.Table(
    "intervenant_competence",
    db.Column("id_intervenant", db.Integer, db.ForeignKey("intervenants.id_intervenant", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    db.Column("id_competence", db.Integer, db.ForeignKey("competences.id_competence", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
)

intervenant_tache = db.Table(
    "intervenant_tache",
    db.Column("id_intervenant", db.Integer, db.ForeignKey("intervenants.id_intervenant", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    db.Column("id_tache", db.Integer, db.ForeignKey("taches.id_tache", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
)


class Role(db.Model):
    __tablename__ = "roles"

    id_role = db.Column(db.Integer, primary_key=True)
    nom_role = db.Column(db.String(100), nullable=False)

    utilisateurs = db.relationship("Utilisateur", back_populates="role")


class Utilisateur(db.Model):
    __tablename__ = "utilisateurs"

    id_utilisateur = db.Column(db.Integer, primary_key=True)
    prenom_utilisateur = db.Column(db.String(100), nullable=False)
    nom_utilisateur = db.Column(db.String(100), nullable=False)
    mail_utilisateur = db.Column(db.String(150), nullable=False, unique=True)
    mdp_utilisateur = db.Column(db.String(255), nullable=False)
    id_role = db.Column(db.Integer, db.ForeignKey("roles.id_role"), nullable = False)

    role = db.relationship("Role", back_populates="utilisateurs")
    intervenant = db.relationship("Intervenant", uselist=False, back_populates="utilisateur")

    def __repr__(self):
        return f"Utilisateur {self.nom_utilisateur} {self.prenom_utilisateur}"

class Intervenant(db.Model):
    __tablename__ = "intervenants"

    id_intervenant = db.Column(db.Integer, db.ForeignKey("utilisateurs.id_utilisateur", ondelete="CASCADE"), primary_key=True)
    disponible = db.Column(db.Boolean, nullable=False, server_default=sa.text('TRUE'))
    nb_heures_dispo = db.Column(db.Integer)
    bulletin_adhesion = db.Column(db.String(255))
    carte_etudiante = db.Column(db.String(255))
    carte_vitale = db.Column(db.String(255))
    piece_identite = db.Column(db.String(255))
    photo_identite = db.Column(db.String(255))
    cv = db.Column(db.String(255))

    utilisateur = db.relationship("Utilisateur", back_populates="intervenant")
    competences = db.relationship("Competence", secondary=intervenant_competence, back_populates="intervenants")
    projets = db.relationship("Projet", secondary=intervenant_projet, back_populates="intervenants")
    taches = db.relationship("Tache", secondary=intervenant_tache, back_populates="intervenants")

    def __repr__(self):
        nom = self.utilisateur.nom_utilisateur if self.utilisateur else str(self.id_intervenant)
        return f"Intervenant {nom}"
    
class Competence(db.Model):
    __tablename__ = "competences"

    id_competence = db.Column(db.Integer, primary_key=True)
    nom_competence = db.Column(db.String(150), nullable=False)

    intervenants = db.relationship("Intervenant", secondary=intervenant_competence, back_populates="competences")

class EtatRelation(db.Model):
    __tablename__ = "etats_relations"

    id_etat_relation = db.Column(db.Integer, primary_key=True)
    libelle_relation = db.Column(db.String(150), nullable=False)

    interactions = db.relationship("InteractionClient", back_populates="etat_relation")

class Client(db.Model):
    __tablename__ = "clients"

    id_client = db.Column(db.Integer, primary_key=True)
    raison_sociale = db.Column(db.String(200), nullable=False)
    mail_client = db.Column(db.String(150))
    telephone_client = db.Column(db.String(30))
    secteur = db.Column(db.String(100))
    date_dernier_contact = db.Column(db.Date)
    latitude = db.Column(db.Numeric(10, 7))
    longitude = db.Column(db.Numeric(10, 7))

    conventions = db.relationship("Convention", back_populates="client")
    interactions = db.relationship("InteractionClient", back_populates="client")

    def __init__(self, id_client, raison_sociale, mail_client, telephone_client, secteur, 
                 dernier_contact, latitude, longitude):
        self.id_client = id_client
        self.raison_sociale = raison_sociale
        self.mail_client = mail_client
        self.telephone_client = telephone_client
        self.secteur = secteur
        self.dernier_contact = dernier_contact
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return f"Client {self.raison_sociale}"


class InteractionClient(db.Model):
    # Attention, ce n'est pas une table de correspondance entre deux autres tables
    # elle permet de faire figurer, à un instant t, l'état de la relation entre TNS et le client
    __tablename__ = "interactions_client"

    id_interaction = db.Column(db.Integer, primary_key=True)
    id_client = db.Column(db.Integer, db.ForeignKey("clients.id_client", ondelete="SET NULL", onupdate="CASCADE"), nullable=False)
    date_interaction = db.Column(db.Date, nullable=False)
    detail_interaction = db.Column(db.Text)
    id_etat_relation = db.Column(db.Integer, db.ForeignKey("etats_relations.id_etat_relation", ondelete="SET NULL", onupdate="CASCADE"), nullable=False)

    client = db.relationship("Client", back_populates="interactions")
    etat_relation = db.relationship("EtatRelation", back_populates="interactions")

class Convention(db.Model):
    __tablename__ = "conventions"

    id_convention = db.Column(db.Integer, primary_key=True)
    id_client = db.Column(db.Integer, db.ForeignKey("clients.id_client"), nullable=False)
    type_convention = db.Column(db.String(2), nullable=False)
    date_debut_convention = db.Column(db.Date, nullable=False)
    date_fin_convention = db.Column(db.Date)
    regles = db.Column(db.Text)
    cahier_charges = db.Column(db.Text)
    prix = db.Column(db.Numeric(10, 2))

    client = db.relationship("Client", back_populates="conventions")
    projets = db.relationship("Projet", back_populates="convention")

    __table_args__ = (
        CheckConstraint("type_convention IN ('CE','CC')", name="convention_type_check"),
    )

class Projet(db.Model):
    __tablename__ = "projets"

    id_projet = db.Column(db.Integer, primary_key=True)
    nom_projet = db.Column(db.String(200), nullable = False)
    statut_projet = db.Column(SAEnum(StatutProjet, name="statut_projet_enum"), nullable=False, server_default=sa.text("'Pas commencé'"))
    date_debut_projet = db.Column(db.Date)
    date_fin_projet = db.Column(db.Date)
    id_convention = db.Column(db.Integer, db.ForeignKey("conventions.id_convention"), nullable=False)

    convention = db.relationship("Convention", back_populates="projets")
    jalons = db.relationship("Jalon", back_populates="projet")
    intervenants = db.relationship("Intervenant", secondary=intervenant_projet, back_populates="projets")

    def __repr__(self):
        return f"Projet {self.nom_projet}"
    

class Jalon(db.Model):
    __tablename__ = "jalons"

    id_jalon = db.Column(db.Integer, primary_key=True)
    id_projet = db.Column(db.Integer, db.ForeignKey("projets.id_projet", ondelete="SET NULL", onupdate="CASCADE"), nullable=False)
    nom_jalon = db.Column(db.String(200), nullable=False)
    statut_jalon = db.Column(SAEnum(StatutJalon, name="statut_jalon_enum"), nullable=False, server_default=sa.text("'À venir'"))
    date_debut_jalon = db.Column(db.Date)
    date_fin_jalon = db.Column(db.Date)

    projet = db.relationship("Projet", back_populates="jalons")
    taches = db.relationship("Tache", back_populates="jalon")

class Tache(db.Model):
    __tablename__ = "taches"

    id_tache = db.Column(db.Integer, primary_key=True)
    id_jalon = db.Column(db.Integer, db.ForeignKey("jalons.id_jalon", ondelete="SET NULL", onupdate="CASCADE"), nullable=False)
    nom_tache = db.Column(db.String(200), nullable=False)
    description_tache = db.Column(db.Text)
    statut_tache = db.Column(SAEnum(StatutTache, name="statut_tache_enum"), nullable=False, server_default=sa.text("'Pas commencé'"))
    date_dernier_delai_tache = db.Column(db.Date)
    id_intervenant_tache = db.Column(db.Integer, db.ForeignKey("intervenants.id_intervenant", ondelete="SET NULL", onupdate="CASCADE"))

    jalon = db.relationship("Jalon", back_populates="taches")
    intervenants = db.relationship("Intervenant", back_populates="taches", secondary=intervenant_tache,)

    def __repr__(self):
        return f"<Tache {self.nom_tache}>"