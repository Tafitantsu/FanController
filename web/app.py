from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_jwt_extended import (
    JWTManager, create_access_token, get_jwt_identity,
    jwt_required, set_access_cookies, unset_jwt_cookies
)
import threading
import os
import json
from cryptography.fernet import Fernet
import hashlib

# ---------------------------
# Flask & JWT setup
# ---------------------------
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# JWT key persistante
JWT_KEY_FILE = "jwt.key"
if os.path.exists(JWT_KEY_FILE):
    with open(JWT_KEY_FILE, "rb") as f:
        app.config["JWT_SECRET_KEY"] = f.read()
else:
    key = os.urandom(24)
    with open(JWT_KEY_FILE, "wb") as f:
        f.write(key)
    app.config["JWT_SECRET_KEY"] = key

app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # Pour simplifier, sinon gérer CSRF
jwt = JWTManager(app)

# ---------------------------
# Configuration hardware
# ---------------------------
system_hardware = {'sensor': None, 'fan': None, 'led': None}

global TEMPERATURE_THRESHOLD
from config import TEMPERATURE_THRESHOLD as DEFAULT_THRESHOLD
TEMPERATURE_THRESHOLD = DEFAULT_THRESHOLD

# ---------------------------
# Gestion mots de passe chiffrés
# ---------------------------
PASSWORD_FILE = "passwords.json.enc"
FERNET_KEY_FILE = "fernet.key"

def get_fernet():
    if not os.path.exists(FERNET_KEY_FILE):
        key = Fernet.generate_key()
        with open(FERNET_KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(FERNET_KEY_FILE, "rb") as f:
            key = f.read()
    return Fernet(key)

def load_passwords():
    if not os.path.exists(PASSWORD_FILE):
        # Default: admin/admin, first_login True
        return {"admin": {"hash": hashlib.sha256("admin".encode()).hexdigest(), "first_login": True}}
    fernet = get_fernet()
    with open(PASSWORD_FILE, "rb") as f:
        encrypted = f.read()
    decrypted = fernet.decrypt(encrypted)
    return json.loads(decrypted.decode())

def save_passwords(passwords):
    fernet = get_fernet()
    data = json.dumps(passwords).encode()
    encrypted = fernet.encrypt(data)
    with open(PASSWORD_FILE, "wb") as f:
        f.write(encrypted)

USER_PASSWORDS = load_passwords()

# ---------------------------
# Routes Flask
# ---------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = USER_PASSWORDS.get(username)
        if user and user['hash'] == hashlib.sha256(password.encode()).hexdigest():
            access_token = create_access_token(identity=username)
            first_login = user.get('first_login', False)
            resp = jsonify(first_login=first_login)
            set_access_cookies(resp, access_token)
            return resp
        return jsonify({"msg": "Bad username or password"}), 401
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    resp = jsonify({"msg": "Logged out"})
    unset_jwt_cookies(resp)
    return resp

@app.route('/')
def root():
    return redirect(url_for('home'))

@app.route('/home')
@jwt_required()
def home():
    current_identity = get_jwt_identity()
    return render_template('index.html', user=current_identity)

@app.route('/status')
@jwt_required()
def status():
    if not all(system_hardware.values()):
        return jsonify({"error": "Hardware not initialized"}), 500

    current_temp = system_hardware['sensor'].read()
    fan_status = system_hardware['fan'].get_status()
    led_status = system_hardware['led'].get_status()

    return jsonify({
        'temperature': current_temp,
        'fan_status': fan_status,
        'led_status': led_status
    })

@app.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    username = get_jwt_identity()
    new_password = request.form.get('new_password')
    if username in USER_PASSWORDS and new_password:
        USER_PASSWORDS[username]['hash'] = hashlib.sha256(new_password.encode()).hexdigest()
        USER_PASSWORDS[username]['first_login'] = False
        save_passwords(USER_PASSWORDS)
        access_token = create_access_token(identity=username)
        resp = jsonify({"msg": "Password changed"})
        set_access_cookies(resp, access_token)
        return resp
    return jsonify({"msg": "Erreur lors du changement de mot de passe."}), 400

# ---------------------------
# SocketIO events
# ---------------------------
@socketio.on('set_threshold')
@jwt_required()
def handle_set_threshold(data):
    global TEMPERATURE_THRESHOLD
    try:
        new_threshold = float(data.get('threshold'))
        TEMPERATURE_THRESHOLD = new_threshold
        emit('threshold_updated', {'threshold': TEMPERATURE_THRESHOLD})
    except Exception as e:
        emit('error', {'message': str(e)})

def background_data_thread():
    import time
    while True:
        if system_hardware['sensor'] is None:
            time.sleep(1)
            continue
        temp = system_hardware['sensor'].read()
        fan_status = system_hardware['fan'].get_status()
        led_status = system_hardware['led'].get_status()
        socketio.emit('data', {
            'temperature': temp,
            'fan_status': fan_status,
            'led_status': led_status,
            'threshold': TEMPERATURE_THRESHOLD
        })
        time.sleep(2)

# ---------------------------
# Run server
# ---------------------------
def run_server(sensor, fan, led, shared_threshold):
    system_hardware['sensor'] = sensor
    system_hardware['fan'] = fan
    system_hardware['led'] = led

    def background_thread():
        import time
        while True:
            temp = sensor.read()
            fan_status = fan.get_status()
            led_status = led.get_status() if hasattr(led, 'get_status') else None
            socketio.emit('data', {
                'temperature': temp,
                'fan_status': fan_status,
                'led_status': led_status,
                'threshold': shared_threshold.get()
            })
            time.sleep(2)

    threading.Thread(target=background_thread, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
