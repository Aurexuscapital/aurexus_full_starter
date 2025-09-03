from app.engines import register

def run(params: dict) -> dict:
    # This can orchestrate other engines later.
    return {"ok": True, "engine": "ai_agent", "params": params, "transcript": ["Agent stub."]}

register(
    key="ai_agent",
    fn=run,
    name="AI Agent",
    description="Autonomous negotiator/orchestrator that can call other engines."
)