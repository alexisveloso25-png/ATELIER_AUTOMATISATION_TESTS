import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "runs.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT    NOT NULL,
                summary   TEXT    NOT NULL,
                per_api   TEXT    NOT NULL,
                tests     TEXT    NOT NULL
            )
        """)
        conn.commit()


def save_run(report: dict):
    with _connect() as conn:
        conn.execute(
            "INSERT INTO runs (timestamp, summary, per_api, tests) VALUES (?, ?, ?, ?)",
            (
                report["timestamp"],
                json.dumps(report["summary"]),
                json.dumps(report["per_api"]),
                json.dumps(report["tests"]),
            ),
        )
        conn.commit()


def list_runs(limit: int = 20) -> list:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, timestamp, summary, per_api FROM runs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "summary": json.loads(row["summary"]),
            "per_api": json.loads(row["per_api"]),
        }
        for row in rows
    ]


def get_run(run_id: int):
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM runs WHERE id = ?", (run_id,)
        ).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "timestamp": row["timestamp"],
        "summary": json.loads(row["summary"]),
        "per_api": json.loads(row["per_api"]),
        "tests": json.loads(row["tests"]),
    }
