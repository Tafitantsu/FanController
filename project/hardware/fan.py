from hardware import IS_RPI
from config import FAN_PIN

if IS_RPI:
    import lgpio

class Fan:
    def __init__(self):
        self.is_on = False
        if IS_RPI:
            try:
                self.h = lgpio.gpiochip_open(0)
                lgpio.gpio_claim_output(self.h, FAN_PIN)
                print(f"Ventilateur initialisé sur la broche GPIO {FAN_PIN}.")
            except Exception as e:
                print(f"Erreur d'initialisation GPIO pour le ventilateur : {e}")
                # En cas d'échec, on bascule en mode simulation
                self.h = None
                global IS_RPI
                IS_RPI = False
        else:
            print("Ventilateur initialisé en mode simulation.")

    def on(self):
        """Allume le ventilateur."""
        if not self.is_on:
            if IS_RPI and hasattr(self, 'h') and self.h is not None:
                lgpio.gpio_write(self.h, FAN_PIN, 1)

            print("ACTION: Ventilateur allumé.")
            self.is_on = True

    def off(self):
        """Éteint le ventilateur."""
        if self.is_on:
            if IS_RPI and hasattr(self, 'h') and self.h is not None:
                lgpio.gpio_write(self.h, FAN_PIN, 0)

            print("ACTION: Ventilateur éteint.")
            self.is_on = False

    def get_status(self):
        """Retourne l'état actuel du ventilateur."""
        return "ON" if self.is_on else "OFF"

    def cleanup(self):
        """Nettoie les ressources GPIO."""
        if IS_RPI and hasattr(self, 'h') and self.h is not None:
            self.off() # S'assurer que le ventilateur est éteint
            lgpio.gpiochip_close(self.h)
            print("Nettoyage des GPIOs du ventilateur terminé.")
