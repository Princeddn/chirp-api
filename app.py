from flask import Flask, request, jsonify, render_template_string, send_file
from datetime import datetime
import json, os, csv, uuid, time
from github_backup_push import push_to_github
import requests
from Decoder import BaseDecoder, NexelecDecoder, WattecoDecoder

app = Flask(__name__)
DB_FILE = "database.json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Princeddn/chirp-api/data-backup/database.json"
convertion = BaseDecoder()
decoder_nexelec = NexelecDecoder()
decoder_watteco = WattecoDecoder()

def load_data_local():
    """Lit localement database.json."""
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
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

def save_data(new_entries):
    """Ajoute les nouvelles entrées en local, puis push GitHub."""
    current = load_data_local()
    existing_ids = {d.get("id") for d in current}
    new_data = [d for d in new_entries if d.get("id") not in existing_ids]

    if new_data:
        current.extend(new_data)
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, ensure_ascii=False)
        print(f"✅ {len(new_data)} nouvelle(s) donnée(s) sauvegardée(s)")

        time.sleep(0.2)  # Petit délai avant push
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
        save_data([data])
        push_to_github()
        return jsonify({"status": "ok"}), 200

    rows = load_data_github()
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

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard LoRa Optimisé</title>
        <!-- Bootstrap CSS -->
        <link rel="stylesheet"
              href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
        <style>
          body { margin: 20px; }
          pre { margin: 0; }
          .alarm { background-color: #ffcccc !important; }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            let chart;
            async function loadData() {
                const res = await fetch('/uplink?format=json');
                return await res.json();
            }

            // Rafraîchit le tableau toutes les X secondes
            async function autoRefresh() {
                await refreshTable();
                setTimeout(autoRefresh, 10000); // toutes les 10s
            }

            async function refreshTable() {
                const data = await loadData();
                const tbody = document.getElementById('sensor-tbody');
                tbody.innerHTML = '';

                data.forEach(d => {
                    const tr = document.createElement('tr');

                    // Check alarme co2
                    if (d.decoded?.co2?.value > 1000) {
                       tr.classList.add('alarm');
                    }

                    const tdTime = document.createElement('td');
                    tdTime.innerHTML = d.timestamp || '';
                    tr.appendChild(tdTime);

                    const tdDevice = document.createElement('td');
                    tdDevice.innerHTML = d.deviceInfo?.deviceName || '';
                    tr.appendChild(tdDevice);

                    const tdData = document.createElement('td');
                    tdData.innerHTML = '<pre>'+(d.data || '')+'</pre>';
                    tr.appendChild(tdData);

                    const tdDecoded = document.createElement('td');
                    tdDecoded.innerHTML = '<pre>'+JSON.stringify(d.decoded, null, 2)+'</pre>';
                    tr.appendChild(tdDecoded);

                    tbody.appendChild(tr);
                });
            }

            async function updateChart() {
                const capteur = document.getElementById("capteur").value;
                const grandeur = document.getElementById("grandeur").value;
                const data = await loadData();
                const filtered = data.filter(d =>
                    (capteur === "all" || d.deviceInfo?.deviceName === capteur) &&
                    d.decoded?.[grandeur]?.value !== undefined
                );
                const labels = filtered.map(d => d.timestamp);
                const vals = filtered.map(d => d.decoded[grandeur].value);

                chart.data.labels = labels;
                chart.data.datasets[0].label = grandeur;
                chart.data.datasets[0].data = vals;
                chart.update();
            }

            async function lancerBackup() {
                const res = await fetch("/uplink?event=push", { method: "POST" });
                const result = await res.json();
                alert(result.status);
            }

            window.onload = async function() {
                // Initial chart
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
                        responsive: true
                    }
                });

                // Premier refresh
                await refreshTable();
                // auto refresh
                autoRefresh();
            }
        </script>
    </head>
    <body class="container">
        <h1 class="mt-4 mb-4">📡 Dashboard Capteurs LoRa (Optimisé)</h1>
        <div class="mb-3">
            <button class="btn btn-outline-primary me-2" onclick="location.href='/uplink?format=json'">📄 JSON</button>
            <button class="btn btn-outline-success me-2" onclick="location.href='/uplink?format=csv'">⬇️ Export CSV</button>
            <button class="btn btn-outline-info" onclick="lancerBackup()">💾 Sauvegarde GitHub</button>
        </div>

        <div class="row mb-3">
          <div class="col-md-4">
            <label>🔧 Capteur:</label>
            <select id="capteur" class="form-select">
                <option value="all">Tous</option>
                {% for c in capteurs %}
                    <option value="{{c}}">{{c}}</option>
                {% endfor %}
            </select>
          </div>
          <div class="col-md-4">
            <label>🌡️ Grandeur:</label>
            <select id="grandeur" class="form-select">
                {% for g in grandeurs %}
                    <option value="{{g}}">{{g}}</option>
                {% endfor %}
            </select>
          </div>
          <div class="col-md-4 d-flex align-items-end">
            <button class="btn btn-outline-primary" onclick="updateChart()">🔄 Courbe</button>
          </div>
        </div>

        <canvas id="chart" style="max-width: 100%; height: 300px;"></canvas>

        <h3 class="mt-4">📋 Données Reçues (auto-refresh)</h3>
        <table class="table table-bordered">
            <thead class="table-light">
                <tr>
                    <th>Horodatage</th>
                    <th>Capteur</th>
                    <th>Payload</th>
                    <th>Données décodées</th>
                </tr>
            </thead>
            <tbody id="sensor-tbody">
            </tbody>
        </table>

        <!-- Bootstrap JS -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    return render_template_string(html, rows=rows, capteurs=capteurs, grandeurs=sorted(grandeurs))

@app.route('/trame/<id>')
def detail_trame(id):
    rows = load_data_github()
    entry = next((r for r in rows if r.get("id") == id), None)
    if not entry:
        return "Trame non trouvée", 404
    return f"<h2>Détail trame {id}</h2><pre>{json.dumps(entry, indent=2)}</pre>"

# Au démarrage, si le local est vide => on télécharge la base depuis GitHub
if not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
    print("🌀 database.json vide. On le recharge depuis GitHub.")
    try:
        r = requests.get(GITHUB_RAW_URL)
        r.raise_for_status()
        initial_data = r.json()
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)
        print("✅ Base locale initialisée depuis GitHub.")
    except Exception as e:
        print("❌ Erreur initialisation locale :", e)