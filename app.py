from flask import Flask, request, jsonify, render_template_string, send_file, redirect, url_for
from datetime import datetime
import json, os, csv, uuid

from Decoder import BaseDecoder, NexelecDecoder, WattecoDecoder

app = Flask(__name__)
DB_FILE = "database.json"

# Décodeurs
convertion = BaseDecoder()
decoder_nexelec = NexelecDecoder()
decoder_watteco = WattecoDecoder()

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(entry):
    data = load_data()
    data.append(entry)
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
def uplink():
    if request.method == 'POST':
        event = request.args.get("event", "up")
        if event != "up":
            return jsonify({"status": f"ignored event: {event}"}), 200
        data = request.json
        decoded = decode_lorawan_data(data.get("data", ""))
        data["timestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data["decoded"] = decoded
        data["id"] = str(uuid.uuid4())
        print("📡 Donnée reçue + décodée :", data)
        save_data(data)
        return jsonify({"status": "ok"}), 200

    # Méthode GET
    rows = load_data()
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard Capteurs LoRa</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            .btns button { padding: 8px 16px; margin-right: 10px; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ccc; padding: 8px; vertical-align: top; }
            th { background-color: #f2f2f2; }
            .filter { margin: 20px 0; }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            async function updateChart() {
                const capteur = document.getElementById("capteur").value;
                const grandeur = document.getElementById("grandeur").value;
                const res = await fetch('/uplink?format=json');
                const data = await res.json();
                const filtered = data.filter(d => d.deviceInfo?.deviceName === capteur && d.decoded?.[grandeur]);
                const labels = filtered.map(d => d.timestamp);
                const valeurs = filtered.map(d => d.decoded[grandeur]?.value || 0);
                chart.data.labels = labels;
                chart.data.datasets[0].data = valeurs;
                chart.options.scales.y.title.text = grandeur;
                chart.update();
            }

            let chart;
            window.onload = function() {
                const ctx = document.getElementById('chart').getContext('2d');
                chart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Valeur',
                            data: [],
                            borderColor: 'blue',
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: { title: { display: true, text: 'Temps' }},
                            y: { title: { display: true, text: 'Valeur' }}
                        }
                    }
                });
                updateChart();
                setInterval(updateChart, 10000);
            }
        </script>
    </head>
    <body>
        <h2>📡 Dashboard Données Capteurs LoRa</h2>
        <div class="btns">
            <button onclick="window.location.href='/uplink?format=json'">📄 JSON</button>
            <button onclick="window.location.href='/uplink?format=csv'">⬇️ Export CSV</button>
        </div>
        <div class="filter">
            🔧 Capteur :
            <select id="capteur" onchange="updateChart()">
                {% for c in capteurs %}
                    <option value="{{c}}">{{c}}</option>
                {% endfor %}
            </select>
            🌡️ Grandeur :
            <select id="grandeur" onchange="updateChart()">
                {% for g in grandeurs %}
                    <option value="{{g}}">{{g}}</option>
                {% endfor %}
            </select>
        </div>
        <canvas id="chart" width="600" height="200"></canvas>
        <h3>Données brutes</h3>
        <table>
            <tr>
                <th>Horodatage</th>
                <th>Capteur</th>
                <th>Payload</th>
                <th>Données décodées</th>
            </tr>
            {% for row in rows %}
            <tr>
                <td><a href="/trame/{{ row.id }}">{{ row.timestamp }}</a></td>
                <td>{{ row.deviceInfo.deviceName }}</td>
                <td><pre>{{ row.data }}</pre></td>
                <td><pre>{{ row.decoded | tojson(indent=2) }}</pre></td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    capteurs = list({r.get("deviceInfo", {}).get("deviceName") for r in rows if r.get("deviceInfo")})
    grandeurs = set()
    for r in rows:
        d = r.get("decoded", {})
        if isinstance(d, dict):
            grandeurs.update(d.keys())
    return render_template_string(html, rows=rows, capteurs=capteurs, grandeurs=sorted(grandeurs))

@app.route('/trame/<id>')
def detail_trame(id):
    rows = load_data()
    entry = next((r for r in rows if r.get("id") == id), None)
    if not entry:
        return "Trame non trouvée", 404
    return f"<h2>Détail trame {id}</h2><pre>{json.dumps(entry, indent=2)}</pre>"

@app.route('/uplink', methods=['GET'])
def export_data():
    if request.args.get("format") == "csv":
        rows = load_data()
        csv_file = "export.csv"
        with open(csv_file, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "device", "data", "decoded"])
            for row in rows:
                writer.writerow([
                    row.get("timestamp"),
                    row.get("deviceInfo", {}).get("deviceName"),
                    row.get("data"),
                    json.dumps(row.get("decoded"))
                ])
        return send_file(csv_file, as_attachment=True)
    return redirect(url_for("uplink"))