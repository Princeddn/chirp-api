from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# Liste pour stocker les trames
received_data = []

@app.route('/uplink', methods=['GET', 'POST'])
def handle_uplink():
    if request.method == 'POST':
        event = request.args.get("event", "up")

        # On ne garde que les événements "up"
        if event != "up":
            print(f"📭 Reçu un event ignoré : {event}")
            return jsonify({"status": f"ignored event: {event}"}), 200

        # Donnée envoyée par ChirpStack
        data = request.json
        data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        received_data.append(data)
        print("📡 Donnée reçue :", data)
        return jsonify({"status": "ok"}), 200

    elif request.method == 'GET':


        accept = request.headers.get('Accept', '')

        # Cas où aucune donnée n'est encore reçue
        if not received_data:
            if 'application/json' in accept:
                return jsonify([]), 200
            else:
                return "<h2 style='font-family:Arial;'>Aucune donnée reçue pour le moment.</h2>"

        # HTML par défaut, JSON seulement si explicitement demandé
        if 'application/json' in accept:
            return jsonify(received_data), 200
        else:
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
                        <th>Donnée (data)</th>
                    </tr>
                    {% for entry in data %}
                    <tr>
                        <td>{{ entry.timestamp }}</td>
                        <td>{{ entry.deviceInfo.deviceName }}</td>
                        <td><pre>{{ entry.data }}</pre></td>
                    </tr>
                    {% endfor %}
                </table>
            </body>
            </html>
            """
            return render_template_string(html, data=received_data)