# quiz_manager.py  v2
"""
QuizManager — orchestrates QuestionBank, AbilityEngine, Student, Logger.
Updated for v2: passes uncertainty + streak fields to engine.
"""

from __future__ import annotations
import random
from typing import Optional

import config as cfg
from models         import QuestionBank, Question
from ability_engine import AbilityEngine
from student        import Student
from logger         import Logger


class QuizManager:

    def __init__(self):
        self.bank   = QuestionBank(cfg.DATA_DIR, cfg.QUESTION_FILES)
        self.engine = AbilityEngine(cfg)
        self.logger = Logger()

    # ------------------------------------------------------------------
    def start_quiz(self, level: str, subject: str) -> dict:
        return Student(level, subject).to_dict()

    # ------------------------------------------------------------------
    def next_question(self, student_dict: dict) -> Optional[dict]:
        student = Student.from_dict(student_dict)
        if student.questions_done >= cfg.QUIZ_LENGTH[student.subject]:
            return None

        exclude = set(student.answered_ids)
        ability = student.ability
        subject = student.subject

        q: Optional[Question] = None
        window = cfg.DIFFICULTY_WINDOW_INIT
        while window <= cfg.DIFFICULTY_WINDOW_MAX:
            q = self.bank.get_in_window(subject, ability, window, exclude)
            if q:
                break
            window += cfg.DIFFICULTY_WINDOW_STEP

        if q is None:
            q = self.bank.get_nearest(subject, ability, exclude)
        if q is None:
            return None

        options = list(q.options)
        correct = q.correct_answer
        if cfg.RANDOMIZE_OPTIONS:
            random.shuffle(options)

        return {
            "id":              q.id,
            "question":        q.question,
            "options":         options,
            "correct_answer":  correct,
            "explanation":     q.explanation,
            "hint":            getattr(q, 'hint', '💡 You can do it! 🔥'),
            "difficulty":      q.difficulty,
            "type":            q.type,
            "estimated_time":  q.estimated_time,
            "discrimination":  getattr(q, 'discrimination', None),
            "question_number": student.questions_done + 1,
            "total_questions": cfg.QUIZ_LENGTH[student.subject],
        }

    # ------------------------------------------------------------------
    def submit_answer(
        self,
        student_dict:  dict,
        qid:           str,
        answer_given:  str,
        hint_used:     bool,
        time_taken:    float,
    ) -> tuple[dict, dict]:

        student  = Student.from_dict(student_dict)
        question = self.bank.get_by_id(qid)
        if question is None:
            raise ValueError(f"Unknown question id: {qid}")

        correct = (answer_given.strip().lower() ==
                   question.correct_answer.strip().lower())

        update = self.engine.update(
            ability         = student.ability,
            uncertainty     = student.uncertainty,
            difficulty      = question.difficulty,
            correct         = correct,
            hint_used       = hint_used,
            time_taken      = time_taken,
            estimated_time  = question.estimated_time,
            questions_done  = student.questions_done,
            correct_streak  = student.correct_streak,
            wrong_streak    = student.wrong_streak,
            discrimination  = getattr(question, 'discrimination', None),
            guessing_param  = getattr(question, 'guessing_param', None),
            question_type   = question.type,
        )

        student.record_answer(
            qid             = qid,
            difficulty      = question.difficulty,
            correct         = correct,
            hint_used       = hint_used,
            time_taken      = time_taken,
            new_ability     = update["ability_after"],
            new_uncertainty = update["uncertainty_after"],
        )

        self.logger.log(
            qid            = qid,
            difficulty     = question.difficulty,
            ability_before = update["ability_before"],
            ability_after  = update["ability_after"],
            correct        = correct,
            time_taken     = time_taken,
            hint_used      = hint_used,
            update_detail  = update,
        )

        result = {
            "correct":          correct,
            "correct_answer":   question.correct_answer,
            "explanation":      question.explanation,
            "ability_before":   update["ability_before"],
            "ability_after":    update["ability_after"],
            "delta":            update["delta"],
            "expected_p":       update["expected_p"],
            "uncertainty":      update["uncertainty_after"],
            "questions_done":   student.questions_done,
            "total_questions":  cfg.QUIZ_LENGTH[student.subject],
            "dev": {
                "surprise":          update["surprise"],
                "surprise_adj":      update["surprise_adj"],
                "learning_rate":     update["learning_rate"],
                "hint_modifier":     update["hint_modifier"],
                "time_modifier":     update["time_modifier"],
                "time_ratio":        update["time_ratio"],
                "streak_modifier":   update["streak_modifier"],
                "guess_detected":    update["guess_detected"],
                "uncertainty_before":update["uncertainty_before"],
                "uncertainty_after": update["uncertainty_after"],
                "discrimination":    update["discrimination"],
                "guessing_param":    update["guessing_param"],
                "question_type":     question.type,
                "boundary_factor":   update["boundary_factor"],
                "estimated_time":    question.estimated_time,
                "correct_streak":    student.correct_streak,
                "wrong_streak":      student.wrong_streak,
            }
        }

        return student.to_dict(), result

    # ------------------------------------------------------------------
    def get_results(self, student_dict: dict) -> dict:
        student = Student.from_dict(student_dict)
        return {
            "subject":             student.subject,
            "level":               student.level,
            "final_ability":       student.ability,
            "final_uncertainty":   student.uncertainty,
            "accuracy":            student.accuracy,
            "correct":             student.correct,
            "wrong":               student.wrong,
            "total":               student.questions_done,
            "hints_used":          student.hints_used,
            "avg_time":            student.avg_time,
            "score":               student.score,
            "ability_history":     student.ability_history,
            "uncertainty_history": student.uncertainty_history,
            "difficulty_history":  student.difficulty_history,
            "time_history":        student.time_history,
        }
