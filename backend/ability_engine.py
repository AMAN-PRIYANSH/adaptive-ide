# ability_engine.py  — v2 (final pre-ML freeze)
"""
AbilityEngine v2
================
Four additions over v1, chosen after academic review:

  A. 2-PL IRT (per-question discrimination parameter a)
  B. 3-PL IRT (guessing parameter c)
  C. Ability uncertainty / confidence tracking (σ)
  D. Streak modelling
  E. Guess detection via response time

Everything else evaluated and deliberately excluded — see DESIGN_DECISIONS
at the bottom of this file.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FULL MATHEMATICAL PIPELINE  (v2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1 — Expected Probability  (3-PL IRT)
------------------------------------------
Classical 1-PL (Rasch): P = σ(k·(θ−b))
2-PL adds per-item discrimination a:
    P = σ(a·(θ−b))   where σ(x) = 1/(1+e^−x)

3-PL adds a guessing floor c:
    P = c + (1−c) · σ(a·(θ−b))

Interpretation:
  c = 0.20 means even a student with θ→−∞ still has a 20 % chance
  of answering correctly by guessing (4-option MCQ → theoretical 0.25).

  When a question has a field "discrimination" in its JSON, that value
  is used as a. Otherwise the global IRT_K is used.

STEP 2 — Answer Encoding
--------------------------
    A = 1 if correct else 0

STEP 3 — Raw Surprise  (prediction error)
------------------------------------------
    S = A − P

  Identical to the gradient of the log-likelihood in IRT — this IS
  online EM on the IRT model parameters.

STEP 4 — Guess Detection
--------------------------
If the question is hard  (difficulty > GUESS_HARD_THRESHOLD)
AND the student answered suspiciously fast (time_ratio < GUESS_TIME_THRESHOLD)
AND the answer was correct:
    S_guess = S × GUESS_DISCOUNT   (discount the positive surprise)

This prevents a lucky fast guess on a hard question from inflating ability.

STEP 5 — Hint Adjustment
--------------------------
    if hint_used and S > 0:
        S_hint = S × (1 − HINT_PENALTY)
    else:
        S_hint = S

STEP 6 — Time Modifier
------------------------
    τ = time_taken / estimated_time

    if τ < FAST_THRESHOLD and S > 0:
        time_mod = 1 + FAST_BONUS         # fast + correct → boost
    elif τ > SLOW_THRESHOLD:
        time_mod = 1 − SLOW_PENALTY       # very slow → mild penalty
    else:
        time_mod = 1.0

    S_time = S_hint × time_mod

STEP 7 — Streak Modifier
--------------------------
Consecutive correct answers suggest genuine mastery; consecutive wrong
answers suggest the student is stuck.

    if correct_streak >= STREAK_BOOST_START and S_time > 0:
        S_streak = S_time × STREAK_BOOST_FACTOR      (e.g. ×1.10)
    elif wrong_streak >= STREAK_PENALTY_START and S_time < 0:
        S_streak = S_time × STREAK_PENALTY_FACTOR    (e.g. ×0.90 → more negative)
    else:
        S_streak = S_time

    S_adj = S_streak   (final adjusted surprise)

STEP 8 — Decaying Learning Rate
---------------------------------
    α_n = α₀ × decay^n   where n = questions answered so far

    Early questions → large α (fast convergence from cold start).
    Later questions → small α (stable estimate).

STEP 9 — Ability Delta
------------------------
    Δθ = α_n × S_adj

STEP 10 — Ability Update
--------------------------
    θ_new = clip(θ + Δθ,  ABILITY_MIN,  ABILITY_MAX)

STEP 11 — Uncertainty Update  (σ)
----------------------------------
σ represents how confident we are in θ.  It starts high and decays
with each question answered.  High-surprise answers (we were very wrong)
slow the decay — a surprising outcome means our current θ estimate
might be incorrect and needs more evidence.

    surprise_magnitude = |S|        (0 to 1)
    σ_new = max(
        UNCERTAINTY_MIN,
        σ × UNCERTAINTY_DECAY + surprise_magnitude × UNCERTAINTY_SURPRISE_BOOST
    )

Note: σ decays toward UNCERTAINTY_MIN as evidence accumulates, but each
surprising answer pushes it back up slightly.  This is analogous to the
posterior variance in Bayesian estimation without the full Bayesian machinery.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESIGN DECISIONS — what was NOT added and why
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Topic-wise abilities     → FUTURE WORK.  Requires topic taxonomy on every
                           question (partially done via "topic" field from
                           sanfoundry). With only 177 Python questions the
                           per-topic sample size would be too small to
                           produce stable estimates. Add after the ML layer.

Bayesian ability (full)  → EXCLUDED.  Full Bayesian IRT (MCMC / EM) requires
                           a prior corpus of student response data to fit the
                           item parameters.  We have no such data yet.
                           Our σ-tracking is a lightweight proxy that gives
                           the same benefit to the UI without the complexity.

Forgetting curve         → EXCLUDED.  Forgetting (Ebbinghaus) requires
                           inter-session time gaps.  We have no persistence;
                           every session is fresh.  Add when login is added.

RL for question selection → FUTURE WORK.  The current windowed selector is
                           the hand-coded policy.  The ML layer will replace
                           this with a learned policy (DQN or contextual bandit).

Knowledge graph          → FUTURE WORK.  Needs a hand-curated prerequisite
                           graph per subject.  Valuable but out of scope for
                           this frozen engine version.

Difficulty weighting     → ALREADY HANDLED.  The IRT logistic already weights
                           by difficulty via (θ−b). A separate weight on top
                           would double-count.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ML HANDOFF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Every update() call returns UpdateResult — a flat dict of all signals.
This is your training feature vector.  Fields:
  ability_before, ability_after, delta, expected_p, surprise,
  surprise_adj, learning_rate, hint_modifier, time_modifier, time_ratio,
  guess_detected, streak_modifier, uncertainty_before, uncertainty_after,
  discrimination, guessing_param
The target label for supervised learning: correct (bool).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import math
from typing import TypedDict


class UpdateResult(TypedDict):
    # Core
    ability_before:     float
    ability_after:      float
    delta:              float
    # IRT
    expected_p:         float
    discrimination:     float
    guessing_param:     float
    # Surprise chain
    surprise:           float
    surprise_adj:       float
    guess_detected:     bool
    # Modifiers
    hint_modifier:      float
    time_modifier:      float
    time_ratio:         float
    streak_modifier:    float
    # Learning rate
    learning_rate:      float
    # Uncertainty
    uncertainty_before: float
    uncertainty_after:  float


class AbilityEngine:

    def __init__(self, cfg):
        self.k_default    = cfg.IRT_DEFAULT_DISCRIMINATION
        self.c_default    = cfg.IRT_GUESSING_PARAM
        self.alpha0       = cfg.LEARNING_RATE_BASE
        self.decay        = cfg.LEARNING_RATE_DECAY
        self.hint_penalty = cfg.HINT_PENALTY
        self.fast_thr     = cfg.TIME_FAST_THRESHOLD
        self.slow_thr     = cfg.TIME_SLOW_THRESHOLD
        self.fast_bonus   = cfg.TIME_FAST_BONUS
        self.slow_penalty = cfg.TIME_SLOW_PENALTY
        self.ability_min  = cfg.ABILITY_MIN
        self.ability_max  = cfg.ABILITY_MAX
        # Uncertainty
        self.u_decay      = cfg.UNCERTAINTY_DECAY
        self.u_min        = cfg.UNCERTAINTY_MIN
        self.u_surp_boost = cfg.UNCERTAINTY_SURPRISE_BOOST
        # Streak
        self.streak_boost_start   = cfg.STREAK_BOOST_START
        self.streak_boost_factor  = cfg.STREAK_BOOST_FACTOR
        self.streak_penalty_start = cfg.STREAK_PENALTY_START
        self.streak_penalty_factor= cfg.STREAK_PENALTY_FACTOR
        # Guess detection
        self.guess_hard_thr  = cfg.GUESS_HARD_THRESHOLD
        self.guess_time_thr  = cfg.GUESS_TIME_THRESHOLD
        self.guess_discount  = cfg.GUESS_DISCOUNT

    # ------------------------------------------------------------------
    def expected_probability(
        self,
        ability:     float,
        difficulty:  float,
        discrimination: float,
        guessing:    float,
    ) -> float:
        """
        3-PL IRT:
            P = c + (1−c) · σ(a·(θ−b))
        where σ is the logistic sigmoid.
        """
        logit = discrimination * (ability - difficulty)
        sigmoid = 1.0 / (1.0 + math.exp(-logit))
        return guessing + (1.0 - guessing) * sigmoid

    # ------------------------------------------------------------------
    def update(
        self,
        ability:        float,
        uncertainty:    float,          # current σ
        difficulty:     float,
        correct:        bool,
        hint_used:      bool,
        time_taken:     float,
        estimated_time: float,
        questions_done: int,
        correct_streak: int   = 0,      # consecutive correct before this Q
        wrong_streak:   int   = 0,      # consecutive wrong before this Q
        discrimination: float = None,   # per-question a; None → use default
        guessing_param: float = None,   # per-question c; None → use default
        question_type:  str   = "direct",
    ) -> UpdateResult:

        a = discrimination if discrimination is not None else self.k_default
        c = guessing_param if guessing_param is not None else self.c_default

        # ── STEP 1: Expected probability (3-PL IRT) ────────────────────
        P = self.expected_probability(ability, difficulty, a, c)

        # ── STEP 2: Answer encoding ────────────────────────────────────
        A = 1.0 if correct else 0.0

        # ── STEP 3: Raw surprise ───────────────────────────────────────
        surprise = A - P

        # ── STEP 4: Guess detection ────────────────────────────────────
        time_ratio    = time_taken / max(estimated_time, 1.0)
        guess_detected = (
            correct
            and difficulty > self.guess_hard_thr
            and time_ratio  < self.guess_time_thr
        )
        S = surprise * self.guess_discount if guess_detected else surprise

        # ── STEP 5: Hint adjustment ────────────────────────────────────
        hint_modifier = 1.0
        if hint_used and S > 0:
            hint_modifier = 1.0 - self.hint_penalty
        S_hint = S * hint_modifier

        # ── STEP 6: Time modifier ──────────────────────────────────────
        time_modifier = 1.0
        if time_ratio < self.fast_thr and S > 0 and not guess_detected:
            time_modifier = 1.0 + self.fast_bonus
        elif time_ratio > self.slow_thr:
            time_modifier = 1.0 - self.slow_penalty
        S_time = S_hint * time_modifier

        # ── STEP 7: Streak modifier ────────────────────────────────────
        streak_modifier = 1.0
        if correct and correct_streak >= self.streak_boost_start and S_time > 0:
            streak_modifier = self.streak_boost_factor
        elif not correct and wrong_streak >= self.streak_penalty_start and S_time < 0:
            streak_modifier = self.streak_penalty_factor
        S_adj = S_time * streak_modifier

        # ── STEP 8: Decaying learning rate ─────────────────────────────
        alpha = self.alpha0 * (self.decay ** questions_done)

        # ── STEP 9: Delta ──────────────────────────────────────────────
        delta = alpha * S_adj

        # ── STEP 10: Ability update + clamp ───────────────────────────
        new_ability = max(self.ability_min,
                          min(self.ability_max, ability + delta))

        # ── STEP 11: Uncertainty update ────────────────────────────────
        surprise_magnitude = abs(surprise)
        new_uncertainty = max(
            self.u_min,
            uncertainty * self.u_decay
            + surprise_magnitude * self.u_surp_boost
        )

        return UpdateResult(
            ability_before     = round(ability, 4),
            ability_after      = round(new_ability, 4),
            delta              = round(delta, 4),
            expected_p         = round(P, 4),
            discrimination     = round(a, 4),
            guessing_param     = round(c, 4),
            surprise           = round(surprise, 4),
            surprise_adj       = round(S_adj, 4),
            guess_detected     = guess_detected,
            hint_modifier      = round(hint_modifier, 4),
            time_modifier      = round(time_modifier, 4),
            time_ratio         = round(time_ratio, 4),
            streak_modifier    = round(streak_modifier, 4),
            learning_rate      = round(alpha, 4),
            uncertainty_before = round(uncertainty, 4),
            uncertainty_after  = round(new_uncertainty, 4),
        )
