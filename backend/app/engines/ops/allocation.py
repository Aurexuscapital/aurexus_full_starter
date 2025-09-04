from app.engines import register

def run(params: dict) -> dict:
    return {"ok": True, "engine": "allocation", "params": params}

register(
    key="allocation",
    fn=run,
    name="Allocation / Matching",
    description="Allocate inventory across orders or investor buckets."
)