# app/ai/config.py
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class AgentSpec:
    key: str
    role: str
    model: str                      # placeholder, e.g., "gpt-4o" / "sonnet" / etc.
    style: str                      # "json" (tool-calling) | "narrative" | "classifier"
    temperature: float = 0.2
    max_tokens: int = 1500
    tools: Optional[List[str]] = None  # names of engines or tool capabilities

# Define your “bench” of agents.
AGENTS: Dict[str, AgentSpec] = {
    # JSON/tool agent used to orchestrate engines & return structured outputs
    "planner_json": AgentSpec(
        key="planner_json",
        role="Tool-using planner that returns strict JSON for downstream engines.",
        model="REPLACE_ME_JSON_MODEL",
        style="json",
        temperature=0.1,
        tools=["valuation", "comps", "market_prediction", "risk"]
    ),
    # Narrative agent: turns numbers into user-facing prose
    "narrative": AgentSpec(
        key="narrative",
        role="Explains results to a non-technical user; calm, concise, compliant.",
        model="REPLACE_ME_NARRATIVE_MODEL",
        style="narrative",
        temperature=0.5,
        max_tokens=900
    ),
    # Classifier: routes intents (free vs premium, valuation vs scenario, etc.)
    "classifier": AgentSpec(
        key="classifier",
        role="Classifies the user request into a small set of intents.",
        model="REPLACE_ME_CLASSIFIER_MODEL",
        style="classifier",
        temperature=0.0,
        max_tokens=300
    ),
}

# Simple policy for which agent to use per intent
INTENT_POLICY: Dict[str, List[str]] = {
    "valuation": ["planner_json", "narrative"],
    "comps": ["planner_json", "narrative"],
    "scenario_sim": ["planner_json", "narrative"],
    "market_outlook": ["planner_json", "narrative"],
    "risk": ["planner_json", "narrative"],
    "fallback": ["planner_json"],
}