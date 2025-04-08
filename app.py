from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# Stockage temporaire des trames
received_data = []

@app.route('/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'POST':
        event = request.args.get("event", "up")

        # On ne garde que les événements "up"
        if event != "up":
            print(f" Reçu un event ignoré : {event}")
            return jsonify({"status": f"ignored event: {event}"}), 200

        data = request.json
        data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        received_data.append(data)
        print("📡 Donnée reçue :", data)
        return jsonify({"status": "ok"}), 200

    elif request.method == 'GET':
        accept = request.headers.get('Accept', '')
        if 'text/html' in accept:
            html = """ ... (HTML inchangé) ... """
            return render_template_string(html, data=received_data)
        else:
            return jsonify(received_data), 200
