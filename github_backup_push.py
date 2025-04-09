import os
import subprocess
from datetime import datetime

def push_to_github():
    token = os.getenv("GITHUB_PAT")
    user = os.getenv("GIT_USER")
    email = os.getenv("GIT_EMAIL")
    repo_url = f"https://{token}@github.com/{user}/chirp-api.git"

    try:
        subprocess.run(["git", "config", "--global", "user.email", email], check=True)
        subprocess.run(["git", "config", "--global", "user.name", user], check=True)
        subprocess.run(["git", "checkout", "-B", "data-backup"], check=True)
        subprocess.run(["git", "add", "database.json"], check=True)
        subprocess.run(["git", "commit", "-m", f"Backup auto {datetime.now()}"], check=True)
        subprocess.run(["git", "push", repo_url, "data-backup", "--force"], check=True)
        print("✅ Sauvegarde GitHub OK")
    except subprocess.CalledProcessError as e:
        print("❌ Échec GitHub:", e)