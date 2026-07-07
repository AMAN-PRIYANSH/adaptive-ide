# tests/test_engine.py  v2
"""
Unit tests for AbilityEngine v2 and Student.
Run: python -m pytest tests/ -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
from ability_engine import AbilityEngine
from student import Student
from models import Question
import config as cfg

U0 = cfg.UNCERTAINTY_INIT   # shorthand

# ── Fixtures ──────────────────────────────────────────────────────────
@pytest.fixture
def engine():
    return AbilityEngine(cfg)

def call_update(engine, ability=0.5, uncertainty=U0, difficulty=0.5,
                correct=True, hint_used=False, time_taken=30,
                estimated_time=30, questions_done=0,
                correct_streak=0, wrong_streak=0):
    return engine.update(
        ability=ability, uncertainty=uncertainty, difficulty=difficulty,
        correct=correct, hint_used=hint_used, time_taken=time_taken,
        estimated_time=estimated_time, questions_done=questions_done,
        correct_streak=correct_streak, wrong_streak=wrong_streak,
    )

# ── 3-PL IRT ─────────────────────────────────────────────────────────
def test_expected_probability_matched(engine):
    """At θ==b, P should be between c and 1 (above 0.5 due to guessing floor)."""
    P = engine.expected_probability(0.5, 0.5, cfg.IRT_DEFAULT_DISCRIMINATION, cfg.IRT_GUESSING_PARAM)
    assert 0.5 < P < 0.7   # c=0.20 → floor at 0.20, midpoint = 0.20+0.40=0.60

def test_expected_probability_easy(engine):
    P = engine.expected_probability(0.9, 0.1, cfg.IRT_DEFAULT_DISCRIMINATION, cfg.IRT_GUESSING_PARAM)
    assert P > 0.85

def test_guessing_floor(engine):
    """P should never fall below c even for worst-case student."""
    P = engine.expected_probability(0.0, 1.0, cfg.IRT_DEFAULT_DISCRIMINATION, cfg.IRT_GUESSING_PARAM)
    assert P >= cfg.IRT_GUESSING_PARAM - 0.01

# ── Ability updates ───────────────────────────────────────────────────
def test_correct_increases_ability(engine):
    r = call_update(engine, ability=0.5, difficulty=0.6, correct=True)
    assert r['ability_after'] > r['ability_before']

def test_wrong_decreases_ability(engine):
    r = call_update(engine, ability=0.5, difficulty=0.4, correct=False)
    assert r['ability_after'] < r['ability_before']

def test_hint_reduces_delta(engine):
    r_no  = call_update(engine, ability=0.5, difficulty=0.7, correct=True, hint_used=False)
    r_yes = call_update(engine, ability=0.5, difficulty=0.7, correct=True, hint_used=True)
    assert r_yes['delta'] < r_no['delta']

def test_ability_clipped_max(engine):
    r = call_update(engine, ability=cfg.ABILITY_MAX-0.001, difficulty=0.0, correct=True)
    assert r['ability_after'] <= cfg.ABILITY_MAX

def test_ability_clipped_min(engine):
    r = call_update(engine, ability=cfg.ABILITY_MIN+0.001, difficulty=1.0,
                    correct=False, time_taken=120)
    assert r['ability_after'] >= cfg.ABILITY_MIN

def test_learning_rate_decays(engine):
    r0  = call_update(engine, questions_done=0)
    r10 = call_update(engine, questions_done=10)
    assert r10['learning_rate'] < r0['learning_rate']

def test_fast_correct_boosts(engine):
    r_norm = call_update(engine, ability=0.5, difficulty=0.7, correct=True, time_taken=30, estimated_time=30)
    r_fast = call_update(engine, ability=0.5, difficulty=0.7, correct=True, time_taken=10, estimated_time=30)
    assert r_fast['delta'] >= r_norm['delta'] * 0.99

def test_slow_penalises(engine):
    r_norm = call_update(engine, ability=0.5, difficulty=0.7, correct=True, time_taken=30, estimated_time=30)
    r_slow = call_update(engine, ability=0.5, difficulty=0.7, correct=True, time_taken=90, estimated_time=30)
    assert r_slow['delta'] < r_norm['delta']

# ── Guess detection ───────────────────────────────────────────────────
def test_guess_detected_hard_fast_correct(engine):
    r = call_update(engine, ability=0.5, difficulty=0.8, correct=True,
                    time_taken=5, estimated_time=60)
    assert r['guess_detected'] == True
    # Surprise should be discounted
    assert abs(r['surprise_adj']) < abs(r['surprise'])

def test_guess_not_detected_easy(engine):
    r = call_update(engine, ability=0.5, difficulty=0.3, correct=True,
                    time_taken=5, estimated_time=60)
    assert r['guess_detected'] == False

def test_guess_not_detected_wrong(engine):
    r = call_update(engine, ability=0.5, difficulty=0.8, correct=False,
                    time_taken=5, estimated_time=60)
    assert r['guess_detected'] == False

# ── Streak modifier ───────────────────────────────────────────────────
def test_streak_boost_applied(engine):
    r_no_streak  = call_update(engine, correct=True, correct_streak=0)
    r_with_streak= call_update(engine, correct=True, correct_streak=cfg.STREAK_BOOST_START)
    assert r_with_streak['streak_modifier'] == cfg.STREAK_BOOST_FACTOR
    assert r_with_streak['delta'] > r_no_streak['delta']

# ── Uncertainty ───────────────────────────────────────────────────────
def test_uncertainty_decreases_normally(engine):
    r = call_update(engine, ability=0.5, difficulty=0.5, correct=True,
                    uncertainty=0.3)
    # Expected answer close to P → low surprise → σ should decrease
    assert r['uncertainty_after'] < r['uncertainty_before']

def test_uncertainty_never_below_min(engine):
    u = U0
    for _ in range(30):
        r = call_update(engine, uncertainty=u, correct=True, difficulty=0.5)
        u = r['uncertainty_after']
    assert u >= cfg.UNCERTAINTY_MIN

# ── Student ───────────────────────────────────────────────────────────
def test_student_init_range():
    for level, (lo, hi) in cfg.ABILITY_INIT.items():
        for _ in range(20):
            s = Student(level, "Python")
            assert lo <= s.ability <= hi

def test_student_streak_tracking():
    s = Student("Intermediate", "Python")
    s.record_answer("PY-0001", 0.4, True,  False, 20, 0.52, 0.28)
    s.record_answer("PY-0002", 0.5, True,  False, 25, 0.55, 0.25)
    assert s.correct_streak == 2
    assert s.wrong_streak   == 0
    s.record_answer("PY-0003", 0.5, False, False, 40, 0.50, 0.27)
    assert s.correct_streak == 0
    assert s.wrong_streak   == 1

def test_student_serialise_roundtrip():
    s1 = Student("Intermediate", "Python")
    s1.record_answer("PY-0001", 0.4, True, False, 25.0, 0.55, 0.27)
    s2 = Student.from_dict(s1.to_dict())
    assert s1.ability        == s2.ability
    assert s1.uncertainty    == s2.uncertainty
    assert s1.correct_streak == s2.correct_streak
    assert s1.answered_ids   == s2.answered_ids

def test_accuracy_calculation():
    s = Student("Intermediate","Python")
    s.record_answer("PY-0001", 0.3, True,  False, 20, 0.52, 0.28)
    s.record_answer("PY-0002", 0.4, False, False, 40, 0.48, 0.30)
    assert abs(s.accuracy - 0.5) < 0.001

def test_question_strips_answer():
    d = {"id":"PY-0001","subject":"Python","question":"Q","options":[],
         "correct_answer":"Secret","explanation":"","difficulty":0.5,
         "type":"direct","estimated_time":25}
    q = Question.from_dict(d)
    assert "correct_answer" not in q.to_dict(include_answer=False)
    assert q.to_dict(include_answer=True)["correct_answer"] == "Secret"

# ── Corrected threshold tests ─────────────────────────────────────────
def test_expected_probability_hard_corrected(engine):
    """With c=0.20, even worst-case P is ~0.33 not ~0.20 at (0.1, 0.9)."""
    P = engine.expected_probability(0.1, 0.9, cfg.IRT_DEFAULT_DISCRIMINATION, cfg.IRT_GUESSING_PARAM)
    # floor = c = 0.20, actual at (0.1,0.9) ≈ 0.334 — well above pure 1-PL
    assert cfg.IRT_GUESSING_PARAM <= P <= 0.40

def test_streak_penalty_hard_wrong(engine):
    """Streak penalty is meaningful on hard questions where surprise is large-negative."""
    # Hard question: diff=0.8, ability=0.5 → large negative surprise
    r_no  = call_update(engine, correct=False, difficulty=0.8, wrong_streak=0)
    r_yes = call_update(engine, correct=False, difficulty=0.8,
                        wrong_streak=cfg.STREAK_PENALTY_START)
    # streak_penalty_factor=0.90 → S_adj is 0.90 × S_time (less negative)
    # Δθ = α × S_adj → less negative → ability drops LESS
    assert r_yes['delta'] > r_no['delta']   # both negative, yes is closer to 0
