from flask import Flask, request, jsonify, send_file, render_template
from datetime import datetime
import json, os, csv, uuid, time
from github_backup_push import push_to_github
import requests
from Decoder import BaseDecoder, NexelecDecoder, WattecoDecoder
from pytz import timezone  # Pour la gestion du fuseau horaire

app = Flask(__name__)
DB_FILE = "database.json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Princeddn/chirp-api/data-backup/database.json"
convertion = BaseDecoder()
decoder_nexelec = NexelecDecoder()
decoder_watteco = WattecoDecoder()


def restore_database_from_github(force=False):
    """
    Restaure la base locale depuis GitHub si elle est vide ou absente,
    ou si 'force=True' est spécifié.
    """
    if force or not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
        print("🔁 Restauration de database.json depuis GitHub...")
        try:
            r = requests.get(GITHUB_RAW_URL)
            r.raise_for_status()
            data = r.json()
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("✅ Base locale restaurée depuis GitHub.")
        except Exception as e:
            print(f"❌ Erreur restauration GitHub : {e}")
    else:
        print("🟢 database.json déjà présent, aucune restauration nécessaire.")

def ensure_valid_json_file():
    """Vérifie que database.json est un JSON UTF-8 valide, sinon restaure."""
    if not os.path.exists(DB_FILE):
        print("❗ database.json n'existe pas encore.")
        restore_database_from_github(force=True)
        return

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"❌ database.json invalide au démarrage : {e}")
        restore_database_from_github(force=True)
    except Exception as e:
        print(f"⚠️ Erreur inconnue lors de la vérification de database.json : {e}")


# 🔁 Restaurer et vérifier tout de suite
restore_database_from_github()
ensure_valid_json_file()


def load_data_local():
    """Lit localement database.json."""
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"❌ database.json corrompu : {e}")
        return []
    except Exception as e:
        print(f"⚠️ Erreur lecture locale : {e}")
        return []


def load_data_github():
    """Lit directement depuis GitHub pour l'affichage du dashboard."""
    try:
        print("📡 Lecture des données depuis GitHub RAW...")
        r = requests.get(GITHUB_RAW_URL)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("❌ Erreur lecture GitHub pour affichage :", e)
        return []

# 💾 Sauvegarde robuste avec restauration si nécessaire
def save_data(new_entries):
    current = load_data_local()

    # ✅ Si le fichier est corrompu ou mal formé, on restaure avant d'ajouter
    if not isinstance(current, list):
        print("⚠️ Base locale mal formée. Tentative de restauration.")
        restore_database_from_github(force=True)
        current = load_data_local()

    existing_ids = {d.get("id") for d in current}
    new_data = [d for d in new_entries if d.get("id") not in existing_ids]

    if new_data:
        current.extend(new_data)
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, ensure_ascii=False)
        print(f"✅ {len(new_data)} nouvelle(s) donnée(s) sauvegardée(s)")
        time.sleep(0.2)
        push_to_github()
    else:
        print("ℹ️ Pas de nouvelles données à sauvegarder")

        
def decode_lorawan_data(encoded_data):
    try:
        decoded_bytes = convertion.identify_and_process_data(encoded_data)
        decoded_hex = convertion.bytes_to_string(decoded_bytes)
        product_type = int(decoded_hex[:2], 16)

        if product_type in [0xA9, 0xAA, 0xAB, 0xFF, 0xAD]:
            return decoder_nexelec.periodic_data_output(decoded_hex)
        elif product_type in [0xA3, 0xA4, 0xA5, 0xA6, 0xA7]:
            return decoder_nexelec.periodic_data_output_air(decoded_hex)
        else:
            product_type_2octets = int(decoded_hex[:4], 16)
            if product_type_2octets in [0x110A, 0x310A]:
                return decoder_watteco.decode_watteco(decoded_hex)
            else:
                return {"error": f"Type inconnu : 0x{product_type_2octets:04X}"}
    except Exception as e:
        return {"error": str(e)}

@app.route('/uplink', methods=['GET', 'POST'])
def uplink():
    if request.method == 'POST':
        event = request.args.get("event", "up")
        if event == "push":
            push_to_github()
            return jsonify({"status": "✅ Sauvegarde GitHub déclenchée"}), 200

        if event != "up":
            return jsonify({"status": f"ignored event: {event}"}), 200
        data = request.json
        decoded = decode_lorawan_data(data.get("data", ""))
        paris_tz = timezone('Europe/Paris')
        data["timestamp"] = datetime.now(paris_tz).strftime('%Y-%m-%d %H:%M:%S %Z')        
        data["decoded"] = decoded
        data["id"] = str(uuid.uuid4())
        print("📡 Donnée reçue + décodée :", data)
        save_data([data])
        return jsonify({"status": "ok"}), 200
    
    
    # 🔁 Forcer la restauration depuis GitHub via URL
    if request.args.get("restore") == "1":
        restore_database_from_github(force=True)
        return jsonify({"status": "🔁 Base restaurée depuis GitHub"}), 200


    rows = load_data_github()
    fmt = request.args.get("format")



    if fmt == "json":
        return jsonify(rows)

    elif fmt == "csv":
        csv_file = "export.csv"
        with open(csv_file, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "Nom du capteur", "Product_type", "Fabricant", "data", "decoded"])
            for row in rows:
                decoded = row.get("decoded", {})
                product_type = decoded.get("Product_type", "Inconnu")
                device_name = row.get("deviceInfo", {}).get("deviceName", "Inconnu")
                writer.writerow([
                    row.get("timestamp"),
                    device_name,
                    product_type,
                    decoded.get("Fabricant", "N/A"),
                    row.get("data"),
                    json.dumps(decoded, ensure_ascii=False)
                ])

        return send_file(csv_file, as_attachment=True)

    capteurs = sorted({r.get("deviceInfo", {}).get("deviceName", "Inconnu") for r in rows if "deviceInfo" in r})

    # On récupère toutes les grandeurs présentes dans les données décodées
    grandeurs = set()
    for r in rows:
        decoded = r.get("decoded", {})
        if isinstance(decoded, dict):
            grandeurs.update(decoded.keys())

    return render_template("Pageweb.html", rows=rows, capteurs=capteurs, grandeurs=sorted(grandeurs))


@app.route('/trame/<id>')
def detail_trame(id):
    rows = load_data_github()
    entry = next((r for r in rows if r.get("id") == id), None)
    if not entry:
        return "Trame non trouvée", 404
    return f"<h2>Détail trame {id}</h2><pre>{json.dumps(entry, indent=2)}</pre>"


    