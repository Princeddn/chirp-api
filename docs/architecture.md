# Architecture Technique

## 1. Vue d'Ensemble

Chirp-API est une application monolithique légère construite avec **Flask** (Python). Elle combine les rôles de :
- Servceur Web (HTTP)
- Moteur de Traitement (ETL léger)
- Base de Données (Fichier plat)

### Diagramme HAUT-NIVEAU

```mermaid
graph LR
    Sensors[(Capteurs LoRa)] -->|LoRaWAN| Gateway
    Gateway -->|IP| ChirpStack[Serveur ChirpStack]
    ChirpStack -->|HTTP POST /uplink| App[App Flask (Chirp-API)]
    
    subgraph "Chirp-API Core"
        App -->|Raw Payload| Decoder[Moteur de Décodage]
        Decoder -->|Decoded JSON| App
        App -->|Write| DB[(database.json)]
        App -->|Read| Dashboard[Interface Web JS]
    end
    
    subgraph "External Services"
        App -->|Git Push| GitHub[Backup GitHub]
        App -->|HTTP POST| ChirpStackAPI[ChirpStack API (Downlink)]
    end
```

---

## 2. Composants Clés

### 2.1 Le Contrôleur (`app.py`)
Le point d'entrée de l'application. Il gère les routes HTTP et l'orchestration.
- **Responsabilités :**
  - Recevoir les webhooks (`/uplink`).
  - Servir les fichiers statiques (`index.html`, assets).
  - Exposer l'API pour le frontend (`/database.json`, `/api/downlink`).
  - Gérer la configuration (`config.json`).

### 2.2 Le Moteur de Décodage (`Decoder.py`)
Le cœur "intelligence" du système. C'est un module extensible conçu pour normaliser les données.
- **Design Pattern :** Stratégie / Factory.
- **Fonctionnement :**
  - Itère sur une liste de classes compatibles (`globals.COMPATIBILITY`).
  - Chaque classe (Driver) tente de parser le payload.
  - Si succès, retourne un dictionnaire standardisé.
- **Classes Principales :**
  - `BaseDecoder` : Classe parente avec utilitaires.
  - `UnifiedDecoder` : La classe qui orchestre les appels.
  - `Milesight_*`, `Adeunis_*`, `Nexelec_*` : Les drivers spécifiques.

### 2.3 La Base de Données (`database.json`)
Un système de stockage simple basé sur un fichier JSON.
- **Structure :** Liste de dictionnaires (Array of Objects).
- **Avantages :** Zéro installation, portable, lisible par humain.
- **Limites :** Performance sur très gros volumes (>100k entrées), pas de requêtes complexes (SQL).

### 2.4 Le Frontend (`index.html` + `dashboard.js`)
Une Single Page Application (SPA) ultra-légère.
- **Stack :** HTML5, CSS3, Vanilla JS.
- **Logique :** 
  - Récupère `database.json` toutes les X secondes.
  - Parse le JSON côté client pour générer les cartes.
  - Gère l'affichage dynamique des icônes selon le type de capteur (Température, Porte, Fuite, etc.).

---

## 3. Flux de Données (Data Flow)

### 3.1 Flux Uplink (Capteur -> Dashboard)
1. **Émission :** Le capteur envoie une trame LoRa.
2. **Réception :** ChirpStack reçoit la trame et fait un POST JSON vers `http://mon-serveur:3000/uplink`.
3. **Traitement :** `app.py` extrait `data` (Base64) et appelle `unified_decoder.decode_uplink()`.
4. **Décodage :** `Decoder.py` identifie le capteur et convertit l'hexadécimal en valeurs physiques.
5. **Stockage :** `app.py` ajoute l'entrée à la liste en mémoire et écrit dans `database.json`.
6. **Affichage :** Le navigateur de l'utilisateur fait un GET `/database.json` et met à jour l'interface.

### 3.2 Flux Downlink (Dashboard -> Capteur)
1. **Action :** L'utilisateur clique sur "Envoyer commande" dans le dashboard.
2. **API Interne :** Le JS envoie un POST `/api/downlink` avec `{devEui, data}`.
3. **Relais :** `app.py` authentifie la requête et la transmet à l'API ChirpStack.
4. **Mise en file :** ChirpStack met le message en file d'attente pour le prochain slot d'écoute du capteur.

---

## 4. Sécurité & Configuration

- **Authentification :** Le système est conçu pour tourner en réseau local sécurisé (LAN/VPN). Il n'y a pas de login utilisateur par défaut (Open Dashboard).
- **Secrets :** Les tokens API (ChirpStack, GitHub) sont stockés dans `config.json` ou variables d'environnement.
- **Backup :** Le script `github_backup_push.py` permet d'exfiltrer les données vers un repo GitHub privé pour prévenir la perte de données locale.
