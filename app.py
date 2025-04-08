from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# Stockage temporaire des trames
received_data = []

@app.route('/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'POST':
        # Réception des données de ChirpStack
        data = request.json
        data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        received_data.append(data)
        print("📡 Donnée reçue :", data)
        return jsonify({"status": "ok"}), 200

    elif request.method == 'GET':
        # Vérifie si le client attend du HTML ou du JSON
        accept = request.headers.get('Accept', '')
        if 'text/html' in accept:
            # Rendu HTML
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Dashboard - Données ChirpStack</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ccc; padding: 8px; }
                    th { background-color: #f2f2f2; }
                    pre { margin: 0; white-space: pre-wrap; }
                </style>
            </head>
            <body>
                <h2>📊 Données reçues de ChirpStack</h2>
                <p>Total : {{ data|length }} trame(s)</p>
                <table>
                    <tr>
                        <th>Timestamp</th>
                        <th>Device Name</th>
                        <th>Application ID</th>
                        <th>Payload</th>
                    </tr>
                    {% for entry in data %}
                    <tr>
                        <td>{{ entry.timestamp }}</td>
                        <td>{{ entry.deviceName }}</td>
                        <td>{{ entry.applicationID }}</td>
                        <td><pre>{{ entry.object | tojson(indent=2) }}</pre></td>
                    </tr>
                    {% endfor %}
                </table>
            </body>
            </html>
            """
            return render_template_string(html, data=received_data)
        else:
            # Rendu JSON
            return jsonify(received_data), 200
