from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from datetime import datetime
import json, os, csv, uuid, time
from github_backup_push import push_to_github
import requests
from Decoder import jeedom_decoder
from pytz import timezone

app = Flask(__name__, static_folder='assets')
DB_FILE = "database.json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Princeddn/chirp-api/data-backup/database.json"
CHIRPSTACK_API_URL = os.getenv("CHIRPSTACK_API_URL", "https://chirpstack.example.com")
CHIRPSTACK_API_TOKEN = os.getenv("CHIRPSTACK_API_TOKEN", "your_token_here")

def restore_database_from_github(force=False):
    if force or not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
        try:
            r = requests.get(GITHUB_RAW_URL)
            r.raise_for_status()
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(r.json(), f, indent=2, ensure_ascii=False)
            print("✅ Database restored from GitHub.")
        except Exception as e:
            print(f"❌ Restore failed: {e}")

if not os.path.exists(DB_FILE): restore_database_from_github(force=True)

def load_data_local():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return []

def save_data(new_entries):
    current = load_data_local()
    if not isinstance(current, list): current = []
    
    current.extend(new_entries)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)
    
    try:
         pass # push_to_github() # Disabled for speed
    except: pass

def decode_lorawan_data(encoded_data, deveui=None):
    # Delegate everything to the dynamic decoder
    return jeedom_decoder.decode_uplink(encoded_data, deveui)


# --- Routes ---

@app.route('/')
def home():
    # Serve the main dashboard
    return send_file('index.html')

@app.route('/database.json')
def get_database():
    return send_file(DB_FILE)

@app.route('/assets/<path:path>')
def send_assets(path):
    return send_from_directory('assets', path)

@app.route('/uplink', methods=['POST'])
def uplink():
    # Helper to handle ChirpStack webhooks
    data = request.json
    if not data: return jsonify({"error": "No data"}), 400

    dev_eui = data.get("deviceInfo", {}).get("devEui") or data.get("devEUI")
    raw_payload = data.get("data")
    
    decoded = decode_lorawan_data(raw_payload, dev_eui)
    
    paris_tz = timezone('Europe/Paris')
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(paris_tz).strftime('%Y-%m-%d %H:%M:%S %Z'),
        "received_at": datetime.now().isoformat(),
        "devEUI": dev_eui,
        "deviceInfo": data.get("deviceInfo", {}),
        "data": raw_payload,
        "decoded": decoded,
        "fPort": data.get("fPort"),
        "txInfo": data.get("txInfo"),
        "rxInfo": data.get("rxInfo")
    }

    print(f"📡 Uplink from {dev_eui}: {decoded}")
    save_data([entry])
    return jsonify({"status": "stored"}), 200

@app.route('/api/downlink', methods=['POST'])
def send_downlink():
    req = request.json
    dev_eui = req.get('devEui')
    payload = req.get('data') # Hex or Base64
    port = req.get('fPort', 1)
    
    if not dev_eui: return jsonify({"error": "Missing devEui"}), 400

    print(f"⬇️ Downlink Request -> {dev_eui} : {payload}")

    try:
        import base64
        # Try to treat as hex first
        payload_bytes = bytes.fromhex(payload)
        payload_b64 = base64.b64encode(payload_bytes).decode('utf-8')
    except:
        payload_b64 = payload

    url = f"{CHIRPSTACK_API_URL}/api/devices/{dev_eui}/queue"
    headers = {
        "Grpc-Metadata-Authorization": f"Bearer {CHIRPSTACK_API_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "deviceQueueItem": {
            "confirmed": False,
            "data": payload_b64,
            "fPort": port,
            "object": None
        }
    }
    
    if "your_token_here" in CHIRPSTACK_API_TOKEN:
        # Simulation Mode
        return jsonify({
            "status": "simulated", 
            "message": "Token not configured. Downlink simulated.", 
            "payload": payload_b64
        }), 200

    try:
        r = requests.post(url, json=body, headers=headers, timeout=5)
        if r.status_code in [200, 201]:
             return jsonify({"status": "queued", "chirpstack_resp": r.json()}), 200
        else:
             return jsonify({"error": "ChirpStack Error", "details": r.text}), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)