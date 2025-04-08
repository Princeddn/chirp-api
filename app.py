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


        if not received_data:
            return  "<h2>Aucune donnée reçue pour le moment. <h2>"

        # HTML ou JSON ?
        accept = request.headers.get('Accept', '')
        if 'text/html' in accept:
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
            return jsonify(received_data), 200
