from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from models import db, Geraet, Notiz, AdminNotiz
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
    notizen = Notiz.query.all()
    problem_ids = [n.geraet_id for n in notizen if n.probleme]
    notizen_dict = {n.geraet_id: n for n in notizen}
    return render_template(
        'geraete.html',
        geraete=geraete,
        notizen=notizen_dict,
        user=session['username'],
        problem_ids=problem_ids
    )

@app.route('/geraet/<int:geraet_id>', methods=['GET', 'POST'])
@login_required
def geraet_detail(geraet_id):
    user = session['username']
    geraet = Geraet.query.get_or_404(geraet_id)
    admin_notiz = AdminNotiz.query.filter_by(geraet_id=geraet.id).first()

    if user == "Admin":
        benutzer_notizen = Notiz.query.filter_by(geraet_id=geraet.id).all()
        if request.method == "POST" and "admin_speichern" in request.form:
            if not admin_notiz:
                admin_notiz = AdminNotiz(geraet_id=geraet.id)
                db.session.add(admin_notiz)

            admin_notiz.geliefert_am = request.form.get("geliefert_am")
            admin_notiz.info_problem_admin = request.form.get("info_problem_admin")
            admin_notiz.info_admin = request.form.get("info_admin")
            db.session.commit()
            flash("Admin-Daten gespeichert", "success")
            return redirect(url_for('geraet_detail', geraet_id=geraet.id))

        return render_template('geraet_detail.html', geraet=geraet, user=user, admin_notiz=admin_notiz, benutzer_notizen=benutzer_notizen)

    else:
        notiz = Notiz.query.filter_by(user=user, geraet_id=geraet.id).first()
        if request.method == 'POST' and "user_speichern" in request.form:
            kunde = request.form.get('kunde')
            probleme = bool(request.form.get('probleme'))
            problembeschreibung = request.form.get('problembeschreibung')
            info_user = request.form.get('info_user')

            if notiz:
                notiz.kunde = kunde
                notiz.probleme = probleme
                notiz.problembeschreibung = problembeschreibung
                notiz.info_user = info_user
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

        return render_template('geraet_detail.html', geraet=geraet, user=user, notiz=notiz)

@app.route('/geraet/neu', methods=['GET', 'POST'])
@admin_required
def geraet_erstellen():
    if request.method == "POST":
        name = request.form['name']
        beschreibung = request.form['beschreibung']
        geraet = Geraet(name=name, beschreibung=beschreibung)
        db.session.add(geraet)
        db.session.commit()
        return redirect(url_for('geraete_liste'))
    return render_template('geraet_erstellen.html')

# Automatisches Setup (nur beim ersten Start sinnvoll)
with app.app_context():
    if not os.path.exists("datenbank.db"):
        db.create_all()
        print("✅ Neue Datenbank erstellt.")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
