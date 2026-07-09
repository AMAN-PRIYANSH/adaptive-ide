# Adaptive Learning IDE — Phase 2: Adaptive Quiz Engine

A Flask + vanilla-JS web app that estimates student ability in real time
and adapts question difficulty after every answer.

---

## What's New in v2.2

- Fixed question stacking bug (questions now render fresh each time)
- Added Supabase PostgreSQL logger for persistent data collection
- Added admin dashboard at `/admin` with live stats and charts
- Added synthetic student simulator (200 students, 3000 training rows)
- Trained baseline ML model (Random Forest, AUC=0.5497 vs IRT 0.5423)
- Added `ml_predictor.py` as drop-in replacement for IRT formula
- Fixed 4 hints that had cross-question references
- Fixed 21 broken questions, normalised Unicode quotes across all 156 Qs
- Added `requirements.txt`, `Procfile`, `render.yaml` for Render deployment
- App now reads `PORT` env var for cloud hosting compatibility

---

## Project Structure

```
adaptive-ide/
├── backend/
│   ├── app.py              ← Flask routes (entry point)
│   ├── config.py           ← All tuneable parameters
│   ├── models.py           ← Question, QuestionBank
│   ├── ability_engine.py   ← IRT-based ability update (full math docs inside)
│   ├── student.py          ← Per-session state
│   ├── quiz_manager.py     ← Orchestrator
│   ├── logger.py           ← Attempt log (swap for DB later)
│   └── data/               ← JSON question files (copy from root data/)
├── frontend/
│   ├── templates/
│   │   ├── index.html      ← Landing / setup page
│   │   ├── quiz.html       ← Question + feedback
│   │   └── result.html     ← Charts + final stats
│   └── static/
│       ├── css/main.css
│       └── js/quiz.js
├── data/                   ← Generated JSON + enriched .md files
├── tests/
│   └── test_engine.py      ← 17 unit tests
├── md_to_json.py           ← .md → JSON converter (run this first)
└── README.md
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install flask pytest
```

### 2. Generate JSON datasets from .md files
```bash
python md_to_json.py
# Writes to ./data/  (python_questions.json, c_questions.json, data_structures_questions.json)
```

### 3. Copy data files into backend
```bash
cp data/*.json backend/data/
```

### 4. Run the app
```bash
cd backend
python app.py
# → http://localhost:5050
```

### 5. Run tests
```bash
python -m pytest tests/ -v
```

---

## How the Adaptive Engine Works

### Student Ability
A float in **[0.05, 0.95]** representing estimated knowledge level.
Initialised randomly within level ranges:
- Beginner: 0.10–0.25
- Intermediate: 0.40–0.60
- Advanced: 0.75–0.90

### Question Selection
The engine picks a random unanswered question whose `difficulty` is
within `±0.15` of the student's current ability. If none exists, the
window expands by `0.10` until `±0.50`. If still empty, the nearest
question by difficulty is chosen.

### Ability Update (IRT-inspired)

```
P = 1 / (1 + exp(−2.0 × (ability − difficulty)))   # expected probability

surprise = actual_outcome − P                        # core signal
  → correct on hard question: surprise ≈ +1.0
  → wrong on easy question:   surprise ≈ −1.0

# Modifiers
if hint_used and correct:  surprise *= 0.60          # −40% hint penalty
if time < 50% expected and correct: surprise *= 1.10 # +10% speed bonus
if time > 2× expected:     surprise *= 0.90          # −10% slow penalty

# Decaying learning rate
α = 0.12 × 0.92^(questions_answered)

# Update
Δability = α × surprise
new_ability = clip(ability + Δability, 0.05, 0.95)
```

Full mathematical explanation with justifications is in `ability_engine.py`.

### Dev Panel
Click **🛠 Dev** (top-right during quiz) to see every internal engine
variable updating in real time after each answer — difficulty,
expected P, surprise, learning rate, ability delta, and more.
No password required.

---

## Adding a New Subject

1. Add a `.md` question bank following the same format.
2. Run `python md_to_json.py your_file.md`.
3. Copy the JSON to `backend/data/`.
4. Add one line to `QUESTION_FILES` in `backend/config.py`.
5. Add one line to `QUIZ_LENGTH` in `backend/config.py`.

No engine code changes required.

---

## Future ML Handoff

The `Logger` records every attempt as a structured dict including
`(ability_before, difficulty, hint_used, time_ratio, expected_p, correct)`.
This is your training set. When you have enough data:

1. Replace `AbilityEngine.update()` with a trained model prediction.
2. Keep the same interface — `QuizManager` will not need changes.
3. The `QuestionSelector` window logic can similarly be replaced with a
   learned recommendation policy.

---

## Known Issues / Future Work

- Several C and Python questions have **missing code snippets** (the
  web scraper dropped them). These are marked `type: "program"`.
  Fill in the `question` field in the JSON before deploying.
- DSA-0036 is described as a "Java code" question in a DSA bank —
  flag for review.
- No login / persistence by design (Version 1 spec).
- `estimated_time` and `difficulty` values are Claude's initial
  estimates — replace with human-reviewed values using the
  enriched `.md` files in `data/`.

---

## Deployment (Render + Supabase)

Set environment variables on Render:
```
SUPABASE_URL = your project URL
SUPABASE_KEY = your anon key
```
Then push to GitHub — Render auto-deploys.
