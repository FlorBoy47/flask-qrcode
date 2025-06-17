from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Geraet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    beschreibung = db.Column(db.Text, nullable=True)

class Notiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), nullable=False)
    geraet_id = db.Column(db.Integer, db.ForeignKey('geraet.id'), nullable=False)

    # Felder für Acaris
    kunde = db.Column(db.String(100), nullable=True)
    probleme = db.Column(db.Boolean, default=False)
    problembeschreibung = db.Column(db.Text, nullable=True)
    info_user = db.Column(db.Text, nullable=True)

    # Felder für Admin
    geliefert_am = db.Column(db.String(100), nullable=True)
    info_problem_admin = db.Column(db.Text, nullable=True)
    info_admin = db.Column(db.Text, nullable=True)

    # Neue Felder zur Problemlösung
    problem_behoben = db.Column(db.Boolean, default=False)
    kommentar_behoben = db.Column(db.Text, nullable=True)
