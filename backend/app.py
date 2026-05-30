import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, g

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_FILE = os.path.join(BASE_DIR, "contact.db")

app = Flask(__name__)


def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DB_FILE)
        db.row_factory = sqlite3.Row
    return db


def create_tables():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            message TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    db.commit()


@app.before_first_request
def before_first_request():
    os.makedirs(BASE_DIR, exist_ok=True)
    create_tables()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,DELETE,OPTIONS"
    return response


@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "Grace backend is running."})


@app.route("/api/contacts", methods=["GET", "POST", "OPTIONS"])
def contacts():
    if request.method == "OPTIONS":
        return "", 204

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()
        phone = (data.get("phone") or "").strip()
        message = (data.get("message") or "").strip()

        if not name or not email:
            return jsonify({"error": "Name and email are required."}), 400

        created_at = datetime.utcnow().isoformat() + "Z"
        db = get_db()
        cursor = db.execute(
            "INSERT INTO contacts (name, email, phone, message, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, email, phone, message, created_at),
        )
        db.commit()

        return (
            jsonify(
                {
                    "id": cursor.lastrowid,
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "message": message,
                    "created_at": created_at,
                }
            ),
            201,
        )

    db = get_db()
    rows = db.execute("SELECT * FROM contacts ORDER BY id DESC").fetchall()
    return jsonify([dict(row) for row in rows])


@app.route("/api/contacts/<int:contact_id>", methods=["GET", "DELETE"])
def contact_detail(contact_id):
    db = get_db()
    row = db.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Contact not found."}), 404

    if request.method == "DELETE":
        db.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        db.commit()
        return jsonify({"deleted": contact_id})

    return jsonify(dict(row))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
