# logger.py v3.1 — lazy Supabase init (fixes Render env var timing)
"""
Logger writes to Supabase PostgreSQL + local JSONL fallback.
Supabase client is initialised lazily on first write — this ensures
env vars are available even if the module is imported before they're set.
"""

from __future__ import annotations
import json, os, time, threading

_supabase       = None
_supabase_ready = False
_supabase_tried = False


def _get_supabase():
    """Lazy init — called on first log() call, not at import time."""
    global _supabase, _supabase_ready, _supabase_tried
    if _supabase_tried:
        return _supabase

    _supabase_tried = True
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_KEY", "").strip()

    if not url or not key:
        print("[Logger] No Supabase credentials — local file only")
        return None

    try:
        from supabase import create_client
        _supabase = create_client(url, key)
        _supabase_ready = True
        print(f"[Logger] Supabase connected ✓ ({url[:40]}...)")
    except Exception as e:
        print(f"[Logger] Supabase init failed: {e}")
        _supabase = None

    return _supabase


class Logger:

    def __init__(self, log_path: str = None):
        if log_path is None:
            base     = os.path.dirname(os.path.abspath(__file__))
            log_path = os.path.join(base, "data", "session_log.jsonl")
        self._path = log_path
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(self._path), exist_ok=True)

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

        self._write_local(entry)

        sb = _get_supabase()
        if sb:
            threading.Thread(
                target=self._write_supabase,
                args=(sb, entry),
                daemon=True
            ).start()

    def _write_local(self, entry: dict):
        line = json.dumps(entry, default=str) + "\n"
        with self._lock:
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(line)

    def _write_supabase(self, sb, entry: dict):
        COLS = {
            "ts","qid","difficulty","ability_before","ability_after",
            "correct","time_taken","hint_used","delta","expected_p",
            "discrimination","guessing_param","surprise","surprise_adj",
            "guess_detected","hint_modifier","time_modifier","time_ratio",
            "streak_modifier","learning_rate","uncertainty_before","uncertainty_after"
        }
        try:
            row = {k: v for k, v in entry.items() if k in COLS}
            sb.table("quiz_attempts").insert(row).execute()
        except Exception as e:
            print(f"[Logger] Supabase write failed: {e}")

    def all_entries(self) -> list[dict]:
        sb = _get_supabase()
        if sb:
            try:
                res = sb.table("quiz_attempts")\
                        .select("*")\
                        .order("id", desc=False)\
                        .execute()
                return res.data
            except Exception as e:
                print(f"[Logger] Supabase read failed: {e}")

        entries = []
        if not os.path.exists(self._path):
            return entries
        with open(self._path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try: entries.append(json.loads(line))
                    except: pass
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
