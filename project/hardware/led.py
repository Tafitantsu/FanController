from hardware import IS_RPI
from config import LED_PIN

if IS_RPI:
    import lgpio

class Led:
    def __init__(self):
        self.is_on = False
        if IS_RPI:
            try:
                self.h = lgpio.gpiochip_open(0)
                lgpio.gpio_claim_output(self.h, LED_PIN)
                print(f"LED initialisée sur la broche GPIO {LED_PIN}.")
            except Exception as e:
                print(f"Erreur d'initialisation GPIO pour la LED : {e}")
                self.h = None
                global IS_RPI
                IS_RPI = False
        else:
            print("LED initialisée en mode simulation.")

    def on(self):
        """Allume la LED."""
        if not self.is_on:
            if IS_RPI and hasattr(self, 'h') and self.h is not None:
                lgpio.gpio_write(self.h, LED_PIN, 1)

            print("ACTION: LED allumée.")
            self.is_on = True

    def off(self):
        """Éteint la LED."""
        if self.is_on:
            if IS_RPI and hasattr(self, 'h') and self.h is not None:
                lgpio.gpio_write(self.h, LED_PIN, 0)

            print("ACTION: LED éteinte.")
            self.is_on = False

    def get_status(self):
        """Retourne l'état actuel de la LED."""
        return "ON" if self.is_on else "OFF"

    def cleanup(self):
        """Nettoie les ressources GPIO."""
        if IS_RPI and hasattr(self, 'h') and self.h is not None:
            self.off() # S'assurer que la LED est éteinte
            lgpio.gpiochip_close(self.h)
            print("Nettoyage des GPIOs de la LED terminé.")
