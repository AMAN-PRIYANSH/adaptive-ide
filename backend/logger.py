# logger.py v3 — Supabase + local file fallback
"""
Logger writes to two places simultaneously:
  1. Supabase PostgreSQL (primary — survives server restarts on Render)
  2. Local JSONL file    (fallback — works when running locally)

If SUPABASE_URL and SUPABASE_KEY are not set, silently falls back to
local file only. So the app works identically on localhost without any
environment variables.

Supabase table schema (run this SQL in Supabase dashboard once):

    create table quiz_attempts (
        id            bigserial primary key,
        ts            text,
        qid           text,
        difficulty    float,
        ability_before float,
        ability_after  float,
        correct       int,
        time_taken    float,
        hint_used     int,
        delta         float,
        expected_p    float,
        discrimination float,
        guessing_param float,
        surprise      float,
        surprise_adj  float,
        guess_detected boolean,
        hint_modifier float,
        time_modifier float,
        time_ratio    float,
        streak_modifier float,
        learning_rate float,
        uncertainty_before float,
        uncertainty_after  float
    );
"""

from __future__ import annotations
import json, os, time, threading

# ── Supabase client (optional) ─────────────────────────────────────────
_supabase = None
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[Logger] Supabase connected ✓")
    except Exception as e:
        print(f"[Logger] Supabase init failed: {e} — using local file only")
else:
    print("[Logger] No Supabase credentials — using local file only")


class Logger:

    def __init__(self, log_path: str = None):
        if log_path is None:
            base = os.path.dirname(os.path.abspath(__file__))
            log_path = os.path.join(base, "data", "session_log.jsonl")
        self._path = log_path
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(self._path), exist_ok=True)

    # ------------------------------------------------------------------
    def log(self, qid, difficulty, ability_before, ability_after,
            correct, time_taken, hint_used, update_detail):

        entry = {
            "ts":             time.strftime("%Y-%m-%dT%H:%M:%S"),
            "qid":            qid,
            "difficulty":     difficulty,
            "ability_before": ability_before,
            "ability_after":  ability_after,
            "correct":        int(correct),
            "time_taken":     time_taken,
            "hint_used":      int(hint_used),
            **update_detail,
        }

        # Write local file (always)
        self._write_local(entry)

        # Write Supabase (if connected) — in background thread so it
        # never slows down the HTTP response
        if _supabase:
            threading.Thread(
                target=self._write_supabase,
                args=(entry,),
                daemon=True
            ).start()

    # ------------------------------------------------------------------
    def _write_local(self, entry: dict):
        line = json.dumps(entry, default=str) + "\n"
        with self._lock:
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(line)

    def _write_supabase(self, entry: dict):
        try:
            # Supabase doesn't accept extra fields — only send known columns
            row = {k: v for k, v in entry.items()
                   if k in {
                       "ts","qid","difficulty","ability_before","ability_after",
                       "correct","time_taken","hint_used","delta","expected_p",
                       "discrimination","guessing_param","surprise","surprise_adj",
                       "guess_detected","hint_modifier","time_modifier","time_ratio",
                       "streak_modifier","learning_rate","uncertainty_before",
                       "uncertainty_after"
                   }}
            _supabase.table("quiz_attempts").insert(row).execute()
        except Exception as e:
            print(f"[Logger] Supabase write failed: {e}")

    # ------------------------------------------------------------------
    def all_entries(self) -> list[dict]:
        """Read from Supabase if available, else local file."""
        if _supabase:
            try:
                res = _supabase.table("quiz_attempts")\
                               .select("*")\
                               .order("id", desc=False)\
                               .execute()
                return res.data
            except Exception as e:
                print(f"[Logger] Supabase read failed: {e}")

        # Fallback to local
        entries = []
        if not os.path.exists(self._path):
            return entries
        with open(self._path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except:
                        pass
        return entries

    def stats(self) -> dict:
        entries = self.all_entries()
        if not entries:
            return {"total": 0}
        correct  = sum(1 for e in entries if e.get("correct"))
        guessed  = sum(1 for e in entries if e.get("guess_detected"))
        hinted   = sum(1 for e in entries if e.get("hint_used"))
        avg_time = sum(e.get("time_taken", 0) for e in entries) / len(entries)
        return {
            "total":    len(entries),
            "correct":  correct,
            "accuracy": round(correct / len(entries), 3),
            "guesses":  guessed,
            "hints":    hinted,
            "avg_time": round(avg_time, 1),
        }
