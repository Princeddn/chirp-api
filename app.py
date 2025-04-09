from flask import Flask, request, jsonify, render_template_string, send_file
from datetime import datetime
import json, os, csv, uuid
from github_backup_push import push_to_github

from Decoder import BaseDecoder, NexelecDecoder, WattecoDecoder

app = Flask(__name__)
DB_FILE = "database.json"

convertion = BaseDecoder()
decoder_nexelec = NexelecDecoder()
decoder_watteco = WattecoDecoder()

def load_data():
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        return []
    except Exception as e:
        print(f"⚠️ Erreur lecture JSON : {e}")
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
        if event == "push":
            push_to_github()
            return jsonify({"status": "✅ Sauvegarde GitHub déclenchée"}), 200

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

    rows = load_data()
    fmt = request.args.get("format")

    if fmt == "json":
        return jsonify(rows)

    elif fmt == "csv":
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

    capteurs = sorted({r.get("deviceInfo", {}).get("deviceName") for r in rows if r.get("deviceInfo")})
    grandeurs = set()
    for r in rows:
        decoded = r.get("decoded", {})
        if isinstance(decoded, dict):
            grandeurs.update(decoded.keys())

    html = """<!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard LoRa</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            .btns button { padding: 8px 16px; margin-right: 10px; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ccc; padding: 8px; vertical-align: top; }
            th { background-color: #f2f2f2; }
            .filter { margin: 20px 0; }
            .msg { margin-top: 15px; font-weight: bold; color: green; }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            let chart;
            async function updateChart() {
                const capteur = document.getElementById("capteur").value;
                const grandeur = document.getElementById("grandeur").value;
                const res = await fetch('/uplink?format=json');
                const data = await res.json();
                const filtered = data.filter(d =>
                    (capteur === "all" || d.deviceInfo?.deviceName === capteur) &&
                    d.decoded?.[grandeur]?.value !== undefined
                );
                const labels = filtered.map(d => d.timestamp);
                const valeurs = filtered.map(d => d.decoded[grandeur].value);
                chart.data.labels = labels;
                chart.data.datasets[0].label = grandeur + " (" + (filtered[0]?.decoded[grandeur]?.unit || '') + ")";
                chart.data.datasets[0].data = valeurs;
                chart.update();
            }

            async function lancerBackup() {
                const res = await fetch("/uplink?event=push", { method: "POST" });
                const data = await res.json();
                document.getElementById("msg").innerText = data.status;
            }

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
                            borderWidth: 2,
                            fill: false
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: { title: { display: true, text: 'Horodatage' }},
                            y: { title: { display: true, text: 'Valeur mesurée' }}
                        }
                    }
                });
            }
        </script>
    </head>
    <body>
        <h2>📡 Dashboard Capteurs LoRa</h2>
        <div class="btns">
            <button onclick="window.location.href='/uplink?format=json'">📄 JSON</button>
            <button onclick="window.location.href='/uplink?format=csv'">⬇️ Export CSV</button>
            <button onclick="lancerBackup()">💾 Sauvegarde GitHub</button>
            <span class="msg" id="msg"></span>
        </div>
        <div class="filter">
            🔧 Capteur :
            <select id="capteur">
                <option value="all">Tous</option>
                {% for c in capteurs %}
                    <option value="{{c}}">{{c}}</option>
                {% endfor %}
            </select>
            🌡️ Grandeur :
            <select id="grandeur">
                {% for g in grandeurs %}
                    <option value="{{g}}">{{g}}</option>
                {% endfor %}
            </select>
            <button onclick="updateChart()">🔄 Afficher la courbe</button>
        </div>
        <canvas id="chart" width="600" height="200"></canvas>
        <h3>📋 Données Reçues</h3>
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
    </html>"""
    return render_template_string(html, rows=rows, capteurs=capteurs, grandeurs=sorted(grandeurs))

@app.route('/trame/<id>')
def detail_trame(id):
    rows = load_data()
    entry = next((r for r in rows if r.get("id") == id), None)
    if not entry:
        return "Trame non trouvée", 404
    return f"<h2>Détail trame {id}</h2><pre>{json.dumps(entry, indent=2)}</pre>"

if __name__ == "__main__":
    app.run(debug=True)
