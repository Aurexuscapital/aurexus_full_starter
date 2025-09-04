from app.engines import register

def run(params: dict) -> dict:
    return {"ok": True, "engine": "order_matching", "params": params}

register(
    key="order_matching",
    fn=run,
    name="Order Matching",
    description="Match bids/asks; allocate fills under market rules."
)