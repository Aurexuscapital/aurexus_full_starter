# app/ai/nl_entry.py
from __future__ import annotations
import re
from typing import Any, Dict

from app.engines.Core import valuation as valuation_engine
try:
    from app.engines.Core import market_prediction as market_pred
except Exception:
    market_pred = None


# --- helpers ---------------------------------------------------------------

def _unwrap(x):
    """Some engines may return (dict, meta). Always give back the dict."""
    if isinstance(x, tuple):
        return x[0]
    return x

def _looks_like_valuation(q: str) -> bool:
    t = q.lower()
    return any(k in t for k in ["value", "valuation", "worth", "price", "estimate", "appraise"])

def _looks_like_outlook(q: str) -> bool:
    t = q.lower()
    return any(k in t for k in ["market", "outlook", "forecast", "trend", "next year", "2025", "2026", "2030"])

def _extract_address(q: str) -> str | None:
    m = re.search(r"\b(?:at|for)\s+([^,]+(?:, [^,]+){0,2})", q, flags=re.I)
    if not m:
        return None
    addr = m.group(1).strip()
    return addr.rstrip("?.!,")

def _detect_pool(q: str) -> bool:
    return "pool" in q.lower()


# --- main entry ------------------------------------------------------------

async def route_query(prompt: str) -> dict:
    """
    Natural language → deterministic engines.
    """
    # 1) valuation path
    if _looks_like_valuation(prompt):
        address = _extract_address(prompt) or "123 Test St, Sydney"
        add_pool = _detect_pool(prompt)

        sales_revenue_hint = 1.0 + (0.06 if add_pool else 0.0)

        params: Dict[str, Any] = {
            "mode": "equity",
            "address": address,
            "bedrooms": 3,
            "bathrooms": 2,
            "living_area_sqft": 1500,
            "land_cost": 50_000,
            "build_cost": 700_000,
            "soft_costs": 150_000,
            "sales_revenue": int(1_600_000 * sales_revenue_hint),
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

        result = _unwrap(valuation_engine.run(params))
        core = (result.get("core_valuation") or {})
        low, base, high = core.get("low"), core.get("base"), core.get("high")

        if all(isinstance(x, (int, float)) for x in (low, base, high)):
            summary = (
                f"Estimated value for **{address}**"
                f"{' with a pool' if add_pool else ''}: "
                f"${base:,.0f} (range ${low:,.0f}–${high:,.0f})."
            )
        else:
            summary = "Got a valuation, but couldn’t format the band."

        pred = None
        if market_pred:
            try:
                pred = _unwrap(market_pred.run(params))
            except Exception:
                pred = {"status": "none"}

        return {
            "status": "ok",
            "intent": "valuation",
            "address": address,
            "renovation": {"pool": add_pool} if add_pool else {},
            "summary": summary,
            "result": result,
            "prediction_overlay": pred,
        }

    # 2) market outlook path
    if _looks_like_outlook(prompt):
        if market_pred is None:
            return {
                "status": "ok",
                "intent": "market_outlook",
                "message": "Market prediction engine not available yet.",
            }
        try:
            pred = _unwrap(market_pred.run({"query": prompt}))
        except Exception:
            pred = {"status": "none"}

        f1w = pred.get("forecast_1w")
        f1m = pred.get("forecast_1m")
        if isinstance(f1w, (int, float)) and isinstance(f1m, (int, float)):
            dir_1w = "up" if f1w > 0 else "down" if f1w < 0 else "flat"
            dir_1m = "up" if f1m > 0 else "down" if f1m < 0 else "flat"
            summary = f"Near-term outlook: {dir_1w} (1-week {f1w:.2%}), {dir_1m} (1-month {f1m:.2%})."
        else:
            summary = "Outlook available (heuristic)."

        return {
            "status": "ok",
            "intent": "market_outlook",
            "summary": summary,
            "prediction": pred,
        }

    # 3) fallback echo
    return {
        "status": "ok",
        "intent": "echo",
        "prompt": prompt,
        "message": f"AI stub: I received your prompt '{prompt}'"
    }