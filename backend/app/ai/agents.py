# app/ai/agents.py
from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
import json
import time

from app.ai.config import AgentSpec

class AgentError(Exception):
    pass

class BaseAgent:
    def __init__(self, spec: AgentSpec):
        self.spec = spec

    def run(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raise NotImplementedError

class EngineAgent(BaseAgent):
    """
    Deterministic adapter that calls your local engines (valuation, comps, risk).
    """
    def run(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        from app.engines import REGISTRY
        payload = (context or {}).get("payload") or {}
        tool = payload.get("tool")
        params = payload.get("params") or {}

        fn = REGISTRY.get(tool)
        if not fn:
            raise AgentError(f"Engine '{tool}' not found")
        try:
            result = fn(params)
            return {"status": "ok", "engine": tool, "result": result}
        except Exception as e:
            return {"status": "error", "engine": tool, "error": str(e)}

class LLMJsonAgent(BaseAgent):
    """
    Tool-calling JSON agent (stub). Replace the _call_model() with your LLM client.
    Must return valid JSON (dict).
    """
    def run(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        plan = self._call_model(prompt=prompt, context=context)
        # Validate JSON
        if not isinstance(plan, dict):
            raise AgentError("Planner returned non-JSON.")
        return plan

    def _call_model(self, prompt: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        # TODO: swap with your LLM API (OpenAI, Anthropic, Groq, etc.)
        # For now, return a deterministic “plan” for local engines.
        intent = (context or {}).get("intent") or "valuation"
        if intent == "valuation":
            return {
                "type": "plan",
                "steps": [
                    {"tool": "comps", "params": {
                        "address": (context or {}).get("address"),
                        "radius_miles": 1.0, "limit": 8
                    }},
                    {"tool": "valuation", "params": {
                        "mode": "equity",
                        "address": (context or {}).get("address"),
                        "bedrooms": (context or {}).get("bedrooms"),
                        "bathrooms": (context or {}).get("bathrooms"),
                        "living_area_sqft": (context or {}).get("sqft"),
                        "use_comps": True,
                        "comps_radius_km": 1.6,
                        "blend_comps": 0.8,
                        "blend_hedonic": 0.2
                    }},
                ],
                "narrative_prompt": "Explain the result in 2 short paragraphs."
            }
        # default
        return {"type": "plan", "steps": [], "narrative_prompt": "Summarize briefly."}

class LLMNarrativeAgent(BaseAgent):
    """
    Narrative agent (stub): turns structured results into user-facing prose.
    """
    def run(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # TODO: replace with your LLM call. For now, synthesize a simple paragraph.
        result = (context or {}).get("result") or {}
        try:
            base = result.get("core_valuation", {}).get("base")
            low = result.get("core_valuation", {}).get("low")
            high = result.get("core_valuation", {}).get("high")
            addr = (context or {}).get("address") or "the property"
            narrative = (
                f"For {addr}, our engines estimate a value around ${base:,.0f} "
                f"(range ${low:,.0f}–${high:,.0f}). This blends comps with a hedonic model, "
                f"and adjusts for progress, liquidity, and macro assumptions."
            )
        except Exception:
            narrative = "Here is your result. (Narrative agent failed to read structure.)"
        return {"status": "ok", "narrative": narrative, "model": self.spec.model}

def make_agent(spec: AgentSpec) -> BaseAgent:
    if spec.style == "json":
        return LLMJsonAgent(spec)
    if spec.style == "narrative":
        return LLMNarrativeAgent(spec)
    # For “classifier” or others, you’d add more classes later.
    return LLMJsonAgent(spec)