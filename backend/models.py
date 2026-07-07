# models.py  v2
from __future__ import annotations
import json, os, random
from dataclasses import dataclass
from typing import Optional


@dataclass
class Question:
    id:             str
    subject:        str
    question:       str
    options:        list
    correct_answer: str
    explanation:    str
    difficulty:     float
    type:           str   = "direct"
    estimated_time: int   = 30
    hint:           str   = "💡 You can do it! 🔥"
    discrimination: float = None   # 2-PL a parameter; None = use global k
    guessing_param: float = None   # 3-PL c parameter; None = use global c
    needs_code:     bool  = False
    topic:          str   = ""

    @classmethod
    def from_dict(cls, d: dict) -> "Question":
        return cls(
            id             = d["id"],
            subject        = d["subject"],
            question       = d["question"],
            options        = d.get("options", []),
            correct_answer = d["correct_answer"],
            explanation    = d.get("explanation", ""),
            difficulty     = float(d.get("difficulty", 0.50)),
            type           = d.get("type", "direct"),
            estimated_time = int(d.get("estimated_time", 30)),
            hint           = d.get("hint", "💡 You can do it! 🔥"),
            discrimination = d.get("discrimination", None),
            guessing_param = d.get("guessing_param", None),
            needs_code     = bool(d.get("needs_code", False)),
            topic          = d.get("topic", ""),
        )

    def to_dict(self, include_answer: bool = False) -> dict:
        d = {
            "id":             self.id,
            "subject":        self.subject,
            "question":       self.question,
            "options":        self.options,
            "explanation":    self.explanation,
            "difficulty":     self.difficulty,
            "type":           self.type,
            "estimated_time": self.estimated_time,
            "hint":           self.hint,
        }
        if include_answer:
            d["correct_answer"] = self.correct_answer
        return d


class QuestionBank:

    def __init__(self, data_dir: str, question_files: dict):
        self._bank: dict[str, list[Question]] = {}
        for subject, filename in question_files.items():
            path = os.path.join(data_dir, filename)
            if not os.path.exists(path):
                print(f"[QuestionBank] WARNING: {path} not found")
                self._bank[subject] = []
                continue
            with open(path, encoding="utf-8") as f:
                raw = json.load(f)
            # Filter out incomplete questions
            all_q  = [Question.from_dict(q) for q in raw]
            valid  = [q for q in all_q if not q.needs_code]
            skipped= len(all_q) - len(valid)
            self._bank[subject] = valid
            print(f"[QuestionBank] '{subject}': {len(valid)} ready"
                  + (f" ({skipped} skipped — needs_code)" if skipped else ""))

    def subjects(self) -> list:
        return list(self._bank.keys())

    def get_by_id(self, qid: str) -> Optional[Question]:
        for qs in self._bank.values():
            for q in qs:
                if q.id == qid:
                    return q
        return None

    def get_in_window(self, subject, ability, window, exclude_ids) -> Optional[Question]:
        candidates = [
            q for q in self._bank.get(subject, [])
            if q.id not in exclude_ids
            and abs(q.difficulty - ability) <= window
        ]
        return random.choice(candidates) if candidates else None

    def get_nearest(self, subject, ability, exclude_ids) -> Optional[Question]:
        pool = [q for q in self._bank.get(subject, []) if q.id not in exclude_ids]
        if not pool:
            return None
        return min(pool, key=lambda q: abs(q.difficulty - ability))

    def total_for_subject(self, subject: str) -> int:
        return len(self._bank.get(subject, []))
