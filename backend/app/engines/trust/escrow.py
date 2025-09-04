from app.engines import register

def run(params: dict) -> dict:
    # e.g., hold/release with milestone checks; stub only.
    return {"ok": True, "engine": "escrow", "params": params}

register(
    key="escrow",
    fn=run,
    name="Escrow",
    description="Hold and release funds based on milestones and oracles."
)