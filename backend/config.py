# config.py v2.3 — tuned after real student testing
import os

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "data")

QUESTION_FILES = {
    "Python":          "python_questions.json",
    "C":               "c_questions.json",
    "Data Structures": "data_structures_questions.json",
}

QUIZ_LENGTH = {
    "Python":          15,
    "C":               15,
    "Data Structures": 12,
}

ABILITY_INIT = {
    "Beginner":     (0.10, 0.25),
    "Intermediate": (0.40, 0.60),
    "Advanced":     (0.75, 0.90),
}

ABILITY_MIN = 0.05
ABILITY_MAX = 0.95

DIFFICULTY_WINDOW_INIT = 0.15
DIFFICULTY_WINDOW_STEP = 0.10
DIFFICULTY_WINDOW_MAX  = 0.50

# IRT — reduced guessing floor (was 0.20, now 0.15)
# 0.20 was too high — was eating into positive surprise on easy Qs
IRT_DEFAULT_DISCRIMINATION = 2.0
IRT_GUESSING_PARAM         = 0.15   # was 0.20

# Uncertainty
UNCERTAINTY_INIT           = 0.30
UNCERTAINTY_MIN            = 0.05
UNCERTAINTY_DECAY          = 0.88
UNCERTAINTY_SURPRISE_BOOST = 0.08

# Streaks
STREAK_BOOST_START    = 3
STREAK_BOOST_FACTOR   = 1.10
STREAK_PENALTY_START  = 3
STREAK_PENALTY_FACTOR = 0.90

# Guess detection — raised time threshold (was 0.30, now 0.20)
# 6-10s on a 25s question = 0.24-0.40 ratio, was wrongly flagged
GUESS_HARD_THRESHOLD  = 0.65
GUESS_TIME_THRESHOLD  = 0.20   # was 0.30 — only flag truly instant answers
GUESS_DISCOUNT        = 0.50

# Learning rate — increased base, slower decay
# was: base=0.12, decay=0.92 → too slow convergence for short 15Q sessions
LEARNING_RATE_BASE  = 0.18   # was 0.12
LEARNING_RATE_DECAY = 0.95   # was 0.92 (slower decay = stays responsive longer)

# Hint
HINT_PENALTY = 0.40

# Time modifiers
TIME_FAST_THRESHOLD = 0.50
TIME_SLOW_THRESHOLD = 2.00
TIME_FAST_BONUS     = 0.10
TIME_SLOW_PENALTY   = 0.10

RANDOMIZE_OPTIONS   = True
FULLSCREEN_ON_START = True

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")
