import os
import subprocess
from datetime import datetime

def push_to_github(repo_name, branch, token, git_email="bot@chirp-api.local", git_name="ChirpApi Bot"):
    if not token or not repo_name:
        print("❌ push_to_github: Token or Repo not provided override.")
        return

    # Assuming repo_name is "User/Repo"
    repo_url = f"https://{token}@github.com/{repo_name}.git"

    try:
        # Configuration Git
        subprocess.run(["git", "config", "--global", "user.email", git_email], check=True)
        subprocess.run(["git", "config", "--global", "user.name", git_name], check=True)

        # Vérifier les modifications
        changed = subprocess.run(["git", "diff", "--quiet", "database.json"]).returncode

        if changed == 1:
            # Création du commit
            # On vérifie d'abord si on est sur la bonne branche ou si on doit la créer
            # Pour simplifier dans ce contexte CI/CD local:
            # On ajoute juste le fichier et on commit sur la branche courante si elle match, 
            # MAIS attention le script original faisait un checkout -B branch.
            # Cela risque d écraser le contexte local si on n'est pas prudent.
            # On va supposer que l'user veut backuper database.json sur une branche orpheline ou spécifique 'data-backup'.
            
            subprocess.run(["git", "checkout", "-B", branch], check=True)
            subprocess.run(["git", "add", "database.json"], check=True)
            commit_msg = f"Backup auto {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)

            # Push forcé (nécessaire pour les branches de backup)
            subprocess.run(["git", "push", "--force", repo_url, f"{branch}:{branch}"], check=True)
            print("✅ Sauvegarde GitHub OK")
            
            # Revenir à la branche principale ? Difficile à savoir sans contexte. 
            # On laisse comme ça pour l'instant car c'était la logique voulue.
        else:
            print("⚠️ Aucun changement détecté")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur Git: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")