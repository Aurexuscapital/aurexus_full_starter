from app.engines import register

def run(params: dict) -> dict:
    return {"ok": True, "engine": "resale", "params": params}

register(
    key="resale",
    fn=run,
    name="Resale",
    description="List/settle secondary trades for units/interests."
)