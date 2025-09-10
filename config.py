# Fichier de configuration pour le projet Smart Home

# Seuil de température en degrés Celsius
TEMPERATURE_THRESHOLD = 25.0

# Intervalle de lecture du capteur en secondes
READ_INTERVAL = 2

# Configuration des broches GPIO pour le Raspberry Pi
FAN_PIN = 17  # Broche GPIO pour le ventilateur
LED_PIN = 27  # Broche GPIO pour la LED
# Pour le capteur DS18B20, l'identifiant est nécessaire.
# Laissez vide si vous utilisez la simulation.
# Remplacer par l'ID réel du capteur, ex: '28-00000xxxxxxxx'
SENSOR_ID = ''
