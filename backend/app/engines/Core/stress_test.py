from app.engines import register

def run(params: dict) -> dict:
    return {"ok": True, "engine": "stress_test", "params": params}

register(
    key="stress_test",
    fn=run,
    name="Stress Test",
    description="Shock key inputs (rates, rents, capex) to test resilience."
)