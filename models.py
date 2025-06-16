from flask_sqlalchemy import SQLAlchemy

# Initialisierung der Datenbank



db = SQLAlchemy()

class Geraet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    beschreibung = db.Column(db.Text)

class Notiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), nullable=False)
    geraet_id = db.Column(db.Integer, db.ForeignKey('geraet.id'), nullable=False)
    kunde = db.Column(db.String(100))
    probleme = db.Column(db.Boolean, default=False)
    problembeschreibung = db.Column(db.Text)
    info_user = db.Column(db.Text)

    # NEU: Felder für Problembehebung durch Admin
    problem_behoben = db.Column(db.Boolean, default=False)
    kommentar_admin = db.Column(db.Text)

class AdminNotiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    geraet_id = db.Column(db.Integer, db.ForeignKey('geraet.id'), nullable=False)
    geliefert_am = db.Column(db.String(50))
    info_admin = db.Column(db.Text)
    info_problem_admin = db.Column(db.Text)
