import os
import platform

def is_raspberry_pi():
    """
    Détecte si le code s'exécute sur un Raspberry Pi.
    """
    # Méthode simple : vérifier l'existence d'un fichier spécifique au RPi
    if os.path.exists('/sys/firmware/devicetree/base/model'):
        with open('/sys/firmware/devicetree/base/model', 'r') as f:
            if 'raspberry pi' in f.read().lower():
                return True

    # Méthode alternative : vérifier le nom de la machine
    if 'raspberrypi' in platform.uname().node.lower():
        return True

    return False

# Variable globale pour indiquer le mode de fonctionnement
IS_RPI = is_raspberry_pi()

# Affiche le mode détecté au démarrage du module
if IS_RPI:
    print("Environnement Raspberry Pi détecté. Utilisation des GPIOs réels.")
else:
    print("Environnement de simulation détecté (PC/VM).")
