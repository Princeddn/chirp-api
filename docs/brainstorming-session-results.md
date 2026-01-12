# Brainstorming Session Results

## 1. Contexte du Projet

Le projet **Chirp-API** est né du constat que la gestion des données LoRaWAN via ChirpStack, bien que puissante, manque souvent d'une couche de visualisation simple et "clé en main" pour les utilisateurs finaux.

Les techniciens et administrateurs réseaux LoRaWAN se retrouvent souvent avec :
- Des payloads encodés en hexadécimal difficiles à lire.
- La nécessité de créer un décodeur JavaScript spécifique pour chaque type de capteur dans ChirpStack.
- L'absence d'historisation simple sans monter une stack complexe (InfluxDB/Grafana).

## 2. Problématique (The "Why")

> *"Pourquoi est-ce si compliqué de juste VOIR la température de mon capteur ?"*

**Les points de douleur identifiés :**
- **Complexité des Décodeurs :** Chaque fabricant (Milesight, Nexelec, Adeunis...) a son propre format. Intégrer ça dans ChirpStack demande du copier-coller incessant.
- **Manque de Visibilité :** ChirpStack est un Network Server, pas un Application Server. Il manque un tableau de bord intuitif.
- **Perte de Données :** Sans base de données externe, les logs de ChirpStack sont éphémères.

## 3. Solution Proposée : Chirp-API

Une plateforme légère et autonome qui fait le pont entre ChirpStack et l'humain.

**Les 3 Piliers de la Solution :**

### A. Le Décodeur Unifié (Unified Decoder)
Au lieu de gérer 50 scripts JS dans ChirpStack, on envoie tout le payload brut vers Chirp-API.
C'est le moteur Python (`Decoder.py`) qui :
1. Identifie le fabricant (via le port ou la signature du payload).
2. Applique le bon driver (Milesight, Adeunis, etc.).
3. Retourne un objet JSON standardisé `{ temperature: 21.5, battery: 98 }`.

### B. Le Dashboard "Live"
Une interface web simple (`index.html` + `dashboard.js`) qui :
- Affiche les capteurs sous forme de cartes.
- Met à jour les données en temps réel (polling).
- Permet d'envoyer des commandes (Downlink) pour configurer les capteurs à distance.

### C. Simplicité & Autonomie
- **Zero-Config DB :** Utilisation d'un fichier JSON local (`database.json`) pour éviter d'installer SQL/Mongo.
- **Backup Auto :** Synchronisation automatique des données vers un repo GitHub privé pour la sécurité.
- **Installation Facile :** Un simple `pip install` et `python app.py`.

## 4. Personas Cibles

- **L'Installateur IoT :** Il pose des capteurs et veut vérifier *tout de suite* sur son téléphone si la donnée remonte, sans se logger sur 3 consoles différentes.
- **Le Gestionnaire de Bâtiment :** Il veut juste voir si la température est OK et si une alarme est levée, sans se soucier de l'hexadécimal.

## 5. Idées Futures (Parking Lot)

- Alertes SMS/Email sur seuil critique.
- Export CSV des données historiques.
- Support pour MQTT en plus des webhooks HTTP.
