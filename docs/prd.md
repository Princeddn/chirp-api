# Product Requirements Document (PRD)

## 1. Objectifs & Contexte

### 1.1 Objectifs
L'objectif de **Chirp-API** est de fournir une solution "middleware" clé en main pour visualiser et interagir avec des capteurs LoRaWAN connectés à ChirpStack. Elle vise à supprimer la complexité du décodage de payload et à offrir une interface utilisateur immédiate.

### 1.2 Contexte
ChirpStack est un excellent Network Server, mais il n'est pas conçu pour l'utilisateur final. Les intégrations HTTP sont puissantes mais nécessitent un serveur pour recevoir les données. Chirp-API remplit ce rôle de serveur d'application léger.

---

## 2. Exigences Fonctionnelles (Functional Requirements)

### FR1 - Réception des Données (Webhook)
- **Description :** Le système doit exposer un endpoint HTTP POST pour recevoir les événements "Uplink" de ChirpStack.
- **Détails :** 
  - Endpoint : `/uplink`
  - Payload supporté : JSON (format ChirpStack v4).
  - Doit extraire : `devEUI`, `fPort`, `data` (Base64), `deviceInfo`.

### FR2 - Décodage Unifié (Unified Decoding)
- **Description :** Le système doit automatiquement décoder le payload brut en données lisibles sans configuration par appareil.
- **Détails :**
  - Utilisation de la classe `UnifiedDecoder`.
  - Identification automatique via `fPort` ou signature de payload.
  - Support natif des marques : Milesight, Adeunis, Nexelec, Watteco, Dragino.
  - Fallback : Si aucun décodeur n'est trouvé, stocker la donnée brute.

### FR3 - Stockage & Persistance
- **Description :** Les données reçues doivent être stockées localement.
- **Détails :**
  - Format : Fichier JSON (`database.json`).
  - Pas de dépendance à une base de données lourde (SQL, etc.).
  - Structure : Liste d'objets JSON avec timestamp, devEUI, et données décodées.

### FR4 - Visualisation (Dashboard)
- **Description :** Une interface web doit afficher l'état actuel de tous les capteurs.
- **Détails :**
  - Technologie : HTML simple + JavaScript (polling sur `database.json`).
  - Vues : Liste des cartes (Widgets).
  - Indicateurs : Batterie, Signal (RSSI/SNR), Dernière communication.

### FR5 - Contrôle (Downlink)
- **Description :** L'interface doit permettre d'envoyer des commandes aux capteurs.
- **Détails :**
  - Endpoint API interne : `/api/downlink`.
  - Communication vers ChirpStack : API REST (`POST /api/devices/{dev_eui}/queue`).
  - Doit gérer l'authentification via Token ChirpStack.

### FR6 - Sauvegarde Distante (Backup)
- **Description :** Les données doivent être sauvegardées pour éviter la perte en cas de crash local.
- **Détails :**
  - Support de GitHub comme stockage distant.
  - Déclenchement manuel ou périodique via `/api/backup`.

---

## 3. Exigences Non-Fonctionnelles (NFR)

### NFR1 - Facilité d'Installation
- Le projet doit tourner avec un minimum de dépendances (`flask`, `requests`).
- Pas de compilation complexe nécessaire.

### NFR2 - Performance
- Le dashboard doit charger en moins de 1 seconde pour une flotte < 100 capteurs.
- Le fichier JSON doit rester gérable (rotation ou archivage possible futur).

### NFR3 - Extensibilité
- Ajouter un nouveau capteur doit se faire uniquement en ajoutant une classe Python dans `Decoder.py`, sans toucher au reste du code.

---

## 4. Hypothèses Techniques

- L'utilisateur a une instance ChirpStack fonctionnelle.
- Le serveur Chirp-API peut être joint par ChirpStack (même réseau ou IP publique).
- Python 3.8+ est installé sur la machine hôte.
