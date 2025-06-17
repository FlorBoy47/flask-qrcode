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
    alle_notizen = Notiz.query.all()
    notizen_dict = {n.geraet_id: n for n in alle_notizen if n.user == 'Acaris'}
    return render_template('geraete.html', geraete=geraete, user=session['username'], notizen=notizen_dict)

@app.route('/geraet/<int:geraet_id>', methods=['GET', 'POST'])
@login_required
def geraet_detail(geraet_id):
    user = session['username']
    geraet = Geraet.query.get_or_404(geraet_id)
    notiz = Notiz.query.filter_by(user=user, geraet_id=geraet.id).first()

    if request.method == 'POST':
        if user == "Acaris":
            kunde = request.form.get('kunde')
            probleme = bool(request.form.get('probleme'))
            problembeschreibung = request.form.get('problembeschreibung')
            info_user = request.form.get('info_user')

            if notiz:
                notiz.kunde = kunde
                notiz.probleme = probleme
                notiz.problembeschreibung = problembeschreibung
                notiz.info_user = info_user
                notiz.problem_behoben = False  # Zurücksetzen, wenn Acaris was meldet
                notiz.loesung_kommentar = ""
            else:
                notiz = Notiz(
                    user=user,
                    geraet_id=geraet.id,
                    kunde=kunde,
                    probleme=probleme,
                    problembeschreibung=problembeschreibung,
                    info_user=info_user
                )
                db.session.add(notiz)
            db.session.commit()
            return redirect(url_for('geraet_detail', geraet_id=geraet.id))

        elif user == "Admin":
            notiz = Notiz.query.filter_by(user='Acaris', geraet_id=geraet.id).first()
            if notiz:
                notiz.problem_behoben = 'problem_behoben' in request.form
                notiz.loesung_kommentar = request.form.get("loesung_kommentar", "")
                db.session.commit()
            return redirect(url_for('geraet_detail', geraet_id=geraet.id))

    return render_template('geraet_detail.html', geraet=geraet, notiz=notiz, user=user)

@app.route('/geraet/neu', methods=['GET', 'POST'])
@admin_required
def geraet_erstellen():
    if request.method == 'POST':
        name = request.form['name']
        neues_geraet = Geraet(name=name)
        db.session.add(neues_geraet)
        db.session.commit()
        return redirect(url_for('geraete_liste'))
    return render_template('geraet_erstellen.html')

@app.route('/geraet/<int:geraet_id>/loeschen', methods=['POST'])
@admin_required
def geraet_loeschen(geraet_id):
    geraet = Geraet.query.get_or_404(geraet_id)
    Notiz.query.filter_by(geraet_id=geraet.id).delete()
    db.session.delete(geraet)
    db.session.commit()
    return redirect(url_for('geraete_liste'))

# DB einmalig initialisieren
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
