"""
simulate.py — Synthetic Student Simulator
==========================================
Generates realistic student quiz sessions using the actual AbilityEngine v2.
Output: data/synthetic_sessions.jsonl  (one attempt per line = ML training row)

Academic justification:
    Synthetic data generation via IRT response models is an established
    bootstrapping technique in CAT research when real student data is
    unavailable (van der Linden & Glas, 2010; Embretson & Reise, 2000).
    The response model P(correct | theta_true, b, a, c) is identical to
    the engine's own probability formula — making the simulation
    internally consistent.
"""

import sys, os, random, json, time, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import config as cfg
from ability_engine import AbilityEngine
from models import QuestionBank
from student import Student

# ── Simulation config ─────────────────────────────────────────────────
PERSONAS = [
    ("Beginner",     (0.10, 0.28),  60),
    ("Intermediate", (0.35, 0.65),  80),
    ("Advanced",     (0.68, 0.90),  60),
]
QUESTIONS_PER_SESSION = 15
SUBJECT = "Python"
RANDOM_SEED = 42

SPEED_FACTOR = {"Beginner": 1.40, "Intermediate": 1.00, "Advanced": 0.65}
TIME_STD_FACTOR = 0.25
HINT_PROB = {"Beginner": 0.25, "Intermediate": 0.10, "Advanced": 0.03}

random.seed(RANDOM_SEED)
engine = AbilityEngine(cfg)
bank   = QuestionBank(cfg.DATA_DIR, cfg.QUESTION_FILES)

OUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'synthetic_sessions.jsonl')

def simulate_correct(true_ability, question):
    a = question.discrimination if question.discrimination else cfg.IRT_DEFAULT_DISCRIMINATION
    c = question.guessing_param if question.guessing_param else cfg.IRT_GUESSING_PARAM
    P = engine.expected_probability(true_ability, question.difficulty, a, c)
    return random.random() < P, P

def simulate_time(estimated_time, level, correct):
    speed = SPEED_FACTOR[level] * (1.20 if not correct else 1.0)
    t = random.gauss(estimated_time * speed, estimated_time * TIME_STD_FACTOR)
    return max(3.0, min(t, estimated_time * 4.0))

def simulate_hint(level, true_ability, difficulty):
    base = HINT_PROB[level]
    gap  = max(0, difficulty - true_ability)
    return random.random() < min(base + gap * 0.20, 0.50)

def select_question(ability, answered_ids, window=None):
    if window is None: window = cfg.DIFFICULTY_WINDOW_INIT
    exclude = set(answered_ids)
    q = bank.get_in_window(SUBJECT, ability, window, exclude)
    if q is None and window < cfg.DIFFICULTY_WINDOW_MAX:
        return select_question(ability, answered_ids, window + cfg.DIFFICULTY_WINDOW_STEP)
    return q or bank.get_nearest(SUBJECT, ability, exclude)

all_rows = []
summaries = []
session_id = 0

print(f"Simulating {sum(p[2] for p in PERSONAS)} students x {QUESTIONS_PER_SESSION} questions\n")

for level, (lo, hi), n_students in PERSONAS:
    print(f"  {level} ({n_students} students)...", end=" ", flush=True)
    lc = lt = 0

    for _ in range(n_students):
        true_theta  = random.uniform(lo, hi)
        session_id += 1
        student     = Student(level, SUBJECT)
        answered    = []
        c_streak = w_streak = 0

        for q_num in range(QUESTIONS_PER_SESSION):
            q = select_question(student.ability, answered)
            if q is None: break

            correct, true_P = simulate_correct(true_theta, q)
            hint_used  = simulate_hint(level, true_theta, q.difficulty)
            time_taken = simulate_time(q.estimated_time, level, correct)

            result = engine.update(
                ability=student.ability, uncertainty=student.uncertainty,
                difficulty=q.difficulty, correct=correct,
                hint_used=hint_used, time_taken=time_taken,
                estimated_time=q.estimated_time,
                questions_done=student.questions_done,
                correct_streak=c_streak, wrong_streak=w_streak,
                discrimination=q.discrimination, guessing_param=q.guessing_param,
                question_type=q.type,
            )

            all_rows.append({
                "session_id": session_id, "level": level,
                "true_ability": round(true_theta, 4), "q_num": q_num + 1,
                "qid": q.id, "difficulty": q.difficulty,
                "q_type": q.type, "estimated_time": q.estimated_time,
                "discrimination": result["discrimination"],
                "guessing_param": result["guessing_param"],
                "ability_before": result["ability_before"],
                "uncertainty_before": result["uncertainty_before"],
                "correct_streak": c_streak, "wrong_streak": w_streak,
                "questions_done": student.questions_done,
                "expected_p": result["expected_p"],
                "time_ratio": round(time_taken / q.estimated_time, 4),
                "hint_used": int(hint_used),
                "guess_detected": int(result["guess_detected"]),
                "surprise": result["surprise"],
                "learning_rate": result["learning_rate"],
                "streak_modifier": result["streak_modifier"],
                "time_modifier": result["time_modifier"],
                "hint_modifier": result["hint_modifier"],
                "ability_after": result["ability_after"],
                "uncertainty_after": result["uncertainty_after"],
                "delta": result["delta"],
                "correct": int(correct),
                "true_P": round(true_P, 4),
            })

            answered.append(q.id)
            if correct: c_streak += 1; w_streak = 0
            else:       w_streak += 1; c_streak = 0

            student.record_answer(q.id, q.difficulty, correct, hint_used,
                                  time_taken, result["ability_after"],
                                  result["uncertainty_after"])
            lc += int(correct); lt += 1

        summaries.append({
            "session_id": session_id, "level": level,
            "true_ability": round(true_theta, 4),
            "final_theta":  round(student.ability, 4),
            "accuracy":     round(student.accuracy, 3),
            "theta_error":  round(abs(student.ability - true_theta), 4),
        })

    print(f"accuracy={lc/lt:.1%}")

with open(OUT_FILE, 'w') as f:
    for row in all_rows:
        f.write(json.dumps(row) + '\n')

errors = [s["theta_error"] for s in summaries]
print(f"\nTotal rows : {len(all_rows)}")
print(f"Sessions   : {session_id}")
print(f"\nAbility estimation (|estimated - true|):")
print(f"  Mean : {sum(errors)/len(errors):.4f}")
print(f"  Max  : {max(errors):.4f}")

for level, _, _ in PERSONAS:
    lvl = [s for s in summaries if s["level"] == level]
    avg_e = sum(s["theta_error"] for s in lvl) / len(lvl)
    avg_a = sum(s["accuracy"]    for s in lvl) / len(lvl)
    print(f"  {level:13s}: error={avg_e:.4f}  accuracy={avg_a:.1%}")

print(f"\nOutput: {OUT_FILE}")
