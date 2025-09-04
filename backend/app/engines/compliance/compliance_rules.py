from app.engines import register

def run(params: dict) -> dict:
    return {"ok": True, "engine": "compliance_rules", "params": params, "violations": []}

register(
    key="compliance_rules",
    fn=run,
    name="Compliance Rules",
    description="Evaluate jurisdiction/product rules and constraints."
)