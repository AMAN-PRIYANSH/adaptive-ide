# app.py
"""
Flask application entry point.
All routes are thin — logic lives in QuizManager.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from flask import (
    Flask, session, request, jsonify,
    render_template, send_from_directory
)
import config as cfg
from quiz_manager import QuizManager

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static",
)
app.secret_key = cfg.SECRET_KEY
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

qm = QuizManager()


# ──────────────────────────────────────────────────────────────────────
# Pages
# ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", subjects=qm.bank.subjects())


@app.route("/quiz")
def quiz_page():
    if "student" not in session:
        return render_template("index.html", subjects=qm.bank.subjects(), error="Start a quiz first.")
    return render_template("quiz.html")


@app.route("/result")
def result_page():
    if "student" not in session:
        return render_template("index.html", subjects=qm.bank.subjects())
    results = qm.get_results(session["student"])
    session.pop("student", None)
    return render_template("result.html", results=results)


# ──────────────────────────────────────────────────────────────────────
# API
# ──────────────────────────────────────────────────────────────────────

@app.route("/api/start", methods=["POST"])
def api_start():
    data    = request.get_json(force=True)
    level   = data.get("level")
    subject = data.get("subject")

    if level not in cfg.ABILITY_INIT:
        return jsonify({"error": f"Invalid level: {level}"}), 400
    if subject not in qm.bank.subjects():
        return jsonify({"error": f"Invalid subject: {subject}"}), 400

    session["student"] = qm.start_quiz(level, subject)
    return jsonify({"ok": True, "ability": session["student"]["ability"]})


@app.route("/api/next", methods=["GET"])
def api_next():
    if "student" not in session:
        return jsonify({"error": "No active session"}), 400

    q = qm.next_question(session["student"])
    if q is None:
        return jsonify({"done": True})

    # Strip correct_answer before sending to client
    safe = {k: v for k, v in q.items() if k != "correct_answer"}
    # Store current question server-side so client cannot tamper with the answer
    session["current_question"] = q
    return jsonify(safe)


@app.route("/api/submit", methods=["POST"])
def api_submit():
    if "student" not in session or "current_question" not in session:
        return jsonify({"error": "No active session"}), 400

    data       = request.get_json(force=True)
    answer     = data.get("answer", "").strip()
    hint_used  = bool(data.get("hint_used", False))
    time_taken = float(data.get("time_taken", 30))

    cq = session["current_question"]

    student_dict, result = qm.submit_answer(
        student_dict  = session["student"],
        qid           = cq["id"],
        answer_given  = answer,
        hint_used     = hint_used,
        time_taken    = time_taken,
    )

    session["student"] = student_dict
    session.pop("current_question", None)
    return jsonify(result)


@app.route("/api/results", methods=["GET"])
def api_results():
    if "student" not in session:
        return jsonify({"error": "No active session"}), 400
    results = qm.get_results(session["student"])
    return jsonify(results)


@app.route("/api/config", methods=["GET"])
def api_config():
    """Expose safe config values to the frontend."""
    return jsonify({
        "quiz_length":      cfg.QUIZ_LENGTH,
        "fullscreen":       cfg.FULLSCREEN_ON_START,
        "levels":           list(cfg.ABILITY_INIT.keys()),
        "subjects":         qm.bank.subjects(),
    })


if __name__ == "__main__":
    app.run(debug=True, port=5050)
