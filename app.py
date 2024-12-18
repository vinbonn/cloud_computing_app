from flask import Flask, jsonify, Response
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)

# Autoriser tous les CORS
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/api/start-wireguard', methods=['POST'])
def start_wireguard():
    try:
        # Lancer Docker Compose depuis /opt/myapp
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd="/opt/myapp",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode != 0:
            return jsonify({"error": result.stderr.decode()}), 500

        # Chemin du fichier de configuration généré (ajusté pour être sous /opt/myapp)
        config_path = "/opt/myapp/wireguard-server/config/peer1/peer1.conf"

        # Vérifier si le fichier existe
        if not os.path.exists(config_path):
            return jsonify({"error": f"Configuration file not found at {config_path}"}), 404

        # Lire le contenu du fichier de configuration
        with open(config_path, "r") as config_file:
            config_content = config_file.read()

        # Retourner le contenu du fichier
        return Response(config_content, mimetype="text/plain"), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stop-wireguard', methods=['POST'])
def stop_wireguard():
    try:
        result = subprocess.run(
            ["docker-compose", "down"],
            cwd="/opt/myapp",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            return jsonify({"message": "WireGuard stopped successfully"}), 200
        else:
            return jsonify({"error": result.stderr.decode()}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/apis', methods=['GET'])
def list_apis():
    apis = [
        "POST /start-wireguard - Start the WireGuard container and return peer1.conf",
        "POST /stop-wireguard - Stop the WireGuard container",
        "GET /apis - List all available APIs"
    ]
    return jsonify({"apis": apis}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
