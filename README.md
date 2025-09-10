Le projet complet de contrôle de température a été généré avec succès. Voici la structure finale des fichiers :

project/
├── config.py
├── hardware/
│   ├── __init__.py
│   ├── fan.py
│   ├── led.py
│   └── sensor.py
├── requirements.txt
├── simul.py
└── web/
    ├── app.py
    └── templates/
        └── index.html

Voici les étapes pour utiliser le projet :
1. Installation des dépendances

Ouvrez un terminal, naviguez dans le dossier project et installez les bibliothèques Python nécessaires :

cd project
pip install -r requirements.txt

Sur Raspberry Pi : Assurez-vous que le démon pigpiod est activé si vous utilisez la bibliothèque pigpio, ou que les permissions sont correctes pour lgpio. Pour lgpio, généralement aucune configuration de démon n'est requise, mais vous pourriez avoir besoin de droits d'accès (sudo).
2. Configuration

Avant de lancer, modifiez le fichier config.py si nécessaire :

    TEMPERATURE_THRESHOLD : Ajustez le seuil de température (par défaut 25.0).
    FAN_PIN, LED_PIN : Vérifiez que les numéros de broches GPIO correspondent à votre câblage sur le Raspberry Pi.
    SENSOR_ID: Si vous utilisez un capteur DS18B20, remplacez la chaîne vide par l'identifiant unique de votre capteur (ex: '28-00000xxxxxxxx'). Si vous laissez ce champ vide, le script essaiera de trouver le premier capteur disponible.

3. Lancement de l'application

Pour démarrer le système, exécutez le script simul.py depuis le dossier project :

python3 simul.py

Le script détectera automatiquement s'il s'exécute sur un Raspberry Pi ou sur un autre ordinateur (PC/VM) et passera en mode réel ou en mode simulation.
4. Accès à l'interface web

Une fois le script lancé, ouvrez un navigateur web et accédez à l'une des adresses suivantes :

    Sur le même ordinateur : http://localhost:5000
    Depuis un autre appareil sur le même réseau : http://<VOTRE_ADRESSE_IP_LOCALE>:5000 (remplacez <VOTRE_ADRESSE_IP_LOCALE> par l'adresse IP de la machine qui exécute le script).

Vous verrez un tableau de bord affichant la température et l'état du ventilateur et de la LED, mis à jour automatiquement toutes les deux secondes.
5. Arrêt du programme

Pour arrêter l'application, retournez dans le terminal où le script s'exécute et appuyez sur Ctrl+C. Le programme nettoiera les ressources GPIO avant de se fermer.
6. Administration

Connectez-vous avec le compte `admin`, puis accédez à la page d’administration :  
http://localhost:5000/admin

Vous pouvez :
- Voir la liste des utilisateurs
- Réinitialiser le mot de passe d’un utilisateur (le mot de passe sera demandé au prochain login)
- Revenir au tableau de bord principal
