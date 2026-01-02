import os
import subprocess
from datetime import datetime

def push_to_github(repo_name, branch, token):
    if not token or not repo_name:
        print("❌ push_to_github: Token or Repo not provided override.")
        # Fallback to envs if needed, or just return
        return

    # Assuming repo_name is "User/Repo"
    repo_url = f"https://{token}@github.com/{repo_name}.git"

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