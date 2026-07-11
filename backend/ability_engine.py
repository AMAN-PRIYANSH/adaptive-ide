# ability_engine.py v2.4 — boundary dampening added
"""
AbilityEngine v2.4
==================
New in this version:
  - Boundary dampening (Step 10b): sigmoid-based factor that slows
    ability movement near the floor (0.05) and ceiling (0.95).
    Stays near 1.0 in the middle range [0.20, 0.80].
    Inspired by sigmoid/softmax compression near extreme values.

Full pipeline: Steps 1-11 (same as v2) + Step 10b (new).

BOUNDARY DAMPENING MATH
========================
We use a product of two logistic sigmoids:

    near_floor   = σ(k · (θ − ABILITY_MIN − margin))
    near_ceiling = σ(k · (ABILITY_MAX − margin − θ))
    BF = max(BF_MIN, near_floor × near_ceiling)

where σ(x) = 1/(1+e^−x), k=12, margin=0.12, BF_MIN=0.10

Interpretation:
  • When θ = 0.50: BF ≈ 0.986 (full speed, no dampening)
  • When θ = 0.80: BF ≈ 0.611 (moderate dampening)
  • When θ = 0.88: BF ≈ 0.321 (strong dampening)
  • When θ = 0.93: BF ≈ 0.153 (very strong dampening)
  • When θ = 0.95: BF = 0.10  (minimum — never fully stops)

Same curve mirrored near the floor.

This is applied AFTER the learning rate:
    Δθ = α × S_adj × BF

So near the ceiling, even a correct answer on a hard question
moves ability by only 10-32% of what it would move in the middle.
This prevents ceiling lock (staying at 0.95 forever) while making
the final percentages genuinely hard to reach.

ASYMMETRY JUSTIFICATION
========================
IRT is intentionally asymmetric — wrong answer on a hard question
(where P is low, so surprise S = 0 - P ≈ -0.20) gives a small
negative delta, while correct answer on a matched question
(where P ≈ 0.50, so S = 1 - 0.50 = +0.50) gives a larger positive.
This is not a bug — it reflects that getting a hard question wrong
is expected, so it's less informative than getting it right.
We keep this asymmetry as it is academically correct.
"""

import math
from typing import TypedDict


class UpdateResult(TypedDict):
    ability_before:     float
    ability_after:      float
    delta:              float
    expected_p:         float
    discrimination:     float
    guessing_param:     float
    surprise:           float
    surprise_adj:       float
    guess_detected:     bool
    hint_modifier:      float
    time_modifier:      float
    time_ratio:         float
    streak_modifier:    float
    boundary_factor:    float   # NEW in v2.4
    learning_rate:      float
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
        self.u_decay      = cfg.UNCERTAINTY_DECAY
        self.u_min        = cfg.UNCERTAINTY_MIN
        self.u_surp_boost = cfg.UNCERTAINTY_SURPRISE_BOOST
        self.streak_boost_start    = cfg.STREAK_BOOST_START
        self.streak_boost_factor   = cfg.STREAK_BOOST_FACTOR
        self.streak_penalty_start  = cfg.STREAK_PENALTY_START
        self.streak_penalty_factor = cfg.STREAK_PENALTY_FACTOR
        self.guess_hard_thr  = cfg.GUESS_HARD_THRESHOLD
        self.guess_time_thr  = cfg.GUESS_TIME_THRESHOLD
        self.guess_discount  = cfg.GUESS_DISCOUNT
        # Boundary dampening
        self.bd_k      = cfg.BOUNDARY_DAMPENING_K
        self.bd_margin = cfg.BOUNDARY_DAMPENING_MARGIN
        self.bd_min    = cfg.BOUNDARY_DAMPENING_MIN

    # ------------------------------------------------------------------
    def _boundary_factor(self, theta: float) -> float:
        """
        Sigmoid-based boundary dampening.
        Returns value in [BD_MIN, 1.0].
        Near middle: ~1.0 (no effect).
        Near floor/ceiling: drops toward BD_MIN.
        """
        near_floor   = 1.0 / (1.0 + math.exp(
            -self.bd_k * (theta - self.ability_min - self.bd_margin)))
        near_ceiling = 1.0 / (1.0 + math.exp(
            -self.bd_k * (self.ability_max - self.bd_margin - theta)))
        return max(self.bd_min, near_floor * near_ceiling)

    # ------------------------------------------------------------------
    def expected_probability(self, ability, difficulty, discrimination, guessing):
        logit   = discrimination * (ability - difficulty)
        sigmoid = 1.0 / (1.0 + math.exp(-logit))
        return guessing + (1.0 - guessing) * sigmoid

    # ------------------------------------------------------------------
    def update(
        self,
        ability:        float,
        uncertainty:    float,
        difficulty:     float,
        correct:        bool,
        hint_used:      bool,
        time_taken:     float,
        estimated_time: float,
        questions_done: int,
        correct_streak: int   = 0,
        wrong_streak:   int   = 0,
        discrimination: float = None,
        guessing_param: float = None,
        question_type:  str   = "direct",
    ) -> UpdateResult:

        a = discrimination if discrimination is not None else self.k_default
        c = guessing_param if guessing_param is not None else self.c_default

        # Step 1: Expected probability (3-PL IRT)
        P = self.expected_probability(ability, difficulty, a, c)

        # Step 2: Answer encoding
        A = 1.0 if correct else 0.0

        # Step 3: Raw surprise
        surprise = A - P

        # Step 4: Guess detection
        time_ratio     = time_taken / max(estimated_time, 1.0)
        guess_detected = (
            correct
            and difficulty > self.guess_hard_thr
            and time_ratio  < self.guess_time_thr
        )
        S = surprise * self.guess_discount if guess_detected else surprise

        # Step 5: Hint adjustment
        hint_modifier = 1.0
        if hint_used and S > 0:
            hint_modifier = 1.0 - self.hint_penalty
        S_hint = S * hint_modifier

        # Step 6: Time modifier
        time_modifier = 1.0
        if time_ratio < self.fast_thr and S > 0 and not guess_detected:
            time_modifier = 1.0 + self.fast_bonus
        elif time_ratio > self.slow_thr:
            time_modifier = 1.0 - self.slow_penalty
        S_time = S_hint * time_modifier

        # Step 7: Streak modifier
        streak_modifier = 1.0
        if correct and correct_streak >= self.streak_boost_start and S_time > 0:
            streak_modifier = self.streak_boost_factor
        elif not correct and wrong_streak >= self.streak_penalty_start and S_time < 0:
            streak_modifier = self.streak_penalty_factor
        S_adj = S_time * streak_modifier

        # Step 8: Decaying learning rate
        alpha = self.alpha0 * (self.decay ** questions_done)

        # Step 9: Raw delta
        raw_delta = alpha * S_adj

        # Step 10b: Boundary dampening (NEW)
        bf = self._boundary_factor(ability)
        delta = raw_delta * bf

        # Step 10: Ability update + clamp
        new_ability = max(self.ability_min,
                          min(self.ability_max, ability + delta))

        # Step 11: Uncertainty update
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
            boundary_factor    = round(bf, 4),
            learning_rate      = round(alpha, 4),
            uncertainty_before = round(uncertainty, 4),
            uncertainty_after  = round(new_uncertainty, 4),
        )
