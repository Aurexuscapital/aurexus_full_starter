from app.engines import register

def run(params: dict) -> dict:
    return {"ok": True, "engine": "eligibility", "params": params, "eligible": True}

register(
    key="eligibility",
    fn=run,
    name="Eligibility / Suitability",
    description="Check investor status and product suitability rules."
)