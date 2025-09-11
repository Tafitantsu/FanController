import time
import threading
import sys
import subprocess
import os

# Ajoute le répertoire du projet au chemin de recherche pour les imports
sys.path.append('.')

from hardware.sensor import TempSensor
from hardware.fan import Fan
from hardware.led import Led
from web.app import run_server
from config import TEMPERATURE_THRESHOLD, READ_INTERVAL

# Durée d'hystérésis en secondes (ex: 5s)
HYSTERESIS_DURATION = 5

class SharedThreshold:
    def __init__(self, value):
        self.value = value
        self.lock = threading.Lock()
    def get(self):
        with self.lock:
            return self.value
    def set(self, new_value):
        with self.lock:
            self.value = new_value

shared_threshold = SharedThreshold(TEMPERATURE_THRESHOLD)

def launch_gunicorn():
    """
    Lance le serveur web via gunicorn en mode production avec SSL.
    """
    cert_path = os.path.join('certs', 'cert.pem')
    key_path = os.path.join('certs', 'key.pem')
    cmd = [
        'gunicorn',
        '--worker-class', 'eventlet',
        '--certfile', cert_path,
        '--keyfile', key_path,
        '-w', '4',
        '-b', '0.0.0.0:443',
        'web.app:app'
    ]
    print(f"Lancement du serveur web en production: {' '.join(cmd)}")
    subprocess.Popen(cmd)

def main():
    """
    Fonction principale du système de contrôle.
    """
    # 1. Initialisation des composants hardware
    print("Initialisation du système de contrôle de température...")
    sensor = TempSensor()
    fan = Fan()
    led = Led()

    # Lancement du serveur web en production via gunicorn avec SSL
    print("Mode production forcé. Lancement via gunicorn avec SSL.")
    web_thread = threading.Thread(target=launch_gunicorn, daemon=True)
    web_thread.start()

    # 3. Boucle de contrôle principale
    print("Démarrage de la boucle de contrôle. Appuyez sur Ctrl+C pour quitter.")
    try:
        # Variables pour l'hystérésis
        over_threshold_since = None
        under_threshold_since = None

        while True:
            # Lecture de la température
            current_temp = sensor.read()
            threshold = shared_threshold.get()  # Utilise le seuil partagé

            print(f"Température actuelle: {current_temp:.2f}°C (Seuil actuel: {threshold}°C)")

            # Hystérésis : activation/désactivation avec temporisation
            if current_temp > threshold:
                if over_threshold_since is None:
                    over_threshold_since = time.time()
                if time.time() - over_threshold_since >= HYSTERESIS_DURATION:
                    fan.on()
                    led.on()
            else:
                over_threshold_since = None
                if under_threshold_since is None:
                    under_threshold_since = time.time()
                if time.time() - under_threshold_since >= HYSTERESIS_DURATION:
                    fan.off()
                    led.off()
            if current_temp > threshold:
                under_threshold_since = None

            # Attente avant la prochaine lecture
            time.sleep(READ_INTERVAL)

    except KeyboardInterrupt:
        print("\nArrêt du programme demandé par l'utilisateur.")

    finally:
        # 4. Nettoyage des ressources
        print("Nettoyage des ressources...")
        fan.cleanup()
        led.cleanup()
        print("Programme terminé.")

if __name__ == "__main__":
    main()
