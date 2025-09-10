from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading

# Crée une instance de l'application Flask
app = Flask(__name__)
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

@app.route('/')
def index():
    """
    Sert la page principale de l'interface web.
    """
    return render_template('index.html')

@app.route('/status')
def status():
    """
    Fournit l'état actuel du système au format JSON.
    C'est le point de terminaison (endpoint) que le JavaScript interroge.
    """
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

# Envoi périodique des données (température, état ventilateur, seuil)
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
def handle_set_threshold(data):
    global TEMPERATURE_THRESHOLD
    try:
        new_threshold = float(data.get('threshold'))
        TEMPERATURE_THRESHOLD = new_threshold
        emit('threshold_updated', {'threshold': TEMPERATURE_THRESHOLD})
    except Exception as e:
        emit('error', {'message': str(e)})

def run_server(sensor, fan, led, shared_threshold):
    # Met à jour les objets hardware globaux
    system_hardware['sensor'] = sensor
    system_hardware['fan'] = fan
    system_hardware['led'] = led

    @socketio.on('set_threshold')
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
            # Ajoutez l'état de la LED si besoin :
            led_status = led.get_status() if hasattr(led, 'get_status') else None
            socketio.emit('data', {
                'temperature': temp,
                'fan_status': fan_status,
                'led_status': led_status,
                'threshold': shared_threshold.get()
            })
            time.sleep(2)

    threading.Thread(target=background_data_thread, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000)
