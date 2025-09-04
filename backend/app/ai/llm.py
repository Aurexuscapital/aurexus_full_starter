# app/ai/llm.py
from __future__ import annotations
from typing import Any, Dict, List

class LLM:
    """
    Planning/critique/explain now *drive* engine parameters.
    Swap internals to a real LLM later; the contract stays the same.
    """

    @staticmethod
    def plan(user_query: str) -> List[Dict[str, Any]]:
        uq = user_query.lower()

        # Extract a very naive address (swap to real LLM later)
        addr = None
        for sep in [" at ", " in ", " near "]:
            if sep in uq:
                addr = user_query.split(sep, 1)[1].strip()
                break
        addr = addr or "Unknown Address"

        # Signals
        wants_value   = any(k in uq for k in ["worth", "value", "valuation", "price"])
        mentions_pool = "pool" in uq
        wants_future  = any(k in uq for k in ["future", "forecast", "trend", "next month", "next year"])

        # Always start with comps to anchor valuation
        steps: List[Dict[str, Any]] = [
            {"tool": "comps",
             "args": {"address": addr, "radius_km": 1.6, "limit": 12},
             "save_as": "comps1"}
        ]

        # Parameterize valuation: AI chooses blend & overlays
        if wants_value or True:
            val_args: Dict[str, Any] = {
                "mode": "equity",
                "address": addr,
                "use_comps": True,
                "comps_radius_km": 1.6,
                "blend_comps": 0.7,          # AI chosen
                "blend_hedonic": 0.3,        # AI chosen
                "tokens_outstanding": 1_000_000,
                "liquidity": {"spread_bps": 70, "depth_units": 40000, "turnover_24h_pct": 1.5},
                "demand":   {"watchlist_count": 140, "bids_24h": 30, "active_users_24h": 70, "external_index": 1.03},
                "macro":    {"discount_rate_delta_bps": 0},   # neutral now; AI can tweak
                "progress": {"percent": 0.0, "planned_completion_months": 12.0},
            }
            if mentions_pool:
                # your valuation can later read this to apply uplift curves
                val_args["reno"] = {"pool": True}

            steps.append({"tool": "valuation", "args": val_args, "save_as": "valuation1"})

        if wants_future:
            steps.append({"tool": "market", "args": {"address": addr}, "save_as": "market1"})

        return steps

    @staticmethod
    def critique(state: Dict[str, Any]) -> List[str]:
        issues: List[str] = []
        # 1) wide valuation band? request tighter comps radius next run
        band = (state.get("valuation1", {}).get("core_valuation") or {})
        if band:
            base = band.get("base"); low = band.get("low"); high = band.get("high")
            if base and low and high:
                span = (high - low) / max(base, 1.0)
                if span > 0.35:
                    issues.append("Band too wide → shrink comps radius, increase comps weight.")
        # 2) missing comps?
        if not (state.get("comps1", {}).get("comps") or []):
            issues.append("No comps returned → fallback to hedonic only.")
        return issues

    @staticmethod
    def explain(user_query: str, state: Dict[str, Any]) -> str:
        v = state.get("valuation1", {})
        band = v.get("core_valuation") or {}
        base, low, high = band.get("base"), band.get("low"), band.get("high")
        comps_used = len((v.get("components") or {}).get("comps_used") or [])
        mp = (v.get("token_pricing") or {})
        fx1m = ((mp.get("prediction_overlay") or {}).get("forecast_1m"))

        lines = ["Aurexus AI result:"]
        if base:
            lines.append(f"- Value range ${low:,.0f} – ${high:,.0f} (base ${base:,.0f}).")
        if comps_used:
            lines.append(f"- Used {comps_used} comparable sales (AI-weighted) within ~1.6 km.")
        if fx1m is not None:
            lines.append(f"- Near-term drift (1m): {fx1m:+.2%} from market signals.")
        if "pool" in user_query.lower():
            lines.append("- Includes pool uplift assumption; adjust in Scenario Simulator if needed.")
        return "\n".join(lines)