from flask import Flask, request, jsonify, render_template_string, send_file
from datetime import datetime
import json, os, csv
from Decoder import BaseDecoder, NexelecDecoder, WattecoDecoder

app = Flask(__name__)
DB_FILE = "database.json"

convertion = BaseDecoder()
decoder_nexelec = NexelecDecoder()
decoder_watteco = WattecoDecoder()

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(full_data):
    data = load_data()
    data.append(full_data)
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

@app.route("/uplink", methods=["GET", "POST"])
def handle_uplink():
    if request.method == "POST":
        event = request.args.get("event", "up")
        if event != "up":
            return jsonify({"status": f"ignored event: {event}"}), 200

        data = request.json
        data["timestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        decoded = decode_lorawan_data(data.get("data", ""))
        data["decoded"] = decoded

        print("\U0001F4E1 Donnée reçue + décodée :", data)
        save_data(data)
        return jsonify({"status": "ok"}), 200

    elif request.method == "GET":
        rows = load_data()
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard LoRa + Données décodées</title>
            <style>
                body { font-family: Arial; margin: 20px; }
                table { border-collapse: collapse; width: 100%; margin-top: 30px; }
                th, td { border: 1px solid #ccc; padding: 6px; }
                th { background-color: #f9f9f9; }
                select, input { margin: 5px; padding: 5px; }
                canvas { max-width: 100%; height: auto; }
            </style>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <h2>📡 Données Reçues et Décodées</h2>

            <label for="grandeur">Choisir une grandeur :</label>
            <select id="grandeur" onchange="updateChart()">
                <option value="temperature">Température</option>
                <option value="humidity">Humidité</option>
                <option value="co2">CO2</option>
                <option value="voc">VOC</option>
                <option value="PM1">PM1</option>
                <option value="PM2.5">PM2.5</option>
                <option value="PM10">PM10</option>
            </select>

            <canvas id="graph" height="100"></canvas>

            <table>
                <tr>
                    <th>Horodatage</th>
                    <th>Capteur</th>
                    <th>Data</th>
                    <th>Décodage</th>
                </tr>
                {% for row in rows %}
                <tr>
                    <td>{{ row.timestamp }}</td>
                    <td>{{ row.deviceInfo.deviceName }}</td>
                    <td><pre>{{ row.data }}</pre></td>
                    <td><pre>{{ row.decoded | tojson(indent=2) }}</pre></td>
                </tr>
                {% endfor %}
            </table>

            <script>
                var allData = {{ rows | tojson }};
                var chart;

                function updateChart() {
                    let g = document.getElementById('grandeur').value;
                    let labels = [];
                    let values = [];

                    allData.forEach(d => {
                        let time = d.timestamp;
                        let decoded = d.decoded;
                        if (decoded && decoded[g] && decoded[g].value !== undefined) {
                            labels.push(time);
                            values.push(decoded[g].value);
                        }
                    });

                    if (chart) chart.destroy();

                    const ctx = document.getElementById('graph').getContext('2d');
                    chart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: g + ' en fonction du temps',
                                data: values,
                                fill: false,
                                borderColor: 'blue',
                                tension: 0.1
                            }]
                        }
                    });
                }

                window.onload = updateChart;
            </script>
        </body>
        </html>
        """
        return render_template_string(html, rows=rows)

if __name__ == '__main__':
    app.run(debug=True)
