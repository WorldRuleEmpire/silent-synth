# Silent Synth - Phase Vaultchain + Orion + Broadcast
# Immutable archival, evolving agents, public distribution

from flask import Flask, request, jsonify, render_template_string, redirect, url_for, send_file
import uuid
import random
import datetime
import qrcode
import os
import json
from io import BytesIO
from base64 import b64encode
import shutil
import threading
import subprocess
import requests
import hashlib

app = Flask(__name__)

# === CONFIG ===
API_KEYS = {"master": "your_api_token"}
EVENT_LOG = []
AFFILIATES = {"master": {"sales": 0, "revenue": 0.0}}
STORE_PRODUCTS = []
WEBHOOK_URLS = [
    "https://maker.ifttt.com/trigger/synth_event/with/key/YOUR_IFTTT_KEY",
    "https://discord.com/api/webhooks/YOUR_DISCORD_WEBHOOK"
]
QR_DIR = "./qr_codes"
PRODUCT_DIR = "./products"
DELIVERY_TOKENS = {}
CHAIN_LOG = "./ledger.json"
CLONE_DIR = "./clones"
GLOBAL_MESH = ["node-alpha", "node-beta", "node-omega"]
SWARM_AGENTS = {}
USERS = []
TOKEN_LEDGER = {}
TOKEN_ECONOMY = {
    "balances": {},
    "supply": 1000000,
    "symbol": "SYNTH"
}
LICENSE_REGISTRY = {}
INSIGHT_LOG = []
NODE_MEMORY = {}
NFT_METADATA_DIR = "./nft_metadata"
EXPORT_DIR = "./export"
VAULTCHAIN_DIR = "./vaultchain"
BROADCAST_LOG = "./broadcast_registry.json"

os.makedirs(QR_DIR, exist_ok=True)
os.makedirs(PRODUCT_DIR, exist_ok=True)
os.makedirs(CLONE_DIR, exist_ok=True)
os.makedirs(NFT_METADATA_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(VAULTCHAIN_DIR, exist_ok=True)

if not os.path.exists(CHAIN_LOG):
    with open(CHAIN_LOG, "w") as chain_file: json.dump([], chain_file)
if not os.path.exists(BROADCAST_LOG):
    with open(BROADCAST_LOG, "w") as f: json.dump([], f)

# === Phase Vaultchain: Immutable Archive ===
@app.route("/vault", methods=["POST"])
def vault_data():
    payload = request.get_json()
    content = json.dumps(payload, indent=2)
    hash_id = hashlib.sha256(content.encode()).hexdigest()
    path = os.path.join(VAULTCHAIN_DIR, f"{hash_id}.json")
    with open(path, "w") as f:
        f.write(content)
    return jsonify({"vault_id": hash_id, "path": path})

# === Phase Orion: Evolving Agent ===
@app.route("/orion/learn", methods=["POST"])
def orion_learn():
    data = request.get_json()
    node = data.get("node")
    if node not in NODE_MEMORY:
        NODE_MEMORY[node] = []
    NODE_MEMORY[node].append(data)
    return jsonify({"status": "stored", "node": node, "total": len(NODE_MEMORY[node])})

# === Phase Broadcast: Registry Distribution ===
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

# === Render Deploy Support ===
@app.route("/render_config")
def render_config():
    render_yaml = '''services:
  - type: web
    name: silent-synth
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python main.py"
    plan: free
    envVars:
      - key: PYTHON_VERSION
        value: 3.11'''
    procfile = "web: python main.py"
    with open("render.yaml", "w") as f:
        f.write(render_yaml)
    with open("Procfile", "w") as f:
        f.write(procfile)
    return jsonify({"status": "Render files generated", "files": ["render.yaml", "Procfile"]})

# === Fire Webhook Utility ===
def fire_webhook(event_type, payload):
    for url in WEBHOOK_URLS:
        try:
            requests.post(url, json={"event": event_type, "data": payload})
        except Exception as e:
            print(f"[WEBHOOK FAIL] {url} - {e}")
