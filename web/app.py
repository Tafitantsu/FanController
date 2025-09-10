from flask import Flask, render_template, jsonify

# Crée une instance de l'application Flask
app = Flask(__name__)

# Variable globale pour stocker les objets hardware
# Ils seront passés depuis le script principal (simul.py)
system_hardware = {
    'sensor': None,
    'fan': None,
    'led': None
}

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

def run_server(sensor, fan, led):
    """
    Fonction pour démarrer le serveur Flask.
    Elle est appelée depuis le script principal (simul.py).
    """
    # Met à jour les objets hardware globaux
    system_hardware['sensor'] = sensor
    system_hardware['fan'] = fan
    system_hardware['led'] = led

    # Lance le serveur Flask
    # host='0.0.0.0' pour le rendre accessible sur le réseau local
    # use_reloader=False est important quand on lance dans un thread
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
