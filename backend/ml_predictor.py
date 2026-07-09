"""
ml_predictor.py
===============
Drop-in replacement for AbilityEngine.expected_probability().

Usage in ability_engine.py:
    from ml_predictor import MLPredictor
    predictor = MLPredictor()
    P = predictor.predict(feature_dict) if predictor.ready else irt_fallback

The engine ALWAYS falls back to IRT if the model file is missing or fails.
This means the system works even before any ML model is trained.
"""

import os, json, pickle
import numpy as np

MODEL_DIR  = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "ability_model.pkl")
META_PATH  = os.path.join(MODEL_DIR, "model_meta.json")


class MLPredictor:

    def __init__(self):
        self.ready    = False
        self.model    = None
        self.features = None
        self._load()

    def _load(self):
        if not os.path.exists(MODEL_PATH):
            print("[MLPredictor] No model file found — using IRT fallback")
            return
        try:
            with open(MODEL_PATH, 'rb') as f:
                self.model = pickle.load(f)
            with open(META_PATH) as f:
                meta = json.load(f)
            self.features = meta["features"]
            self.ready    = True
            print(f"[MLPredictor] Loaded {meta['model_name']} "
                  f"(AUC={meta['test_auc']}, trained on {meta['train_rows']} rows)")
        except Exception as e:
            print(f"[MLPredictor] Load failed: {e} — using IRT fallback")

    def predict(self, feature_dict: dict) -> float:
        """
        Predict P(correct) from a feature dict.
        Returns float in [0, 1].  Falls back to expected_p from IRT if model unavailable.
        """
        if not self.ready:
            return feature_dict.get("expected_p", 0.5)

        try:
            row = np.array([[feature_dict.get(f, 0.0) for f in self.features]])
            prob = self.model.predict_proba(row)[0][1]
            return float(np.clip(prob, 0.01, 0.99))
        except Exception as e:
            print(f"[MLPredictor] predict() failed: {e}")
            return feature_dict.get("expected_p", 0.5)

    @property
    def model_info(self) -> dict:
        if not os.path.exists(META_PATH):
            return {"status": "no model"}
        with open(META_PATH) as f:
            return json.load(f)
