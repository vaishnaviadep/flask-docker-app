import os
import time

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_conn():
    return psycopg2.connect(os.environ["DATABASE_URL"])


def init_db():
    for _ in range(10):
        try:
            with get_conn() as conn, conn.cursor() as cur:
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS tasks ("
                    "id SERIAL PRIMARY KEY, "
                    "title TEXT NOT NULL, "
                    "done BOOLEAN DEFAULT FALSE)"
                )
            return
        except psycopg2.OperationalError:
            time.sleep(2)
    raise RuntimeError("Database not reachable")


init_db()


@app.route("/")
def home():
    return jsonify(message="Task Manager API is running")


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/tasks", methods=["GET"])
def list_tasks():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, title, done FROM tasks ORDER BY id")
        rows = cur.fetchall()
    return jsonify([{"id": r[0], "title": r[1], "done": r[2]} for r in rows])


@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not title:
        return jsonify(error="title is required"), 400
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO tasks (title) VALUES (%s) RETURNING id", (title,))
        new_id = cur.fetchone()[0]
    return jsonify(id=new_id, title=title, done=False), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def toggle_task(task_id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE tasks SET done = NOT done WHERE id = %s RETURNING id, title, done",
            (task_id,),
        )
        row = cur.fetchone()
    if not row:
        return jsonify(error="not found"), 404
    return jsonify(id=row[0], title=row[1], done=row[2])


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        deleted = cur.rowcount
    if not deleted:
        return jsonify(error="not found"), 404
    return jsonify(message="deleted")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)