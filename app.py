from flask import Flask, render_template, request, redirect, url_for, session, flash
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
    if 'username' in session:
        return redirect(url_for('geraete_liste'))
    return redirect(url_for('login'))

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
    notizen_dict = {n.geraet_id: n for n in alle_notizen}
    return render_template('geraete.html', geraete=geraete, user=session['username'], notizen=notizen_dict)

@app.route('/geraet/<int:geraet_id>', methods=['GET', 'POST'])
@login_required
def geraet_detail(geraet_id):
    user = session['username']
    geraet = Geraet.query.get_or_404(geraet_id)
    notiz = Notiz.query.filter_by(user='Acaris', geraet_id=geraet.id).first()

    if request.method == 'POST':
        if user == 'Acaris' and 'user_speichern' in request.form:
            if notiz:
                notiz.kunde = request.form.get('kunde')
                notiz.probleme = bool(request.form.get('probleme'))
                notiz.problembeschreibung = request.form.get('problembeschreibung')
                notiz.info_user = request.form.get('info_user')
            else:
                notiz = Notiz(
                    user='Acaris',
                    geraet_id=geraet.id,
                    kunde=request.form.get('kunde'),
                    probleme=bool(request.form.get('probleme')),
                    problembeschreibung=request.form.get('problembeschreibung'),
                    info_user=request.form.get('info_user')
                )
                db.session.add(notiz)
            db.session.commit()
            flash("Eintrag gespeichert", "success")
            return redirect(url_for('geraet_detail', geraet_id=geraet.id))

        if user == 'Admin' and 'admin_speichern' in request.form:
            if notiz:
                notiz.problem_behoben = bool(request.form.get('problem_behoben'))
                notiz.problem_geloest_info = request.form.get('problem_geloest_info')
                db.session.commit()
                flash("Problemstatus aktualisiert", "success")
            return redirect(url_for('geraet_detail', geraet_id=geraet.id))

    return render_template('geraet_detail.html', geraet=geraet, notiz=notiz, user=user)

@app.route('/geraet/neu', methods=['GET', 'POST'])
@admin_required
def geraet_erstellen():
    if request.method == 'POST':
        name = request.form.get('name')
        beschreibung = request.form.get('beschreibung')
        if name:
            neues_geraet = Geraet(name=name, beschreibung=beschreibung)
            db.session.add(neues_geraet)
            db.session.commit()
            return redirect(url_for('geraete_liste'))
    return render_template('geraet_erstellen.html')

@app.route('/geraet/<int:geraet_id>/loeschen', methods=['POST'])
@admin_required
def geraet_loeschen(geraet_id):
    geraet = Geraet.query.get_or_404(geraet_id)
    notizen = Notiz.query.filter_by(geraet_id=geraet.id).all()
    for n in notizen:
        db.session.delete(n)
    db.session.delete(geraet)
    db.session.commit()
    flash("Gerät gelöscht", "info")
    return redirect(url_for('geraete_liste'))

# Datenbank bei App-Start initialisieren
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
