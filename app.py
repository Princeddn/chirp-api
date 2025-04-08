from flask import Flask, request, jsonify, render_template_string, send_file
from datetime import datetime
import json, os, csv
from Decoder import BaseDecoder, NexelecDecoder, WattecoDecoder

app = Flask(__name__)
DB_FILE = "database.json"

# Initialisation des décodeurs
convertion = BaseDecoder()
decoder_nexelec = NexelecDecoder()
decoder_watteco = WattecoDecoder()

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
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
                return {"error": f"Type inconnu : 0x{product_type_2octets:04X}"}
    except Exception as e:
        return {"error": str(e)}

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

        entry = {
            "timestamp": timestamp,
            "device": device_name,
            "data": data_b64,
            "decoded": decoded
        }

        save_data(entry)
        return jsonify({"status": "ok"}), 200

    # Méthode GET
    format_type = request.args.get("format", "html")
    rows = load_data()

    if format_type == "json":
        return jsonify(rows)

    elif format_type == "csv":
        csv_file = "export.csv"
        with open(csv_file, "w", newline='') as csvfile:
            fieldnames = ["timestamp", "device", "data", "decoded"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({
                    "timestamp": row["timestamp"],
                    "device": row["device"],
                    "data": row["data"],
                    "decoded": json.dumps(row["decoded"])
                })
        return send_file(csv_file, as_attachment=True)

    else:
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Données LoRa</title>
            <style>
                body { font-family: Arial; margin: 40px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ccc; padding: 8px; vertical-align: top; }
                th { background-color: #f2f2f2; }
                pre { white-space: pre-wrap; }
            </style>
        </head>
        <body>
            <h2>📡 Données reçues de ChirpStack</h2>
            <p>Total : {{ rows|length }} trame(s)</p>
            <table>
                <tr>
                    <th>Horodatage</th>
                    <th>Capteur</th>
                    <th>Trame</th>
                    <th>Décodé</th>
                </tr>
                {% for row in rows %}
                <tr>
                    <td>{{ row.timestamp }}</td>
                    <td>{{ row.device }}</td>
                    <td><pre>{{ row.data }}</pre></td>
                    <td><pre>{{ row.decoded | tojson(indent=2) }}</pre></td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """
        return render_template_string(html, rows=rows)