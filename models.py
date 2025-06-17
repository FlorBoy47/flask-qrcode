from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Geraet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    beschreibung = db.Column(db.Text)

    notizen = db.relationship('Notiz', backref='geraet', lazy=True)
    admin_notizen = db.relationship('AdminNotiz', backref='geraet', lazy=True)
    fehlerberichte = db.relationship('Fehlerbericht', backref='geraet', lazy=True)


class Notiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100))
    geraet_id = db.Column(db.Integer, db.ForeignKey('geraet.id'), nullable=False)
    kunde = db.Column(db.String(100))
    probleme = db.Column(db.Boolean, default=False)
    problembeschreibung = db.Column(db.Text)
    info_user = db.Column(db.Text)


class AdminNotiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    geraet_id = db.Column(db.Integer, db.ForeignKey('geraet.id'), nullable=False)
    geliefert_am = db.Column(db.Date)
    info_admin = db.Column(db.Text)
    info_problem_admin = db.Column(db.Text)


class Fehlerbericht(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    geraet_id = db.Column(db.Integer, db.ForeignKey('geraet.id'), nullable=False)
    user = db.Column(db.String(100))
    beschreibung = db.Column(db.Text, nullable=False)
    erledigt = db.Column(db.Boolean, default=False)
    kommentar_admin = db.Column(db.Text)
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)
    erledigt_am = db.Column(db.DateTime, nullable=True)
