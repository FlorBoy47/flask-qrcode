from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'geheimer_schlüssel'

# Benutzerliste
users = {
    'Acaris': 'Acaris1',
    'Admin': 'Admin1'
}

# Teileinformationen
teileinfos = {
    '123': 'Teil 123: Motorabdeckung mit Spezifikationen.',
    '456': 'Teil 456: Sensorhalterung für Außenbereich.'
}

# Notizen pro Benutzer und Teil
notizen = {
    # Beispiel: ('Acaris', '123'): 'Meine gespeicherte Notiz'
}

# Login-Schutz
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        pwd = request.form['password']
        if name in users and users[name] == pwd:
            session['username'] = name
            return redirect(url_for('teilinfo', teil_id='123'))  # Standard-Teil anzeigen
        return 'Falsche Zugangsdaten!'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/teil/<teil_id>', methods=['GET', 'POST'])
@login_required
def teilinfo(teil_id):
    user = session.get('username', 'Unbekannt')
    key = (user, teil_id)

    # Wenn Formular abgeschickt wird
    if request.method == 'POST':
        text = request.form.get('notiz')
        notizen[key] = text

    # Gespeicherte Notiz anzeigen
    gespeicherte_notiz = notizen.get(key, "")
    info = teileinfos.get(teil_id, "Teil nicht gefunden.")
    return render_template('teil.html', teil_id=teil_id, info=info, user=user, notiz=gespeicherte_notiz)

if __name__ == '__main__':
    app.run(debug=True)
