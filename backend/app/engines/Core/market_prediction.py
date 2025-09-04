# app/engines/Core/market_prediction.py
from __future__ import annotations
import os, pickle, random
from typing import Any, Dict, List, Optional
from app.engines import register

# Where we look for the trained model (created by your tiny trainer)
_ART_PATH = "app/engines/Core/_artifacts/market_lin.pkl"
_MODEL_VERSION = "lin_v1"

def _safe_float(x, default=0.0) -> float:
    try:
        return float(x)
    except Exception:
        return float(default)

def _load_model() -> Optional[dict]:
    """Load a pickled sklearn model if present; otherwise return None."""
    if not os.path.exists(_ART_PATH):
        return None
    try:
        with open(_ART_PATH, "rb") as f:
            model = pickle.load(f)
        # must include {"feats": [...], "m1": <sk_model>, "m2": <sk_model>}
        if isinstance(model, dict) and "feats" in model and "m1" in model and "m2" in model:
            return model
    except Exception:
        pass
    return None

def _extract_features(params: Dict[str, Any], feat_names: List[str]) -> List[float]:
    """
    Build the feature vector the model expects. Keep names stable with your trainer.
    Missing fields are filled with neutral defaults so this never throws.
    """
    demand  = (params.get("demand") or {}) or {}
    liq     = (params.get("liquidity") or {}) or {}
    climate = (params.get("climate_signals") or {}) or {}
    macro   = (params.get("macro") or {}) or {}

    raw = {
        # demand-side signals (from valuation params)
        "watchlist_count": _safe_float(demand.get("watchlist_count"), 0),
        "bids_24h":        _safe_float(demand.get("bids_24h"), 0),
        "active_users_24h":_safe_float(demand.get("active_users_24h"), 0),
        "external_index":  _safe_float(demand.get("external_index"), 1.0),

        # orderbook / liquidity (from valuation params)
        "spread_bps":        _safe_float(liq.get("spread_bps"), 120),
        "depth_units":       _safe_float(liq.get("depth_units"), 0),
        "turnover_24h_pct":  _safe_float(liq.get("turnover_24h_pct"), 0.0),

        # climate proxy (keep simple; expand later)
        "enso_rain_anom_pct": _safe_float(climate.get("rain_anom_pct"), 0.0),

        # macro proxy (you can feed this later from an API)
        "rate_10y_bp": _safe_float(macro.get("rate_10y_bp"), 0.0),
    }

    # Return in the exact order the model was trained on
    return [ _safe_float(raw.get(name), 0.0) for name in feat_names ]

def _heuristic(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Lightweight fallback: small, bounded random drift informed by rough ideas.
    Safe to run without any external dependencies.
    """
    demand  = (params.get("demand") or {}) or {}
    liq     = (params.get("liquidity") or {}) or {}
    climate = (params.get("climate_signals") or {}) or {}
    macro   = (params.get("macro") or {}) or {}

    # crude signals
    wl = min(_safe_float(demand.get("watchlist_count"), 0) / 500.0, 1.0)
    bids = min(_safe_float(demand.get("bids_24h"), 0) / 100.0, 1.0)
    users = min(_safe_float(demand.get("active_users_24h"), 0) / 200.0, 1.0)
    ext = _safe_float(demand.get("external_index"), 1.0)

    spread = _safe_float(liq.get("spread_bps"), 120.0)
    depth  = _safe_float(liq.get("depth_units"), 0.0)
    turn   = _safe_float(liq.get("turnover_24h_pct"), 0.0)

    rain   = _safe_float(climate.get("rain_anom_pct"), 0.0)
    ratebp = _safe_float(macro.get("rate_10y_bp"), 0.0)

    # translate to tiny deltas (kept very small; models will replace this)
    demand_k = 0.002 * (0.35*wl + 0.30*bids + 0.20*users + 0.15*(ext-1.0))
    liq_k    = 0.0015 * ((50 - min(spread, 200)) / 200.0 + min(depth, 100000)/200000.0 + min(turn, 5.0)/10.0)
    weather  = 0.0002 * rain
    rates    = -0.0001 * (ratebp / 10.0)
    noise    = random.uniform(-0.003, 0.003)

    f1w = demand_k + liq_k + weather + rates + noise
    f1m = 1.9 * f1w

    return {
        "status": "ok",
        "mode": "heuristic",
        "forecast_1w": float(f1w),
        "forecast_1m": float(f1m),
        "drivers": {
            "demand_k": demand_k,
            "liq_k": liq_k,
            "weather": weather,
            "rates": rates,
            "noise": noise
        }
    }

def run(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Contract:
      inputs: valuation params dict (may include demand/liquidity/climate_signals/macro)
      outputs:
        {
          status: "ok",
          mode: "ml"|"heuristic",
          forecast_1w: float,   # e.g. +0.012 = +1.2% expected drift over 1 week
          forecast_1m: float,   # e.g. -0.020 = -2.0% over 1 month
          drivers: { ... }      # optional diagnostics
        }
    """
    model = _load_model()
    if not model:
        return _heuristic(params)

    try:
        feats = model["feats"]
        X = _extract_features(params, feats)
        m1 = model["m1"]   # 1-week model
        m2 = model["m2"]   # 1-month model

        # Predict
        f1w = float(m1.predict([X])[0])
        f1m = float(m2.predict([X])[0])

        return {
            "status": "ok",
            "mode": "ml",
            "version": _MODEL_VERSION,
            "forecast_1w": f1w,
            "forecast_1m": f1m,
            "drivers": {"model": "sklearn.LinearRegression", "features": feats}
        }
    except Exception:
        # If anything fails, never break valuation – just fallback
        return _heuristic(params)

# Register with the engine registry so valuation can call it
register(
    key="market_prediction",
    fn=run,
    name="Market Prediction",
    description="Predicts 1w/1m drift using a pickled ML model if available; otherwise uses a safe heuristic."
)