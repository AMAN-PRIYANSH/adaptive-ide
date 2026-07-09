"""
train_model.py — Train ML models on synthetic session data
==========================================================
Trains two models:
  Model A: Predicts P(correct) for next question  →  replaces IRT formula
  Model B: Predicts ability_after directly         →  replaces update equation

Both are compared against the IRT baseline (expected_p).
Best model saved to backend/models/ability_model.pkl
"""

import sys, os, json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, roc_auc_score,
                             classification_report, brier_score_loss)
from sklearn.pipeline import Pipeline
import pickle, warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

DATA_FILE  = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'synthetic_sessions.jsonl')
MODEL_DIR  = os.path.join(os.path.dirname(__file__), '..', 'backend', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

# ── Load data ─────────────────────────────────────────────────────────
print("Loading data...")
rows = []
with open(DATA_FILE) as f:
    for line in f:
        rows.append(json.loads(line.strip()))

df = pd.DataFrame(rows)
print(f"  Rows: {len(df)}  |  Columns: {len(df.columns)}")
print(f"  Correct rate: {df['correct'].mean():.1%}")
print(f"  Sessions: {df['session_id'].nunique()}")

# ── Feature engineering ───────────────────────────────────────────────
# These are the features available at prediction time (BEFORE the answer)
FEATURES = [
    # IRT signals
    "ability_before",       # current θ estimate
    "uncertainty_before",   # current σ
    "difficulty",           # question b
    "discrimination",       # question a
    "guessing_param",       # question c
    "expected_p",           # IRT-predicted probability (our baseline)
    # Contextual
    "q_num",                # position in quiz (early vs late)
    "questions_done",       # same
    "correct_streak",       # consecutive correct before this Q
    "wrong_streak",         # consecutive wrong before this Q
    "learning_rate",        # current α
    # Question metadata
    "estimated_time",       # question complexity proxy
    # Derived
    "ability_difficulty_gap",  # θ − b
    "uncertainty_weighted_p",  # expected_p × (1 − uncertainty)
]

df["ability_difficulty_gap"]  = df["ability_before"] - df["difficulty"]
df["uncertainty_weighted_p"]  = df["expected_p"] * (1 - df["uncertainty_before"])

# Encode question type
df["q_type_enc"] = df["q_type"].map({"direct": 0, "logic": 1, "program": 2})
FEATURES.append("q_type_enc")

X = df[FEATURES].values
y = df["correct"].values

# ── Train/test split — split by session (no data leakage) ────────────
session_ids = df["session_id"].unique()
np.random.seed(42)
np.random.shuffle(session_ids)
split = int(len(session_ids) * 0.80)
train_sessions = set(session_ids[:split])
test_sessions  = set(session_ids[split:])

train_mask = df["session_id"].isin(train_sessions)
test_mask  = df["session_id"].isin(test_sessions)

X_train, y_train = X[train_mask], y[train_mask]
X_test,  y_test  = X[test_mask],  y[test_mask]

print(f"\nTrain: {len(X_train)} rows ({train_mask.sum()} / {len(df)})")
print(f"Test:  {len(X_test)} rows")

# ── IRT baseline ──────────────────────────────────────────────────────
irt_preds  = df.loc[test_mask, "expected_p"].values
irt_binary = (irt_preds >= 0.5).astype(int)
irt_acc    = accuracy_score(y_test, irt_binary)
irt_auc    = roc_auc_score(y_test, irt_preds)
irt_brier  = brier_score_loss(y_test, irt_preds)

print(f"\n{'='*55}")
print(f"IRT Baseline (expected_p threshold=0.5)")
print(f"  Accuracy : {irt_acc:.4f}")
print(f"  ROC-AUC  : {irt_auc:.4f}")
print(f"  Brier    : {irt_brier:.4f}  (lower = better)")

# ── Train models ──────────────────────────────────────────────────────
models = {
    "Logistic Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=1.0, max_iter=1000, random_state=42)),
    ]),
    "Random Forest": RandomForestClassifier(
        n_estimators=150, max_depth=6, min_samples_leaf=10,
        random_state=42, n_jobs=-1
    ),
    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=200, learning_rate=0.05, max_depth=4,
        min_samples_leaf=10, random_state=42
    ),
}

results = {}
print(f"\n{'='*55}")
print(f"{'Model':<22} {'Acc':>7} {'AUC':>7} {'Brier':>8} {'vs IRT':>8}")
print("-"*55)

best_model = None
best_auc   = 0.0

for name, model in models.items():
    model.fit(X_train, y_train)
    probs  = model.predict_proba(X_test)[:, 1]
    preds  = (probs >= 0.5).astype(int)
    acc    = accuracy_score(y_test, preds)
    auc    = roc_auc_score(y_test, probs)
    brier  = brier_score_loss(y_test, probs)
    delta  = auc - irt_auc
    results[name] = {"acc": acc, "auc": auc, "brier": brier, "model": model, "probs": probs}
    marker = " ◄ BEST" if auc > best_auc else ""
    print(f"  {name:<20} {acc:>7.4f} {auc:>7.4f} {brier:>8.4f} {delta:>+7.4f}{marker}")
    if auc > best_auc:
        best_auc   = auc
        best_model = (name, model)

print("-"*55)
print(f"  IRT Baseline       {irt_acc:>7.4f} {irt_auc:>7.4f} {irt_brier:>8.4f}")

# ── Feature importance ────────────────────────────────────────────────
print(f"\n{'='*55}")
print(f"Feature Importance — {best_model[0]}")
print("-"*55)

if hasattr(best_model[1], 'feature_importances_'):
    importances = best_model[1].feature_importances_
elif hasattr(best_model[1], 'named_steps'):
    importances = best_model[1].named_steps['clf'].coef_[0]
    importances = np.abs(importances) / np.abs(importances).sum()
else:
    importances = None

if importances is not None:
    feat_imp = sorted(zip(FEATURES, importances), key=lambda x: -x[1])
    for feat, imp in feat_imp:
        bar = "█" * int(imp * 40)
        print(f"  {feat:<28} {imp:>6.4f}  {bar}")

# ── Save best model ───────────────────────────────────────────────────
model_path = os.path.join(MODEL_DIR, "ability_model.pkl")
meta_path  = os.path.join(MODEL_DIR, "model_meta.json")

with open(model_path, 'wb') as f:
    pickle.dump(best_model[1], f)

meta = {
    "model_name":   best_model[0],
    "features":     FEATURES,
    "train_rows":   int(len(X_train)),
    "test_rows":    int(len(X_test)),
    "test_accuracy": round(results[best_model[0]]["acc"], 4),
    "test_auc":      round(results[best_model[0]]["auc"], 4),
    "test_brier":    round(results[best_model[0]]["brier"], 4),
    "irt_baseline_auc": round(irt_auc, 4),
    "auc_improvement":  round(results[best_model[0]]["auc"] - irt_auc, 4),
}
with open(meta_path, 'w') as f:
    json.dump(meta, f, indent=2)

print(f"\n✅ Best model saved: {model_path}")
print(f"   Metadata: {meta_path}")
print(f"\n{'='*55}")
print(f"Summary:")
print(f"  Best model      : {best_model[0]}")
print(f"  AUC             : {meta['test_auc']} (IRT baseline: {meta['irt_baseline_auc']})")
print(f"  AUC improvement : {meta['auc_improvement']:+.4f} over IRT")
print(f"  Brier score     : {meta['test_brier']} (lower = better calibration)")
print(f"\nThis model can now replace engine.expected_probability()")
print(f"Feature vector at prediction time: {FEATURES}")
