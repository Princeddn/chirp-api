from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import json
import os
from Decoder import BaseDecoder, NexelecDecoder, WattecoDecoder  # 👈 Import de tes décodeurs

app = Flask(__name__)
DB_FILE = "database.json"

# Initialiser les décodeurs
convertion = BaseDecoder()
decoder_nexelec = NexelecDecoder()
decoder_watteco = WattecoDecoder()

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    else:
        return []

def save_data(new_entry):
    data = load_data()
    data.append(new_entry)
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

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
                return {"error": f"Type inconnu: 0x{product_type_2octets:04X}"}
    except Exception as e:
        return {"error": str(e)}

@app.route('/uplink', methods=['GET', 'POST'])
def handle_uplink():
    if request.method == 'POST':
        event = request.args.get("event", "up")
        if event != "up":
            print(f"📭 Event ignoré : {event}")
            return jsonify({"status": f"ignored event: {event}"}), 200

        data = request.json
        data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # ⬇️ Ajout du décodage de la trame LoRaWAN
        if 'data' in data:
            decoded = decode_lorawan_data(data['data'])
            data['decoded'] = decoded

        save_data(data)
        print("📡 Donnée reçue + décodée :", data)
        return jsonify({"status": "ok"}), 200

    elif request.method == 'GET':
        data = load_data()

        if not data:
            return "<h2 style='font-family:Arial;'>Aucune donnée reçue pour le moment.</h2>"

        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard - Données Décodées</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ccc; padding: 8px; vertical-align: top; }
                th { background-color: #f2f2f2; }
                pre { margin: 0; white-space: pre-wrap; }
            </style>
        </head>
        <body>
            <h2>📊 Données décodées de ChirpStack</h2>
            <p>Total : {{ data|length }} trame(s)</p>
            <table>
                <tr>
                    <th>Timestamp</th>
                    <th>Device Name</th>
                    <th>Trame Base64</th>
                    <th>Décodé</th>
                </tr>
                {% for entry in data %}
                <tr>
                    <td>{{ entry.timestamp }}</td>
                    <td>{{ entry.deviceInfo.deviceName }}</td>
                    <td><pre>{{ entry.data }}</pre></td>
                    <td><pre>{{ entry.decoded | tojson(indent=2) }}</pre></td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """
        return render_template_string(html, data=data)
