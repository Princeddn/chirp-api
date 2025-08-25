import os
import subprocess
from datetime import datetime

def push_to_github():
    token = os.getenv("GITHUB_PAT")
    user = os.getenv("GIT_USER")
    email = os.getenv("GIT_EMAIL")
    branch = os.getenv("GIT_BRANCH", "beta")  # Par défaut sur beta

    if not token or not user or not email:
        print("❌ GITHUB_PAT, GIT_USER ou GIT_EMAIL non défini dans les variables d'environnement.")
        return

    repo_url = f"https://{token}@github.com/{user}/chirp-api.git"

    try:
        # Configuration Git
        subprocess.run(["git", "config", "--global", "user.email", email], check=True)
        subprocess.run(["git", "config", "--global", "user.name", user], check=True)

        # Vérifier les modifications
        changed = subprocess.run(["git", "diff", "--quiet", "database.json"]).returncode

        if changed == 1:
            # Création du commit
            subprocess.run(["git", "checkout", "-B", branch], check=True)
            subprocess.run(["git", "add", "database.json"], check=True)
            commit_msg = f"Backup auto {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)

            # Push forcé (nécessaire pour les branches de backup)
            subprocess.run(["git", "push", "--force", repo_url, f"{branch}:{branch}"], check=True)
            print("✅ Sauvegarde GitHub OK")
        else:
            print("⚠️ Aucun changement détecté")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur Git: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")