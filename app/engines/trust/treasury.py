from app.engines import register

def run(params: dict) -> dict:
    return {"ok": True, "engine": "treasury", "params": params}

register(
    key="treasury",
    fn=run,
    name="Treasury",
    description="Cash management, ladders, liquidity buffers."
)