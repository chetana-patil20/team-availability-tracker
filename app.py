"""Team Availability Tracker - Flask + SQLite demo application."""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB = BASE_DIR / "instance" / "availability.db"

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
    DATABASE=os.environ.get("DATABASE_PATH", str(DEFAULT_DB)),
    JSON_SORT_KEYS=False,
)

SEED_USERS = [
    ("Ava Patel", "Senior Developer", "AP", "#e9e7ff", "#6654d9", 1),
    ("Mia Chen", "UX Designer", "MC", "#ffe8ee", "#c34e78", 0),
    ("Noah Taylor", "Project Manager", "NT", "#e1f5ed", "#278565", 1),
    ("Sofia Garcia", "Marketing Lead", "SG", "#fff0d9", "#a66a13", 1),
    ("Ethan Brooks", "Data Analyst", "EB", "#e2efff", "#326cb4", 0),
    ("Zara Khan", "Frontend Engineer", "ZK", "#fce8db", "#b45d2b", 1),
]

@contextmanager
def get_db():
    """Open a short-lived SQLite connection and always close it."""
    db_path = Path(app.config["DATABASE"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db() -> None:
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS team_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                initials TEXT NOT NULL,
                avatar_bg TEXT NOT NULL,
                avatar_color TEXT NOT NULL,
                is_available INTEGER NOT NULL DEFAULT 0 CHECK (is_available IN (0, 1)),
                updated_at TEXT NOT NULL
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM team_members").fetchone()[0]
        if count == 0:
            now = datetime.now(timezone.utc).isoformat(timespec="seconds")
            conn.executemany(
                "INSERT INTO team_members (name, role, initials, avatar_bg, avatar_color, is_available, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [(*member, now) for member in SEED_USERS],
            )


def serialize_member(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"], "name": row["name"], "role": row["role"],
        "initials": row["initials"], "avatar_bg": row["avatar_bg"],
        "avatar_color": row["avatar_color"], "is_available": bool(row["is_available"]),
        "updated_at": row["updated_at"],
    }


def fetch_members() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM team_members ORDER BY id").fetchall()
    return [serialize_member(row) for row in rows]


@app.get("/")
def index():
    members = fetch_members()
    available = sum(member["is_available"] for member in members)
    return render_template("index.html", members=members, available=available, total=len(members))


@app.get("/api/members")
def api_members():
    members = fetch_members()
    return jsonify({"members": members, "available": sum(m["is_available"] for m in members), "total": len(members)})


@app.patch("/api/members/<int:member_id>/availability")
def update_availability(member_id: int):
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload.get("is_available"), bool):
        return jsonify({"error": "is_available must be a boolean."}), 400

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE team_members SET is_available = ?, updated_at = ? WHERE id = ?",
            (int(payload["is_available"]), now, member_id),
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "Team member not found."}), 404
        row = conn.execute("SELECT * FROM team_members WHERE id = ?", (member_id,)).fetchone()
    return jsonify({"member": serialize_member(row)})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


# Create the database when running locally; safe to run more than once.
with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=os.environ.get("FLASK_DEBUG", "1") == "1")
