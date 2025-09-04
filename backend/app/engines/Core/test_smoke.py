# app/engines/Core/test_smoke.py
from __future__ import annotations
import json
from typing import Any, Dict

from app.engines.Core import valuation
from app.engines.Core import comps as comps_engine
try:
    from app.engines.Core import market_prediction as market_pred
except Exception:
    market_pred = None


def pretty(x: Any) -> str:
    return json.dumps(x, indent=2, sort_keys=True)

def unwrap(out: Any) -> Dict[str, Any]:
    """Always return a dict even if engine returned (dict, ...) or (dict,)."""
    if isinstance(out, tuple) and out:
        out = out[0]
    return out if isinstance(out, dict) else {"status": "error", "raw": out}


def test_valuation_equity():
    params = {
        "mode": "equity",
        "address": "123 Test St, Sydney",
        "bedrooms": 3,
        "bathrooms": 2.0,
        "living_area_sqft": 1500,
        "land_cost": 50_000,
        "build_cost": 700_000,
        "soft_costs": 150_000,
        "sales_revenue": 1_600_000,
        "discount_rate_equity": 0.12,
        "use_comps": True,
        "comps_radius_km": 1.6,
        "demand": {
            "watchlist_count": 120,
            "bids_24h": 25,
            "active_users_24h": 60,
            "external_index": 1.05,
        },
        "liquidity": {"spread_bps": 80, "depth_units": 30_000, "turnover_24h_pct": 1.2},
        "tokens_outstanding": 1_000_000,
    }
    out = unwrap(valuation.run(params))
    assert out.get("status") == "done", pretty(out)
    band = out.get("core_valuation") or {}
    for k in ("low", "base", "high"):
        assert isinstance(band.get(k), (int, float)), pretty(out)


def test_valuation_credit():
    params = {
        "mode": "credit",
        "address": "1 Example Rd, Sydney",
        "loan_amount": 800_000,
        "coupon_apr": 0.10,
        "tenor_months": 24,
        "schedule": "bullet",
        "collateral": {"value_override": 1_500_000},
        "liquidity": {"spread_bps": 60, "depth_units": 50_000, "turnover_24h_pct": 2.0},
        "demand": {"watchlist_count": 80, "bids_24h": 12, "active_users_24h": 40, "external_index": 1.0},
        "tokens_outstanding": 500_000,
    }
    out = unwrap(valuation.run(params))
    assert out.get("status") == "done", pretty(out)
    band = out.get("core_valuation") or {}
    for k in ("low", "base", "high"):
        assert isinstance(band.get(k), (int, float)), pretty(out)


def test_comps_stub():
    out = unwrap(comps_engine.run({"address": "123 Test St, Sydney", "radius_miles": 1.0, "limit": 8}))
    assert out.get("status") == "ok", pretty(out)
    comps = out.get("comps") or []
    assert len(comps) >= 1, pretty(out)


def test_market_prediction_if_present():
    if market_pred is None:
        return
    out = unwrap(market_pred.run({"address": "123 Test St, Sydney"}))
    assert out.get("status") == "ok", pretty(out)


if __name__ == "__main__":
    # Simple runner without pytest
    try:
        test_valuation_equity()
        test_valuation_credit()
        test_comps_stub()
        test_market_prediction_if_present()
        print("SMOKE OK")
    except AssertionError as e:
        print("SMOKE FAIL\n", e)
        raise