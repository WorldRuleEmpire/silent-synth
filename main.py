from flask import Flask, request, jsonify
import os
import json
import hashlib
import requests

app = Flask(__name__)

# === CONFIG ===
WEBHOOK_URLS = [
    "https://maker.ifttt.com/trigger/synth_event/with/key/YOUR_IFTTT_KEY",
    "https://discord.com/api/webhooks/YOUR_DISCORD_WEBHOOK"
]
VAULTCHAIN_DIR = "./vaultchain"
BROADCAST_LOG = "./broadcast_registry.json"
NODE_MEMORY = {}

# Ensure necessary directories and files exist
os.makedirs(VAULTCHAIN_DIR, exist_ok=True)
if not os.path.exists(BROADCAST_LOG):
    with open(BROADCAST_LOG, "w") as f:
        json.dump([], f)

# === HOME ===
@app.route("/")
def home():
    return "Silent Synth API is live!"

# === VAULT: Immutable Archive ===
@app.route("/vault", methods=["POST"])
def vault_data():
    payload = request.get_json()
    content = json.dumps(payload, indent=2)
    hash_id = hashlib.sha256(content.encode()).hexdigest()
    path = os.path.join(VAULTCHAIN_DIR, f"{hash_id}.json")
    with open(path, "w") as f:
        f.write(content)
    return jsonify({"vault_id": hash_id, "path": path})

# === ORION: Learn ===
@app.route("/orion/learn", methods=["POST"])
def orion_learn():
    data = request.get_json()
    node = data.get("node", "default-node")
    if node not in NODE_MEMORY:
        NODE_MEMORY[node] = []
    NODE_MEMORY[node].append(data)
    return jsonify({"status": "stored", "node": node, "total": len(NODE_MEMORY[node])})

# === BROADCAST ===
@app.route("/broadcast", methods=["POST"])
def broadcast():
    entry = request.get_json()
    with open(BROADCAST_LOG, "r+") as f:
        logs = json.load(f)
        logs.append(entry)
        f.seek(0)
        json.dump(logs, f, indent=2)
    fire_webhook("broadcast", entry)
    return jsonify({"status": "distributed", "total_entries": len(logs)})

# === FIRE WEBHOOK ===
def fire_webhook(event_type, payload):
    for url in WEBHOOK_URLS:
        try:
            requests.post(url, json={"event": event_type, "data": payload})
        except Exception as e:
            print(f"[WEBHOOK ERROR] {url}: {e}")

# === RENDER CONFIG FILES ===
@app.route("/render_config")
def render_config():
    render_yaml = '''services:
  - type: web
    name: silent-synth
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn main:app"
    plan: free
    envVars:
      - key: PYTHON_VERSION
        value: 3.11'''

    procfile = "web: gunicorn main:app"

    with open("render.yaml", "w") as f:
        f.write(render_yaml)
    with open("Procfile", "w") as f:
        f.write(procfile)

    return jsonify({"status": "Render config files generated", "files": ["render.yaml", "Procfile"]})

# === MAIN (for local testing) ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

@app.route("/")
def home():
    return "Silent Synth API is live!"