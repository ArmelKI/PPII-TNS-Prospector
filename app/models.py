import enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum as SAEnum, CheckConstraint
from flask_login import UserMixin, current_user
from app.config import login_manager
from bcrypt import hashpw, gensalt, checkpw
from app.permissions import can_manage_users, can_manage_clients, can_manage_intervenants, can_manage_projets, all_perms

db = SQLAlchemy()

class StatutProjet(enum.Enum):
    # on choisit cet ordre pour faciliter l'affichage (dans cet ordre) des projets triés par statut
    # cf le fonctionnement des ENUM avec les index
    EN_COURS = "En cours"
    PAS_COMMENCE = "Pas commencé"
    BLOQUE = "Bloqué"
    STAND_BY = "Stand-By"
    TERMINE = "Terminé"

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

# Tables de correspondance
intervenant_projet = db.Table(
    "intervenant_projet",
    db.Column("id_intervenant", db.Integer, db.ForeignKey("intervenants.id_intervenant", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    db.Column("id_projet", db.Integer, db.ForeignKey("projets.id_projet", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    db.Column("date_debut_intervention", db.Date),
    db.Column("date_fin_intervention", db.Date)
)

intervenant_tache = db.Table(
    "intervenant_tache",
    db.Column("id_intervenant", db.Integer, db.ForeignKey("intervenants.id_intervenant", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    db.Column("id_tache", db.Integer, db.ForeignKey("taches.id_tache", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
)

projet_competence = db.Table(
    "projet_competence",
    db.Column("id_projet", db.Integer, db.ForeignKey("projets.id_projet", ondelete="CASCADE"), primary_key=True),
    db.Column("id_competence", db.Integer, db.ForeignKey("competences.id_competence", ondelete="CASCADE"), primary_key=True)
)


# Modèles ORM
class MaitriseCompetence(db.Model):
    """
    Association Object pattern for Intervenant <-> Competence.
    Allows storing the 'level' (niveau_maitrise) of a specific skill for a user.
    """
    __tablename__ = "intervenant_competence"

    id_intervenant = db.Column(db.Integer, db.ForeignKey("intervenants.id_intervenant", ondelete="CASCADE"), primary_key=True)
    id_competence = db.Column(db.Integer, db.ForeignKey("competences.id_competence", ondelete="CASCADE"), primary_key=True)
    niveau_maitrise = db.Column(db.Integer, default=0)

    # Relationships to the parent objects
    intervenant = db.relationship("Intervenant", back_populates="maitrise_details")
    competence = db.relationship("Competence", back_populates="intervenant_details")

    # Constraint: Skill level must be between 0 and 10
    __table_args__ = (
        db.CheckConstraint("niveau_maitrise >= 0 AND niveau_maitrise <= 10", name="check_niveau_maitrise"),
    )

class Role(db.Model):
    """
    Defines user roles (e.g., Admin, Project Manager, Contributor).
    """
    __tablename__ = "roles"
    id_role = db.Column(db.Integer, primary_key=True)
    nom_role = db.Column(db.String(100), nullable=False)

    utilisateurs = db.relationship("Utilisateur", back_populates="role")

class Utilisateur(db.Model, UserMixin):
    """
    Core User model handling authentication and identity.
    """
    __tablename__ = "utilisateurs"

    id_utilisateur = db.Column(db.Integer, primary_key=True)
    prenom_utilisateur = db.Column(db.String(100), nullable=False)
    nom_utilisateur = db.Column(db.String(100), nullable=False)
    mail_utilisateur = db.Column(db.String(150), nullable=False, unique=True)
    mdp_utilisateur = db.Column(db.String(255), nullable=False)
    permission = db.Column(db.Integer, nullable=False)
    id_role = db.Column(db.Integer, db.ForeignKey("roles.id_role"), nullable=False)

    role = db.relationship("Role", back_populates="utilisateurs")
    # One-to-One relationship with Intervenant profile
    intervenant = db.relationship("Intervenant", uselist=False, back_populates="utilisateur", cascade="all, delete-orphan")

    def __repr__(self):
        return f"User {self.nom_utilisateur} {self.prenom_utilisateur}"

    def check_password(self, pw_candidate: str) -> bool:
        """Verifies the password against the stored bcrypt hash."""
        if not self.mdp_utilisateur: return False
        stored_hash = self.mdp_utilisateur
        if isinstance(stored_hash, str): stored_hash = stored_hash.encode('utf-8')
        candidate_bytes = pw_candidate.encode('utf-8')
        try:
            return checkpw(candidate_bytes, stored_hash)
        except ValueError:
            return False

    def set_password(self, new_password: str):
        """Hashes the password using bcrypt before storage."""
        pw_bytes = new_password.encode('utf-8')
        hashed = hashpw(pw_bytes, gensalt())
        self.mdp_utilisateur = hashed.decode('utf-8')

    def get_id(self):
        return self.id_utilisateur

    def can_manage_users(self) -> bool:
        return can_manage_users(self)

    def can_manage_clients(self) -> bool:
        return can_manage_clients(self)

    def can_manage_projets(self) -> bool:
        return can_manage_projets(self)

    def can_manage_intervenants(self) -> bool:
        return can_manage_intervenants(self)

    def is_admin(self) -> bool:
        return self.permission == all_perms

class Intervenant(db.Model):
    """
    Extended profile for a user who works on projects (The 'Resource').
    """
    __tablename__ = "intervenants"

    id_intervenant = db.Column(db.Integer, db.ForeignKey("utilisateurs.id_utilisateur", ondelete="CASCADE"), primary_key=True)
    disponible = db.Column(db.Boolean, nullable=False, server_default='TRUE')
    nb_heures_dispo = db.Column(db.Integer)

    # Documents paths
    bulletin_adhesion = db.Column(db.String(255))
    carte_etudiante = db.Column(db.String(255))
    carte_vitale = db.Column(db.String(255))
    piece_identite = db.Column(db.String(255))
    photo_identite = db.Column(db.String(255))
    cv = db.Column(db.String(255))

    utilisateur = db.relationship("Utilisateur", back_populates="intervenant")

    # Skills relationship via association object
    maitrise_details = db.relationship("MaitriseCompetence", back_populates="intervenant", cascade="all, delete-orphan")

    # Projects and Tasks
    projets = db.relationship("Projet", secondary=intervenant_projet, back_populates="intervenants")
    taches = db.relationship("Tache", secondary=intervenant_tache, back_populates="intervenants")

    def __repr__(self):
        nom = self.utilisateur.nom_utilisateur if self.utilisateur else str(self.id_intervenant)
        return f"Intervenant {nom}"

class Competence(db.Model):
    """
    Represents a generic Skill (e.g., Python, Marketing).
    """
    __tablename__ = "competences"

    id_competence = db.Column(db.Integer, primary_key=True)
    nom_competence = db.Column(db.String(150), nullable=False)

    intervenant_details = db.relationship("MaitriseCompetence", back_populates="competence", cascade="all, delete-orphan")
    projets_requerant = db.relationship("Projet", secondary=projet_competence, back_populates="competences_requises")

class EtatRelation(db.Model):
    """
    Defines the state of a client relationship (e.g., Prospect, Active Client).
    """
    __tablename__ = "etats_relations"

    id_etat_relation = db.Column(db.Integer, primary_key=True)
    libelle_relation = db.Column(db.String(150), nullable=False)

    interactions = db.relationship("InteractionClient", back_populates="etat_relation")

class Client(db.Model):
    """
    Represents a client company.
    """
    __tablename__ = "clients"

    id_client = db.Column(db.Integer, primary_key=True)
    raison_sociale = db.Column(db.String(200), nullable=False)
    mail_client = db.Column(db.String(150))
    telephone_client = db.Column(db.String(30))
    secteur = db.Column(db.String(100))
    date_dernier_contact = db.Column(db.Date)
    latitude = db.Column(db.Numeric(10, 7))
    longitude = db.Column(db.Numeric(10, 7))

    conventions = db.relationship("Convention", back_populates="client", cascade="all, delete-orphan")
    interactions = db.relationship("InteractionClient", back_populates="client", cascade="all, delete-orphan")

    def __init__(self, id_client, raison_sociale, mail_client, telephone_client, secteur, date_dernier_contact, latitude, longitude):
        self.id_client = id_client
        self.raison_sociale = raison_sociale
        self.mail_client = mail_client
        self.telephone_client = telephone_client
        self.secteur = secteur
        self.date_dernier_contact = date_dernier_contact
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return f"Client {self.raison_sociale}"

class InteractionClient(db.Model):
    """
    Logs an event/interaction with a client (Phone call, Meeting, etc.).
    """
    __tablename__ = "interactions_client"

    id_interaction = db.Column(db.Integer, primary_key=True)
    id_client = db.Column(db.Integer, db.ForeignKey("clients.id_client", ondelete="SET NULL", onupdate="CASCADE"), nullable=False)
    date_interaction = db.Column(db.Date, nullable=False)
    detail_interaction = db.Column(db.Text)
    id_etat_relation = db.Column(db.Integer, db.ForeignKey("etats_relations.id_etat_relation", ondelete="SET NULL", onupdate="CASCADE"), nullable=False)

    client = db.relationship("Client", back_populates="interactions")
    etat_relation = db.relationship("EtatRelation", back_populates="interactions")

class Convention(db.Model):
    """
    Represents a legal contract/convention binding a client and a project.
    """
    __tablename__ = "conventions"

    id_convention = db.Column(db.Integer, primary_key=True)
    id_client = db.Column(db.Integer, db.ForeignKey("clients.id_client"), nullable=False)
    type_convention = db.Column(db.String(2), nullable=False) # 'CC' (Framework) or 'CE' (Study)
    date_debut_convention = db.Column(db.Date, nullable=False)
    date_fin_convention = db.Column(db.Date)
    regles = db.Column(db.Text)
    cahier_charges = db.Column(db.Text)
    prix = db.Column(db.Numeric(10, 2))

    # File paths
    convention_file = db.Column("convention", db.String(255))
    bon_commande = db.Column(db.String(255))
    recap_mission = db.Column(db.String(255))

    client = db.relationship("Client", back_populates="conventions")
    projets = db.relationship("Projet", back_populates="convention")

    __table_args__ = (CheckConstraint("type_convention IN ('CE','CC')", name="convention_type_check"),)

class Projet(db.Model):
    """
    Represents a Project. The core entity of the application.
    """
    __tablename__ = "projets"

    id_projet = db.Column(db.Integer, primary_key=True)
    nom_projet = db.Column(db.String(200), nullable=False)
    statut_projet = db.Column(SAEnum(StatutProjet, name="statut_projet_enum"), nullable=False, default=StatutProjet.PAS_COMMENCE)
    charge_projet = db.Column(db.Integer, default=0) # Estimated workload
    date_debut_projet = db.Column(db.Date)
    date_fin_projet = db.Column(db.Date)

    id_convention = db.Column(db.Integer, db.ForeignKey("conventions.id_convention"), nullable=False)

    # file paths
    convention_file = db.Column("convention", db.String(255))
    bon_commande = db.Column(db.String(255))
    recap_mission = db.Column(db.String(255))

    convention = db.relationship("Convention", back_populates="projets")
    jalons = db.relationship("Jalon", back_populates="projet", cascade="all, delete-orphan")
    intervenants = db.relationship("Intervenant", secondary=intervenant_projet, back_populates="projets")
    competences_requises = db.relationship("Competence", secondary=projet_competence, back_populates="projets_requerant")

    def __repr__(self):
        return f"Project {self.nom_projet}"

class Jalon(db.Model):
    """
    Represents a Milestone (Phase) within a project.
    Contains multiple tasks.
    """
    __tablename__ = "jalons"

    id_jalon = db.Column(db.Integer, primary_key=True)
    id_projet = db.Column(db.Integer, db.ForeignKey("projets.id_projet", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    nom_jalon = db.Column(db.String(200), nullable=False)
    statut_jalon = db.Column(SAEnum(StatutJalon, name="statut_jalon_enum"), nullable=False, default=StatutJalon.A_VENIR)
    date_debut_jalon = db.Column(db.Date)
    date_fin_jalon = db.Column(db.Date)

    projet = db.relationship("Projet", back_populates="jalons")

    # Important: 'cascade="all, delete-orphan"' ensures that when a Milestone is deleted,
    # all its associated tasks are automatically deleted as well.
    taches = db.relationship("Tache", back_populates="jalon", cascade="all, delete-orphan")

class Tache(db.Model):
    """
    Represents a Task. The smallest unit of work in the Kanban board.
    """
    __tablename__ = "taches"

    id_tache = db.Column(db.Integer, primary_key=True)

    # Foreign Key with CASCADE delete
    id_jalon = db.Column(db.Integer, db.ForeignKey("jalons.id_jalon", ondelete="CASCADE"), nullable=False)

    nom_tache = db.Column(db.String(200), nullable=False)
    description_tache = db.Column(db.Text)
    statut_tache = db.Column(SAEnum(StatutTache, name="statut_tache_enum"), nullable=False, default=StatutTache.PAS_COMMENCE)
    date_dernier_delai_tache = db.Column(db.Date)
    id_intervenant_tache = db.Column(db.Integer, db.ForeignKey("intervenants.id_intervenant", ondelete="SET NULL", onupdate="CASCADE"))

    # Relationship back to Jalon (Essential for SQLAlchemy to understand the link)
    jalon = db.relationship("Jalon", back_populates="taches")

    intervenants = db.relationship("Intervenant", back_populates="taches", secondary=intervenant_tache)

    def __repr__(self):
        return f"<Task {self.nom_tache}>"

@login_manager.user_loader
def load_user(user_id) -> Utilisateur:
    return Utilisateur.query.get(user_id)
