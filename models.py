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
    text = db.Column(db.Text, nullable=True)
