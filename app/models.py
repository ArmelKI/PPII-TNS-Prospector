from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Intervenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    competences = db.Column(db.String(255), nullable=False)
    disponibilite = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Intervenant {self.nom}>"
