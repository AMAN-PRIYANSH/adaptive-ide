# logger.py
"""
Logger
======
Records every quiz attempt in memory. Designed so that swapping to a
real database (SQLite, PostgreSQL) requires only replacing the _persist()
method — the public interface stays identical.

Future ML note: each log entry is one training sample. When you train a
model to replace the heuristic engine, load these entries directly as
feature vectors (ability_before, difficulty, hint_used, time_ratio, …)
with label = correct.
"""

from __future__ import annotations
import time
from typing import Any


class Logger:

    def __init__(self):
        # In-memory store. Replace with DB session in a future version.
        self._log: list[dict] = []

    def log(
        self,
        qid:            str,
        difficulty:     float,
        ability_before: float,
        ability_after:  float,
        correct:        bool,
        time_taken:     float,
        hint_used:      bool,
        update_detail:  dict,
    ):
        entry = {
            "timestamp":      time.strftime("%Y-%m-%dT%H:%M:%S"),
            "qid":            qid,
            "difficulty":     difficulty,
            "ability_before": ability_before,
            "ability_after":  ability_after,
            "correct":        correct,
            "time_taken":     time_taken,
            "hint_used":      hint_used,
            **update_detail,  # all intermediate engine values
        }
        self._persist(entry)

    def _persist(self, entry: dict):
        """Override this method to write to a real database."""
        self._log.append(entry)

    def all_entries(self) -> list[dict]:
        return list(self._log)

    def last_n(self, n: int) -> list[dict]:
        return self._log[-n:]
