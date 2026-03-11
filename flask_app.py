from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session, Response
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3
import datetime

from tester.runner import run_all
import storage

app = Flask(__name__)
storage.init_db()

# ─── Route existante ─────────────────────────────────────────────────────────

@app.get("/")
def consignes():
    return render_template('consignes.html')

# ─── /run ────────────────────────────────────────────────────────────────────

@app.route("/run")
def trigger_run():
    """Déclenche un run de tests, sauvegarde et redirige vers le dashboard."""
    report = run_all()
    storage.save_run(report)
    return redirect(url_for("dashboard"))

@app.route("/run/json")
def trigger_run_json():
    """Déclenche un run et retourne le rapport JSON brut."""
    report = run_all()
    storage.save_run(report)
    return jsonify(report)

# ─── /dashboard ──────────────────────────────────────────────────────────────

@app.route("/dashboard")
def dashboard():
    runs = storage.list_runs(limit=20)
    last_run = storage.get_run(runs[0]["id"]) if runs else None
    return render_template("dashboard.html", runs=runs, last_run=last_run)

# ─── /run/<id> ───────────────────────────────────────────────────────────────

@app.route("/run/<int:run_id>")
def run_detail(run_id):
    run = storage.get_run(run_id)
    if not run:
        return jsonify({"error": "Run not found"}), 404
    return jsonify(run)

# ─── /health ─────────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    runs = storage.list_runs(limit=1)
    last = runs[0] if runs else None
    status = "ok"
    availability = None
    if last:
        availability = last["summary"].get("availability", 0)
        if availability < 0.5:
            status = "degraded"
    return jsonify({
        "status": status,
        "uptime": "N/A",
        "last_run": last["timestamp"] if last else None,
        "availability": availability,
        "checked_at": datetime.datetime.now().isoformat(),
    })

# ─── /export ─────────────────────────────────────────────────────────────────

@app.route("/export")
def export_json():
    """Export des 20 derniers runs en JSON téléchargeable."""
    runs = storage.list_runs(limit=20)
    payload = json.dumps(runs, indent=2, ensure_ascii=False)
    return Response(
        payload,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=runs_export.json"},
    )

if __name__ == "__main__":
    # utile en local uniquement
    app.run(host="0.0.0.0", port=5000, debug=True)
