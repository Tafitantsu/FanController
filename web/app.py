from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
import threading
import os

# Crée une instance de l'application Flask
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.urandom(24)
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Variable globale pour stocker les objets hardware
# Ils seront passés depuis le script principal (simul.py)
system_hardware = {
    'sensor': None,
    'fan': None,
    'led': None
}

# Variable globale pour le seuil configurable
global TEMPERATURE_THRESHOLD
from config import TEMPERATURE_THRESHOLD as DEFAULT_THRESHOLD
TEMPERATURE_THRESHOLD = DEFAULT_THRESHOLD

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token)
        return jsonify({"msg": "Bad username or password"}), 401
    return render_template('login.html')

@app.route('/')
@jwt_required(optional=True)
def index():
    current_identity = get_jwt_identity()
    if not current_identity:
        return redirect(url_for('login'))
    return render_template('index.html')

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

def background_data_thread():
    import time
    while True:
        temp = system_hardware['sensor'].read()
        fan_status = system_hardware['fan'].get_status()
        socketio.emit('data', {
            'temperature': temp,
            'fan_status': fan_status,
            'threshold': TEMPERATURE_THRESHOLD
        })
        time.sleep(2)

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

def run_server(sensor, fan, led, shared_threshold):
    system_hardware['sensor'] = sensor
    system_hardware['fan'] = fan
    system_hardware['led'] = led

    @socketio.on('set_threshold')
    @jwt_required()
    def handle_set_threshold(data):
        try:
            new_threshold = float(data.get('threshold'))
            shared_threshold.set(new_threshold)
            emit('threshold_updated', {'threshold': new_threshold})
        except Exception as e:
            emit('error', {'message': str(e)})

    def background_data_thread():
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

    threading.Thread(target=background_data_thread, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
