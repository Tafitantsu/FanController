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
    web_thread = threading.Thread(target=run_server, args=(sensor, fan, led), daemon=True)
    web_thread.start()
    print(f"Serveur web démarré. Accédez à http://localhost:5000 ou http://<IP_DU_PI>:5000")

    # 3. Boucle de contrôle principale
    print("Démarrage de la boucle de contrôle. Appuyez sur Ctrl+C pour quitter.")
    try:
        while True:
            # Lecture de la température
            current_temp = sensor.read()

            print(f"Température actuelle: {current_temp:.2f}°C (Seuil par défault: {TEMPERATURE_THRESHOLD}°C)")

            # Logique de contrôle
            if current_temp > TEMPERATURE_THRESHOLD:
                # Si la température dépasse le seuil, on allume le ventilateur et la LED
                fan.on()
                led.on()
            else:
                # Sinon, on les éteint
                fan.off()
                led.off()

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
