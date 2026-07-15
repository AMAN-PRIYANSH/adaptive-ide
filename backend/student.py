# student.py  v2
"""
Student — holds all per-session state including new v2 fields:
  - uncertainty (σ)
  - correct_streak / wrong_streak
"""

from __future__ import annotations
import random, time, uuid
from config import ABILITY_INIT, ABILITY_MIN, ABILITY_MAX, UNCERTAINTY_INIT


class Student:

    def __init__(self, level: str, subject: str):
        lo, hi = ABILITY_INIT[level]
        self.session_id:         str        = uuid.uuid4().hex
        self.ability:            float      = round(random.uniform(lo, hi), 4)
        self.uncertainty:        float      = UNCERTAINTY_INIT
        self.subject:            str        = subject
        self.level:              str        = level
        self.questions_done:     int        = 0
        self.correct:            int        = 0
        self.wrong:              int        = 0
        self.hints_used:         int        = 0
        self.correct_streak:     int        = 0
        self.wrong_streak:       int        = 0
        self.answered_ids:       list[str]  = []
        self.ability_history:    list[float]= [self.ability]
        self.uncertainty_history:list[float]= [self.uncertainty]
        self.difficulty_history: list[float]= []
        self.time_history:       list[float]= []
        self.score:              float      = 0.0
        self.start_ts:           float      = time.time()
        self.wrong_questions:    list[dict] = []

    # ------------------------------------------------------------------
    def record_answer(
        self,
        qid:         str,
        difficulty:  float,
        correct:     bool,
        hint_used:   bool,
        time_taken:  float,
        new_ability: float,
        new_uncertainty: float,
        question_text:  str = None,
        student_answer: str = None,
        correct_answer: str = None,
        explanation:    str = None,
        topic:          str = None,
    ):
        self.answered_ids.append(qid)
        self.difficulty_history.append(round(difficulty, 3))
        self.time_history.append(round(time_taken, 1))
        self.ability_history.append(round(new_ability, 4))
        self.uncertainty_history.append(round(new_uncertainty, 4))
        self.ability      = new_ability
        self.uncertainty  = new_uncertainty
        self.questions_done += 1

        if correct:
            self.correct       += 1
            self.correct_streak += 1
            self.wrong_streak   = 0
            self.score         += max(0.5, difficulty)
        else:
            self.wrong          += 1
            self.wrong_streak   += 1
            self.correct_streak  = 0
            self.wrong_questions.append({
                "question_text":  question_text,
                "student_answer": student_answer,
                "correct_answer": correct_answer,
                "explanation":    explanation,
                "difficulty":     difficulty,
                "topic":          topic,
            })

        if hint_used:
            self.hints_used += 1

    # ------------------------------------------------------------------
    @property
    def accuracy(self) -> float:
        if self.questions_done == 0:
            return 0.0
        return round(self.correct / self.questions_done, 4)

    @property
    def avg_time(self) -> float:
        if not self.time_history:
            return 0.0
        return round(sum(self.time_history) / len(self.time_history), 1)

    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "session_id":          self.session_id,
            "ability":             self.ability,
            "uncertainty":         self.uncertainty,
            "subject":             self.subject,
            "level":               self.level,
            "questions_done":      self.questions_done,
            "correct":             self.correct,
            "wrong":               self.wrong,
            "hints_used":          self.hints_used,
            "correct_streak":      self.correct_streak,
            "wrong_streak":        self.wrong_streak,
            "answered_ids":        self.answered_ids,
            "ability_history":     self.ability_history,
            "uncertainty_history": self.uncertainty_history,
            "difficulty_history":  self.difficulty_history,
            "time_history":        self.time_history,
            "score":               round(self.score, 2),
            "start_ts":            self.start_ts,
            "wrong_questions":     self.wrong_questions,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Student":
        s = cls.__new__(cls)
        s.session_id          = d.get("session_id") or uuid.uuid4().hex
        s.ability             = d["ability"]
        s.uncertainty         = d.get("uncertainty", UNCERTAINTY_INIT)
        s.subject             = d["subject"]
        s.level               = d["level"]
        s.questions_done      = d["questions_done"]
        s.correct             = d["correct"]
        s.wrong               = d["wrong"]
        s.hints_used          = d["hints_used"]
        s.correct_streak      = d.get("correct_streak", 0)
        s.wrong_streak        = d.get("wrong_streak", 0)
        s.answered_ids        = d["answered_ids"]
        s.ability_history     = d["ability_history"]
        s.uncertainty_history = d.get("uncertainty_history", [s.uncertainty])
        s.difficulty_history  = d["difficulty_history"]
        s.time_history        = d["time_history"]
        s.score               = d["score"]
        s.start_ts            = d["start_ts"]
        s.wrong_questions     = d.get("wrong_questions", [])
        return s
