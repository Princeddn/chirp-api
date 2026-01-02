# LoRaWAN Analytics Platform

Une plateforme web moderne pour visualiser, décoder et analyser les données de vos capteurs LoRaWAN via ChirpStack.

## 🚀 Fonctionnalités

*   **Tableau de Bord Live** : Visualisation en temps réel de l'activité du réseau et des capteurs.
*   **Widgets Intelligents** : Détection et affichage automatique des métriques clés (Température, Humidité, CO2, Batterie, etc.) pour chaque capteur.
*   **Décodage Universel** : Intègre un décodeur unifié capable de gérer nativement de nombreux fabricants (Milesight, Dragino, Nexelec, Watteco, NKE, etc.) et de s'adapter automatiquement.
*   **Analytique** : Graphiques interactifs pour explorer l'historique des données.
*   **Configuration Facile** : Interface de paramétrage intégrée (pas besoin de toucher au code).
*   **Gestion de Flotte** : Suivi de l'état (Online/Offline) et du niveau de batterie des équipements.
*   **Console Live** : Flux de logs en temps réel et outil d'envoi de commandes Downlink.

## 🛠️ Installation

1.  **Prérequis** :
    *   Python 3.8 ou supérieur.
    *   Un accès à une instance ChirpStack.

2.  **Installation des dépendances** :
    ```bash
    pip install -r requirements.txt
    ```

3.  **Lancement de l'application** :
    ```bash
    python app.py
    ```
    L'application sera accessible à l'adresse : `http://localhost:3000`

## ⚙️ Configuration (Nouveau !)

Plus besoin de modifier les fichiers de code pour connecter votre instance ChirpStack.

1.  Ouvrez l'application dans votre navigateur.
2.  Allez dans le menu **Paramètres** (dans la barre latérale).
3.  Remplissez les champs :
    *   **URL API ChirpStack** : L'adresse de votre serveur (ex: `https://chirpstack.mon-domaine.com`).
    *   **Token API** : Votre clé d'API (générée dans ChirpStack).
    *   **Repo GitHub** (Optionnel) : Pour la sauvegarde automatique des données.
4.  Cliquez sur **Enregistrer**.

Les paramètres sont sauvegardés localement dans un fichier `config.json`.

## 📂 Structure du Projet

*   `app.py` : Serveur Backend Flask.
*   `Decoder.py` : Moteur de décodage unifié (Python).
*   `index.html` : Interface utilisateur (SPA).
*   `assets/js/dashboard.js` : Logique Frontend et gestion des widgets.
*   `database.json` : Stockage local des trames reçues.
*   `config.json` : Fichier de configuration généré par l'interface.

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour ajouter un nouveau décodeur :
1.  Ajoutez votre classe de décodage dans `Decoder.py`.
2.  Dans `Decoder.py`, ajoutez votre classe à la liste `globals.COMPATIBILITY`.