# app/ai/router.py
from __future__ import annotations
from typing import Any, Dict, List, Optional

from app.ai.config import AGENTS, INTENT_POLICY, AgentSpec
from app.ai.agents import make_agent, EngineAgent

# -------------------- Intent + engine adapter --------------------

INTENTS = ["valuation", "comps", "scenario_sim", "market_outlook", "risk"]

def classify_intent(user_text: str) -> str:
    t = (user_text or "").lower()
    if any(k in t for k in ["scenario", "what if", "simulate"]):
        return "scenario_sim"
    if any(k in t for k in ["risk", "default", "prob", "band"]):
        return "risk"
    if any(k in t for k in ["market", "forecast", "outlook"]):
        return "market_outlook"
    if any(k in t for k in ["comp", "comparables"]):
        return "comps"
    return "valuation"

def _run_engine(tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic engine call via EngineAgent adapter."""
    agent = EngineAgent(spec=AgentSpec(
        key=f"engine:{tool}",
        role=f"Engine adapter for {tool}",
        model="deterministic",
        style="engine",
        temperature=0.0,
    ))
    return agent.run(prompt="", context={"payload": {"tool": tool, "params": params}})

# -------------------- Orchestrator (kept for future LLM routing) --------------------

class AgentRouter:
    def __init__(self):
        self.agents = {k: make_agent(v) for k, v in AGENTS.items()}

    def route(self, user_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        intent = classify_intent(user_text)
        plan_agent_key = INTENT_POLICY.get(intent, INTENT_POLICY["fallback"])[0]
        narr_agent_key = (INTENT_POLICY.get(intent, []) + ["narrative"])[-1]

        planner = self.agents[plan_agent_key]
        narrator = self.agents.get(narr_agent_key)

        # 1) ask planner for a plan (JSON)
        plan = planner.run(prompt=user_text, context={"intent": intent, **context})

        # 2) execute steps via deterministic engines
        step_outputs: List[Dict[str, Any]] = []
        last_structured: Optional[Dict[str, Any]] = None
        for step in plan.get("steps", []):
            tool = step.get("tool")
            params = step.get("params") or {}
            out = _run_engine(tool, params)
            step_outputs.append({"tool": tool, "output": out})
            if tool == "valuation" and out.get("status") == "ok":
                last_structured = out.get("result")

        if last_structured is None:
            for so in step_outputs:
                r = so.get("output", {}).get("result")
                if isinstance(r, dict):
                    last_structured = r
                    break

        # 3) narrative
        narrative = None
        if narrator:
            narr_out = narrator.run(
                prompt=plan.get("narrative_prompt") or "",
                context={**context, "result": last_structured},
            )
            narrative = narr_out.get("narrative")

        return {
            "status": "ok",
            "intent": intent,
            "plan": plan,
            "steps": step_outputs,
            "result": last_structured,
            "narrative": narrative,
        }

# -------------------- Direct NL → Engines entry (used by test script) --------------------

import re
from app.engines.Core import valuation as valuation_engine
try:
    from app.engines.Core import market_prediction as market_pred
except Exception:
    market_pred = None

def _looks_like_valuation(q: str) -> bool:
    return any(kw in q.lower() for kw in ["value", "valuation", "worth", "price", "estimate", "appraise"])

def _extract_address(q: str) -> str | None:
    m = re.search(r"\b(?:at|for)\s+([^,]+(?:, [^,]+){0,2})", q, flags=re.I)
    return m.group(1).strip() if m else None

def _detect_pool(q: str) -> bool:
    return "pool" in q.lower()

# --- Direct query entrypoint (NL → Engines) ---
import re
from app.engines.Core import valuation as valuation_engine
try:
    from app.engines.Core import market_prediction as market_pred
except Exception:
    market_pred = None


def _looks_like_valuation(q: str) -> bool:
    return any(kw in q.lower() for kw in ["value", "valuation", "worth", "price", "estimate", "appraise"])


def _extract_address(q: str) -> str | None:
    m = re.search(r"\b(?:at|for)\s+([^,]+(?:, [^,]+){0,2})", q, flags=re.I)
    return m.group(1).strip() if m else None


def _detect_pool(q: str) -> bool:
    return "pool" in q.lower()


async def route_query(prompt: str) -> dict:
    """
    Natural language → valuation engine (+ prediction overlay).
    """
    if _looks_like_valuation(prompt):
        address = _extract_address(prompt) or "123 Test St, Sydney"
        add_pool = _detect_pool(prompt)

        sales_revenue_hint = 1.0 + (0.06 if add_pool else 0.0)

        params = {
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

        result = valuation_engine.run(params)
        core = result.get("core_valuation", {})
        low, base, high = core.get("low"), core.get("base"), core.get("high")

        if isinstance(low, (int, float)) and isinstance(base, (int, float)) and isinstance(high, (int, float)):
            summary = f"Estimated value for **{address}**{' with a pool' if add_pool else ''}: ${base:,.0f} (range ${low:,.0f}–${high:,.0f})."
        else:
            summary = "Got a valuation, but couldn’t format the band."

        pred = None
        if market_pred:
            try:
                pred = market_pred.run(params)
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

    # fallback echo
    return {
        "status": "ok",
        "intent": "echo",
        "prompt": prompt,
        "message": f"AI stub: I received your prompt '{prompt}'"
    }