import time
import threading
import sys

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

def main():
    """
    Fonction principale du système de contrôle.
    """
    # 1. Initialisation des composants hardware
    print("Initialisation du système de contrôle de température...")
    sensor = TempSensor()
    fan = Fan()
    led = Led()

    # 2. Démarrage du serveur web dans un thread séparé
    print("Démarrage du serveur web...")
    web_thread = threading.Thread(target=run_server, args=(sensor, fan, led, shared_threshold), daemon=True)
    web_thread.start()
    print(f"Serveur web démarré. Accédez à http://localhost:5000 ou http://<IP_DU_PI>:5000")

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
