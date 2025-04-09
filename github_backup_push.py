import os
import subprocess
from datetime import datetime

def push_to_github():
    token = os.environ.get("GITHUB_PAT")
    user = os.environ.get("GITHUB_USER")
    repo = os.environ.get("GITHUB_REPO")  # ex: Princeddn/chirp-api
    backup_file = "database.json"

    if not all([token, user, repo]):
        print("⚠️ GITHUB_PAT, GITHUB_USER ou GITHUB_REPO non défini.")
        return

    # Lien complet vers le dépôt avec le token pour authentification
    repo_url = f"https://{user}:{token}@github.com/{repo}.git"

    try:
        # Vérifie si "origin" est bien ajouté
        remote_check = subprocess.run(["git", "remote"], capture_output=True, text=True)
        if "origin" not in remote_check.stdout:
            subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
            print("✅ Remote 'origin' ajouté.")

        # Création d'une branche de backup si elle n'existe pas
        subprocess.run(["git", "fetch", "origin", "data-backup"], check=False)
        subprocess.run(["git", "checkout", "-B", "data-backup"], check=True)

        subprocess.run(["git", "add", backup_file], check=True)
        commit_message = f"🗃️ Backup du {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=False)  # Si rien n'a changé, pas d'erreur
        subprocess.run(["git", "push", "-u", "origin", "data-backup"], check=True)
        print("✅ Backup GitHub effectué.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Échec GitHub: {e}")
