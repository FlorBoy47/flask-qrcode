from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
from models import db, Geraet, Notiz
import os

app = Flask(__name__)
app.secret_key = 'geheimer_schlüssel'

# DB-Konfiguration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datenbank.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Benutzerliste
users = {
    'Admin': 'Admin1',
    'Acaris': 'Acaris1'
}

# Login-Schutz
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Nur Admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') != 'Admin':
            return "Zugriff verweigert", 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return redirect(url_for('geraete_liste'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        pwd = request.form['password']
        if name in users and users[name] == pwd:
            session['username'] = name
            return redirect(url_for('geraete_liste'))
        return 'Falsche Zugangsdaten!'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/geraete')
@login_required
def geraete_liste():
    geraete = Geraet.query.all()

    # Alle Notizen holen und in ein Dictionary packen (geraet_id → Notiz)
    alle_notizen = Notiz.query.all()
    notizen_dict = {n.geraet_id: n for n in alle_notizen}

    return render_template('geraete.html', geraete=geraete, user=session['username'], notizen=notizen_dict)

@app.route('/geraet/<int:geraet_id>', methods=['GET', 'POST'])
@login_required
def geraet_detail(geraet_id):
    user = session['username']
    geraet = Geraet.query.get_or_404(geraet_id)

    notiz = Notiz.query.filter_by(user=user, geraet_id=geraet.id).first()
    if request.method == 'POST':
        text = request.form.get('notiz')
        if notiz:
            notiz.text = text
        else:
            notiz = Notiz(user=user, geraet_id=geraet.id, text=text)
            db.session.add(notiz)
        db.session.commit()
        return redirect(url_for('geraet_detail', geraet_id=geraet.id))

    gespeicherte_notiz = notiz.text if notiz else ""
    return render_template('geraet_detail.html', geraet=geraet, notiz=gespeicherte_notiz, user=user)

@app.route('/geraet/neu', methods=['GET', 'POST'])
@admin_required
def geraet_erstellen():
    if request.method == 'POST':
        name = request.form['name']
        beschreibung = request.form['beschreibung']
        neues_geraet = Geraet(name=name, beschreibung=beschreibung)
        db.session.add(neues_geraet)
        db.session.commit()
        return redirect(url_for('geraete_liste'))
    return render_template('geraet_erstellen.html')

# Datenbank erstellen beim ersten Start
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
