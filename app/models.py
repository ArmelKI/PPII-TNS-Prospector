from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Intervenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    competences = db.Column(db.String(255), nullable=False)
    disponibilite = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Intervenant {self.nom}>"

class Utilisatur(db.Model):
    id_utilisateur = db.Column(db.Integer, primary_key=True)
    prenom_utilisateur = db.Column(db.String(255), nullable=False)
    nom_utilisateur = db.Column(db.String(255), nullabe=False)
    mail_utilisateur = db.Column(db.String(255), nullabe=False, unique=True)
    mdp_utilisateur = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"Utilisateur {self.nom_utilisateur} {self.prenom_utilisateur}"
    