from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Geraet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    beschreibung = db.Column(db.Text, nullable=True)

class Notiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    geraet_id = db.Column(db.Integer, db.ForeignKey('geraet.id'), nullable=False)
    kunde = db.Column(db.String(100))  # Dieses Feld fehlte!
    sonstige_infos = db.Column(db.Text)


class AdminNotiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    geraet_id = db.Column(db.Integer, db.ForeignKey('geraet.id'), nullable=False)
    inhalt = db.Column(db.Text, nullable=True)
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)

class Fehlerbericht(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    geraet_id = db.Column(db.Integer, db.ForeignKey('geraet.id'), nullable=False)
    user = db.Column(db.String(50), nullable=False)
    beschreibung = db.Column(db.Text, nullable=False)
    kommentar_admin = db.Column(db.Text, nullable=True)
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)
    erledigt_am = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default="Offen")  # "Offen", "In Bearbeitung", "Erledigt"
    erledigt = db.Column(db.Boolean, default=False)

    geraet = db.relationship('Geraet', backref='fehlerberichte')
