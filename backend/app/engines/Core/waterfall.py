from app.engines import register

def run(params: dict) -> dict:
    return {"ok": True, "engine": "waterfall", "params": params}

register(
    key="waterfall",
    fn=run,
    name="Waterfall / Distributions",
    description="Model distributions across the capital stack and hurdles."
)