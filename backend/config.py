# config.py
"""
Central configuration for the Adaptive Quiz Engine v2.
All tuneable parameters live here. Do NOT scatter magic numbers in the code.
"""

import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "data")

QUESTION_FILES = {
    "Python":          "python_questions.json",
    "C":               "c_questions.json",
    "Data Structures": "data_structures_questions.json",
}

# ---------------------------------------------------------------------------
# Quiz length per subject
# ---------------------------------------------------------------------------
QUIZ_LENGTH = {
    "Python":          15,
    "C":               15,
    "Data Structures": 12,
}

# ---------------------------------------------------------------------------
# Student ability initialisation ranges
# ---------------------------------------------------------------------------
ABILITY_INIT = {
    "Beginner":     (0.10, 0.25),
    "Intermediate": (0.40, 0.60),
    "Advanced":     (0.75, 0.90),
}

ABILITY_MIN = 0.05
ABILITY_MAX = 0.95

# ---------------------------------------------------------------------------
# Question selection
# ---------------------------------------------------------------------------
DIFFICULTY_WINDOW_INIT = 0.15
DIFFICULTY_WINDOW_STEP = 0.10
DIFFICULTY_WINDOW_MAX  = 0.50

# ---------------------------------------------------------------------------
# IRT parameters
# ---------------------------------------------------------------------------
# k = discrimination constant in the 1-PL / shared-k 2-PL logistic.
# Standard CAT systems use 1.7; we use 2.0 for a crisper boundary.
IRT_K = 2.0

# Per-question discrimination override: if the JSON question has a field
# "discrimination" (a ∈ [0.5, 3.0]), the engine will use that instead of IRT_K.
# Questions without the field fall back to IRT_K.  This enables true 2-PL IRT.
IRT_DEFAULT_DISCRIMINATION = 2.0   # fallback when field is absent

# Guessing parameter c (3-PL IRT).
# For a 4-option MCQ the theoretical floor is 0.25.
# We use 0.20 (slightly below chance) as default — research shows real
# guessing is rarely pure random. Set to 0.0 to disable 3-PL.
IRT_GUESSING_PARAM = 0.20

# ---------------------------------------------------------------------------
# Ability uncertainty (confidence) tracking
# ---------------------------------------------------------------------------
# We maintain a running uncertainty σ alongside θ.
# σ starts high (we know nothing) and shrinks as more evidence arrives.
UNCERTAINTY_INIT      = 0.30   # initial σ at quiz start
UNCERTAINTY_MIN       = 0.05   # floor — we can never be 100 % certain
UNCERTAINTY_DECAY     = 0.88   # multiply σ by this after each question
# Surprise amplification: high-surprise answers slow down σ decay
# (a very surprising answer means our estimate might be off).
UNCERTAINTY_SURPRISE_BOOST = 0.08

# ---------------------------------------------------------------------------
# Streak modelling
# ---------------------------------------------------------------------------
# A correct streak boosts confidence that the student has genuinely mastered
# the material; a wrong streak signals struggle.
STREAK_BOOST_START    = 3      # consecutive correct answers to trigger boost
STREAK_BOOST_FACTOR   = 1.10   # multiply positive surprise_adj by this
STREAK_PENALTY_START  = 3      # consecutive wrong answers to trigger penalty
STREAK_PENALTY_FACTOR = 0.90   # multiply negative surprise_adj by this

# ---------------------------------------------------------------------------
# Guess detection via response time
# ---------------------------------------------------------------------------
# If a student answers a hard question very fast, it may be a lucky guess.
# We define "hard" as difficulty > GUESS_HARD_THRESHOLD
# and "fast" as time_ratio < GUESS_TIME_THRESHOLD.
# When both are true we apply a discount to the positive surprise.
GUESS_HARD_THRESHOLD  = 0.65   # question difficulty above this = hard
GUESS_TIME_THRESHOLD  = 0.30   # answered in < 30 % of expected time = suspiciously fast
GUESS_DISCOUNT        = 0.50   # halve the positive surprise when guess detected

# ---------------------------------------------------------------------------
# Learning rate
# ---------------------------------------------------------------------------
LEARNING_RATE_BASE  = 0.12
LEARNING_RATE_DECAY = 0.92

# ---------------------------------------------------------------------------
# Hint penalty
# ---------------------------------------------------------------------------
HINT_PENALTY = 0.40

# ---------------------------------------------------------------------------
# Time modifiers
# ---------------------------------------------------------------------------
TIME_FAST_THRESHOLD = 0.50
TIME_SLOW_THRESHOLD = 2.00
TIME_FAST_BONUS     = 0.10
TIME_SLOW_PENALTY   = 0.10

# ---------------------------------------------------------------------------
# Security / UI
# ---------------------------------------------------------------------------
RANDOMIZE_OPTIONS   = True
FULLSCREEN_ON_START = True

# ---------------------------------------------------------------------------
# Flask session
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")
