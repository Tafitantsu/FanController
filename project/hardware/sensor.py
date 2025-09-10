import random
import time
from hardware import IS_RPI
from config import SENSOR_ID

if IS_RPI:
    try:
        from w1thermsensor import W1ThermSensor, Sensor
    except ImportError:
        print("La bibliothèque w1thermsensor n'est pas installée. Le capteur fonctionnera en mode simulation.")
        IS_RPI = False # Force la simulation si la lib est absente

class TempSensor:
    def __init__(self):
        self.sensor = None
        if IS_RPI and 'W1ThermSensor' in globals():
            try:
                if SENSOR_ID:
                    self.sensor = W1ThermSensor(sensor_id=SENSOR_ID)
                else:
                    # Tente de trouver le premier capteur disponible
                    self.sensor = W1ThermSensor()
                print(f"Capteur de température réel (DS18B20) initialisé (ID: {self.sensor.id}).")
            except Exception as e:
                print(f"Erreur d'initialisation du capteur DS18B20 : {e}")
                print("Basculement en mode simulation pour le capteur.")
                self.sensor = None
        else:
            print("Capteur de température initialisé en mode simulation.")

        # Pour la simulation
        self.simulated_temp = 22.0
        self.last_read_time = 0

    def read(self):
        """
        Lit la température depuis le capteur réel ou retourne une valeur simulée.
        """
        if self.sensor:
            try:
                temperature = self.sensor.get_temperature()
                return round(temperature, 2)
            except Exception as e:
                print(f"Erreur de lecture du capteur, passage en simulation: {e}")
                self.sensor = None # Désactive le capteur réel en cas d'échec
                return self._get_simulated_temp()
        else:
            return self._get_simulated_temp()

    def _get_simulated_temp(self):
        """
        Génère une température simulée qui varie légèrement.
        """
        # Fait varier la température pour rendre la simulation plus réaliste
        current_time = time.time()
        if current_time - self.last_read_time > 1:
            self.simulated_temp += random.uniform(-0.2, 0.2)
            if self.simulated_temp < 18: self.simulated_temp = 18.0
            if self.simulated_temp > 28: self.simulated_temp = 28.0
            self.last_read_time = current_time

        return round(self.simulated_temp, 2)
