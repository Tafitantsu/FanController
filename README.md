# Système de contrôle de température pour maison intelligente

## Structure du projet

```
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
        ├── index.html
        ├── login.html
        └── admin.html
```

## Fonctionnalités principales

- Lecture et contrôle de la température via capteur DS18B20 (simulation possible sur PC).
- Contrôle du ventilateur et d'une LED selon le seuil configuré.
- Interface web sécurisée : visualisation température, état ventilateur/LED, modification du seuil.
- Authentification par mot de passe (stocké chiffré).
- Administration : gestion des utilisateurs, réinitialisation des mots de passe.

## Installation

1. **Installer les dépendances**

```bash
cd project
pip install -r requirements.txt
```

> **Sur Raspberry Pi** :  
> Vérifiez le démon pigpiod ou les droits pour lgpio selon votre configuration.

2. **Configurer le système**

Modifiez `config.py` selon votre matériel :
- `TEMPERATURE_THRESHOLD` : seuil de température (défaut : 25.0)
- `FAN_PIN`, `LED_PIN` : broches GPIO
- `SENSOR_ID` : identifiant du capteur DS18B20 (optionnel)

3. **Lancer l’application**

```bash
python3 simul.py
```

Le mode simulation ou réel est détecté automatiquement.

4. **Accéder à l’interface web**

- Sur la machine locale : [http://localhost:5000](http://localhost:5000)
- Depuis le réseau : [http://<VOTRE_ADRESSE_IP_LOCALE>:5000](http://<VOTRE_ADRESSE_IP_LOCALE>:5000)

Tableau de bord : température, état ventilateur/LED, seuil configurable.

5. **Arrêter le programme**

Dans le terminal, faites `Ctrl+C`. Les ressources GPIO sont nettoyées.

## Administration

- Connectez-vous avec le compte `admin`.
- Accédez à : [http://localhost:5000/admin](http://localhost:5000/admin)
- Fonctions :
  - Voir la liste des utilisateurs
  - Réinitialiser le mot de passe d’un utilisateur (mot de passe temporaire, modification obligatoire au prochain login)
  - Retour au tableau de bord

## Sécurité

- Les mots de passe sont stockés chiffrés (AES/Fernet).
- Authentification JWT en cookie sécurisé.
- Seuil configurable uniquement après authentification.

---

**Pour toute question ou amélioration, consultez le code source ou contactez l’auteur du projet.**
