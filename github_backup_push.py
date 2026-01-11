import os
import subprocess
from datetime import datetime

def push_to_github(repo_name, branch, token, git_email="bot@chirp-api.local", git_name="ChirpApi Bot"):
    if not token or not repo_name:
        raise ValueError("Token or Repo not provided")

    # Assuming repo_name is "User/Repo"
    # repo_url = f"https://{token}@github.com/{repo_name}.git"
    # Mask token in print, but use in command
    # safe_url = f"https://github.com/{repo_name}.git"
    
    # We pass the token via header or URL. URL is easiest but risky in logs?
    # Better: Configure git credential helper store? No, too complex.
    # Use URL with token but DO NOT PRINT IT.
    
    auth_repo_url = f"https://oauth2:{token}@github.com/{repo_name}.git"

    try:
        # Helper to run git
        def run_git(args):
            # Avoid printing secret URL in logs if exception occurs
            cmd_str = " ".join(args)
            # print(f"DEBUG: Running {cmd_str}") 
            res = subprocess.run(args, capture_output=True, text=True)
            if res.returncode != 0:
                # Mask token in error message
                err_msg = res.stderr.replace(token, "***")
                raise Exception(f"Git command failed: {' '.join(args[:2])}... Error: {err_msg}")
            return res.stdout

        # Configuration Git (Local instead of global to avoid permission issues)
        run_git(["git", "config", "user.email", git_email])
        run_git(["git", "config", "user.name", git_name])

        # Vérifier les modifications
        # git diff return 1 if changed, 0 if not.
        diff_res = subprocess.run(["git", "diff", "--quiet", "database.json"])
        changed = (diff_res.returncode == 1)

        if changed:
            # Création du commit
            run_git(["git", "checkout", "-B", branch])
            run_git(["git", "add", "database.json"])
            commit_msg = f"Backup auto {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            run_git(["git", "commit", "-m", commit_msg])

            # Push forcé
            run_git(["git", "push", "--force", auth_repo_url, f"{branch}:{branch}"])
            print("✅ Sauvegarde GitHub OK")
            return "Backup Successful"
        else:
            print("⚠️ Aucun changement détecté")
            return "No changes detected"
            
    except Exception as e:
        print(f"❌ Erreur Git: {e}")
        # Re-raise to be caught by app.py
        raise e