"""
train_model_real.py — Train ML models on real (collected) session data
========================================================================
Trains two models:
  Model A: Predicts P(correct) for next question  →  replaces IRT formula
  Model B: Predicts ability_after directly         →  replaces update equation

Both are compared against the IRT baseline (expected_p).
Best model saved to backend/models/ability_model_real.pkl

This is the real-data counterpart to train_model.py (synthetic data).
In addition to the 80/20 session-split evaluation, this script also runs
a 5-fold GroupKFold cross-validation grouped by session_id. With only 97
real sessions, a single 80/20 split's test set is small (~19-20 sessions)
— its AUC can look better or worse than the model's true performance just
from which sessions happened to land in the test fold. Cross-validation
averages over 5 different splits so the reported number reflects the
model, not a lucky/unlucky split.
"""

import sys, os, json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, GroupKFold
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, roc_auc_score,
                             classification_report, brier_score_loss)
from sklearn.pipeline import Pipeline
import pickle, warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

DATA_FILE  = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'real_sessions.jsonl')
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

# ── Cross-validation — 5-fold GroupKFold grouped by session_id ────────
# Why this matters: we only have 97 sessions total, so the 80/20 split
# above tests on ~19-20 sessions. That's few enough that the test AUC can
# swing quite a bit depending on which particular sessions ended up in
# the test set — a handful of unusually easy or hard students can shift
# the number without the model actually being better or worse. GroupKFold
# reruns the same train/test split idea 5 times (each time holding out a
# different ~20% of sessions as the test fold, never splitting a session
# across train and test) and we look at the mean and spread (std) of AUC
# across those 5 folds. A small std means the single-split number above
# is trustworthy; a large std means it isn't and the mean here is the
# more honest estimate of how the model generalizes to a new student.
print(f"\n{'='*55}")
print(f"5-Fold Cross-Validation (GroupKFold by session_id)")
print("-"*55)

gkf = GroupKFold(n_splits=5)
cv_results = {}

for name, model in models.items():
    fold_aucs = []
    for train_idx, test_idx in gkf.split(X, y, groups=df["session_id"].values):
        X_tr, X_te = X[train_idx], X[test_idx]
        y_tr, y_te = y[train_idx], y[test_idx]
        fold_model = clone(model)  # fresh unfit clone, same hyperparameters
        fold_model.fit(X_tr, y_tr)
        fold_probs = fold_model.predict_proba(X_te)[:, 1]
        fold_aucs.append(roc_auc_score(y_te, fold_probs))
    fold_aucs = np.array(fold_aucs)
    cv_results[name] = {"mean_auc": fold_aucs.mean(), "std_auc": fold_aucs.std(), "fold_aucs": fold_aucs.tolist()}
    print(f"  {name:<20} mean AUC: {fold_aucs.mean():.4f}   std: {fold_aucs.std():.4f}   folds: {[round(float(a),3) for a in fold_aucs]}")

print("-"*55)
print(f"  (compare each model's single-split AUC above to its CV mean AUC here —")
print(f"   a big gap between the two means the single split was not representative)")

# ── Save best model ───────────────────────────────────────────────────
model_path = os.path.join(MODEL_DIR, "ability_model_real.pkl")
meta_path  = os.path.join(MODEL_DIR, "model_meta_real.json")

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
    "cv_mean_auc":      round(cv_results[best_model[0]]["mean_auc"], 4),
    "cv_std_auc":       round(cv_results[best_model[0]]["std_auc"], 4),
    "cv_fold_aucs":     [round(a, 4) for a in cv_results[best_model[0]]["fold_aucs"]],
    "cv_sessions_total": int(df["session_id"].nunique()),
}
with open(meta_path, 'w') as f:
    json.dump(meta, f, indent=2)

print(f"\n✅ Best model saved: {model_path}")
print(f"   Metadata: {meta_path}")
print(f"\n{'='*55}")
print(f"Summary:")
print(f"  Best model      : {best_model[0]}")
print(f"  Single-split AUC: {meta['test_auc']} (IRT baseline: {meta['irt_baseline_auc']})")
print(f"  AUC improvement : {meta['auc_improvement']:+.4f} over IRT (single split)")
print(f"  CV mean AUC     : {meta['cv_mean_auc']} +/- {meta['cv_std_auc']} (5-fold, grouped by session)")
print(f"  Brier score     : {meta['test_brier']} (lower = better calibration)")
print(f"\nNOTE: training/evaluation only — backend/ability_engine.py, config.py,")
print(f"and the original ability_model.pkl were not touched by this script.")
print(f"Feature vector at prediction time: {FEATURES}")
