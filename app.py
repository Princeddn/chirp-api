from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import sqlite3, json
from Decoder import BaseDecoder, NexelecDecoder, WattecoDecoder

app = Flask(__name__)

# Décodeurs
convertion = BaseDecoder()
decoder_nexelec = NexelecDecoder()
decoder_watteco = WattecoDecoder()

DB_FILE = "chirp_data.db"

# === INITIALISATION DB ===
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS uplinks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                device_name TEXT,
                data_base64 TEXT,
                decoded_json TEXT
            )
        """)
        conn.commit()

# === ENREGISTRER UNE NOUVELLE DONNÉE ===
def save_to_db(timestamp, device_name, data_b64, decoded_obj):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO uplinks (timestamp, device_name, data_base64, decoded_json)
            VALUES (?, ?, ?, ?)
        """, (timestamp, device_name, data_b64, json.dumps(decoded_obj)))
        conn.commit()

# === CHARGER LES DONNÉES POUR AFFICHAGE ===
def get_all_data():
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM uplinks ORDER BY id DESC")
        return c.fetchall()

# === DÉCODAGE AUTOMATIQUE ===
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
                return decoder_watteco.decode_presso(decoded_hex)
            else:
                return {"error": f"Type inconnu : 0x{product_type_2octets:04X}"}
    except Exception as e:
        return {"error": str(e)}

# === ROUTE PRINCIPALE ===
@app.route('/uplink', methods=['GET', 'POST'])
def handle_uplink():
    if request.method == 'POST':
        event = request.args.get("event", "up")
        if event != "up":
            return jsonify({"status": f"ignored event: {event}"}), 200

        data = request.json
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        device_name = data.get("deviceInfo", {}).get("deviceName", "Inconnu")
        data_b64 = data.get("data", "vide")
        decoded = decode_lorawan_data(data_b64)

        save_to_db(timestamp, device_name, data_b64, decoded)
        return jsonify({"status": "ok"}), 200

    elif request.method == 'GET':
        rows = get_all_data()
        if not rows:
            return "<h2 style='font-family:Arial;'>Aucune donnée en base.</h2>"

        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard SQLite</title>
            <style>
                body { font-family: Arial; margin: 40px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ccc; padding: 8px; vertical-align: top; }
                th { background-color: #f2f2f2; }
                pre { white-space: pre-wrap; }
            </style>
        </head>
        <body>
            <h2>📊 Données stockées (SQLite)</h2>
            <table>
                <tr>
                    <th>Horodatage</th>
                    <th>Capteur</th>
                    <th>Donnée (base64)</th>
                    <th>Données décodées</th>
                </tr>
                {% for row in rows %}
                <tr>
                    <td>{{ row['timestamp'] }}</td>
                    <td>{{ row['device_name'] }}</td>
                    <td><pre>{{ row['data_base64'] }}</pre></td>
                    <td><pre>{{ row['decoded_json'] }}</pre></td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """
        return render_template_string(html, rows=rows)

# Appel unique au démarrage
init_db()
