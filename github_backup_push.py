# github_backup_push.py
import os, base64, requests

def push_to_github(db_file="database.json"):
    owner  = os.getenv("GH_OWNER", "Princeddn")
    repo   = os.getenv("GH_REPO",  "chirp-api")
    branch = os.getenv("GH_BRANCH","data-backup")
    path   = os.getenv("GH_PATH",  "database.json")
    token  = os.getenv("GH_TOKEN")  # PAT finement scoped: contents:write

    if not token:
        raise RuntimeError("GH_TOKEN manquant (env).")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    # Récupérer le SHA courant (si le fichier existe)
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    r = requests.get(url, headers=headers, params={"ref": branch})
    sha = r.json().get("sha") if r.status_code == 200 else None

    content_b64 = base64.b64encode(open(db_file, "rb").read()).decode()
    payload = {
        "message": "backup: update database.json",
        "content": content_b64,
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha

    r = requests.put(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["content"]["sha"]
