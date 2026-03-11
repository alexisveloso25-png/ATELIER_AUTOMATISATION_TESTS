# ── Ajouter ces imports en haut ──
from flask import Response
import datetime
import storage
from tester.runner import run_all

storage.init_db()

# ── Ajouter ces routes à la fin, avant le if __name__ ──

@app.route("/run")
def trigger_run():
    report = run_all()
    storage.save_run(report)
    return redirect(url_for("dashboard"))

@app.route("/run/json")
def trigger_run_json():
    report = run_all()
    storage.save_run(report)
    return jsonify(report)

@app.route("/dashboard")
def dashboard():
    runs = storage.list_runs(limit=20)
    last_run = storage.get_run(runs[0]["id"]) if runs else None
    return render_template("dashboard.html", runs=runs, last_run=last_run)

@app.route("/run/<int:run_id>")
def run_detail(run_id):
    run = storage.get_run(run_id)
    if not run:
        return jsonify({"error": "Run not found"}), 404
    return jsonify(run)

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
        "last_run": last["timestamp"] if last else None,
        "availability": availability,
        "checked_at": datetime.datetime.now().isoformat(),
    })

@app.route("/export")
def export_json():
    runs = storage.list_runs(limit=20)
    payload = json.dumps(runs, indent=2, ensure_ascii=False)
    return Response(
        payload,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=runs_export.json"},
    )
