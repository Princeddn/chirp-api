from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/uplink', methods=['POST'])
def uplink():
    data = request.json
    print("Donnée reçue de ChirpStack :", data) 
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
