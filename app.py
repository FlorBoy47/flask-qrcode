from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from models import db, Geraet, Notiz, AdminNotiz, Fehlerbericht
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datenbank.db'
app.secret_key = 'dein_geheimer_schluessel'
db.init_app(app)

# Dummy-Login-Daten
users = {
    "admin": "adminpass",
    "acaris": "acarispass"
}

# Login-Seite
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and users[username] == password:
            session['user'] = username
            flash("Erfolgreich eingeloggt!", "success")
            return redirect(url_for('index'))
        else:
            flash("Login fehlgeschlagen!", "error")

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Erfolgreich ausgeloggt!", "info")
    return redirect(url_for('login'))

# Startseite: Geräteübersicht
@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    geraete = Geraet.query.all()
    return render_template('index.html', geraete=geraete, user=session['user'])

# Gerätedetails anzeigen
@app.route('/geraet/<int:geraet_id>')
def geraet_details(geraet_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    geraet = Geraet.query.get_or_404(geraet_id)
    notizen = Notiz.query.filter_by(geraet_id=geraet.id).all()
    admin_notiz = AdminNotiz.query.filter_by(geraet_id=geraet.id).first()
    fehlerberichte = Fehlerbericht.query.filter_by(geraet_id=geraet.id).order_by(Fehlerbericht.erstellt_am.desc()).all()
    return render_template('geraet_details.html', geraet=geraet, notizen=notizen, admin_notiz=admin_notiz, fehlerberichte=fehlerberichte, user=session['user'])

# Fehler melden (Acaris)
@app.route('/fehler-melden/<int:geraet_id>', methods=['GET', 'POST'])
def fehler_melden(geraet_id):
    if 'user' not in session or session['user'] != 'acaris':
        return redirect(url_for('login'))

    geraet = Geraet.query.get_or_404(geraet_id)
    if request.method == 'POST':
        beschreibung = request.form.get('beschreibung')
        if not beschreibung:
            flash("Bitte eine Beschreibung eingeben.", "error")
            return redirect(request.url)

        neuer_fehler = Fehlerbericht(
            geraet_id=geraet.id,
            user="Acaris",
            beschreibung=beschreibung
        )
        db.session.add(neuer_fehler)
        db.session.commit()
        flash("Fehler wurde gemeldet.", "success")
        return redirect(url_for('geraet_details', geraet_id=geraet.id))

    return render_template('fehler_melden.html', geraet=geraet)

# Admin: Fehlerübersicht + Fehler erledigen
@app.route('/admin/fehler', methods=['GET', 'POST'])
def admin_fehler():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))

    fehlerliste = Fehlerbericht.query.order_by(Fehlerbericht.erstellt_am.desc()).all()
    if request.method == 'POST':
        fehler_id = request.form.get('fehler_id')
        kommentar = request.form.get('kommentar')
        fehler = Fehlerbericht.query.get_or_404(fehler_id)
        fehler.erledigt = True
        fehler.kommentar_admin = kommentar
        fehler.erledigt_am = datetime.utcnow()
        db.session.commit()
        flash("Fehler als erledigt markiert.", "success")
        return redirect(url_for('admin_fehler'))

    return render_template('admin_fehler.html', fehlerliste=fehlerliste)

# Geräte erstellen (optional)
@app.route('/geraet-erstellen', methods=['GET', 'POST'])
def geraet_erstellen():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name')
        beschreibung = request.form.get('beschreibung')
        if name:
            neues_geraet = Geraet(name=name, beschreibung=beschreibung)
            db.session.add(neues_geraet)
            db.session.commit()
            return redirect(url_for('index'))

    return render_template('geraet_erstellen.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)