# app.py v2.2
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, session, request, jsonify, render_template
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

# ── Pages ──────────────────────────────────────────────────────────────
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

@app.route("/admin")
def admin_page():
    return render_template("admin.html")

# ── API ────────────────────────────────────────────────────────────────
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
    safe = {k: v for k, v in q.items() if k != "correct_answer"}
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
    cq         = session["current_question"]
    student_dict, result = qm.submit_answer(
        session["student"], cq["id"], answer, hint_used, time_taken
    )
    session["student"] = student_dict
    session.pop("current_question", None)
    return jsonify(result)

@app.route("/api/results", methods=["GET"])
def api_results():
    if "student" not in session:
        return jsonify({"error": "No active session"}), 400
    return jsonify(qm.get_results(session["student"]))

@app.route("/api/config", methods=["GET"])
def api_config():
    return jsonify({
        "quiz_length": cfg.QUIZ_LENGTH,
        "levels":      list(cfg.ABILITY_INIT.keys()),
        "subjects":    qm.bank.subjects(),
    })

@app.route("/api/admin/stats")
def api_admin_stats():
    from collections import Counter
    stats   = qm.logger.stats()
    entries = qm.logger.all_entries()
    buckets = {"0-20":0,"20-40":0,"40-60":0,"60-80":0,"80-100":0}
    for e in entries:
        a = e.get("ability_after", 0) * 100
        if   a < 20: buckets["0-20"]   += 1
        elif a < 40: buckets["20-40"]  += 1
        elif a < 60: buckets["40-60"]  += 1
        elif a < 80: buckets["60-80"]  += 1
        else:        buckets["80-100"] += 1
    qid_counts    = Counter(e["qid"] for e in entries if "qid" in e)
    top_questions = qid_counts.most_common(10)
    ability_series = [{"ts": e["ts"], "ability": e.get("ability_after", 0)}
                      for e in entries[-100:]]
    return jsonify({
        "stats":           stats,
        "ability_buckets": buckets,
        "top_questions":   [{"qid":q,"count":c} for q,c in top_questions],
        "ability_series":  ability_series,
    })

@app.route("/api/admin/log")
def api_admin_log():
    return jsonify(qm.logger.all_entries()[-200:])

# ── Entry point ────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    # debug=False in production (Render sets PORT env var)
    debug = os.environ.get("RENDER") is None
    app.run(host="0.0.0.0", port=port, debug=debug)
