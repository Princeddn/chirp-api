from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# Stockage temporaire des trames reçues
received_data = []

# Route pour recevoir les données depuis ChirpStack
@app.route('/uplink', methods=['POST'])
def uplink():
    data = request.json
    print(" Trame reçue :", data)

    # Ajout d'un horodatage
    data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Enregistrement dans la liste
    received_data.append(data)

    return jsonify({"status": "ok"}), 200

# Route pour afficher les données reçues dans un tableau HTML
@app.route('/dashboard')
def dashboard():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard ChirpStack</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h2>🛰️ Données reçues de ChirpStack</h2>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Device</th>
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
