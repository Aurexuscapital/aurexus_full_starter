from app.engines import register

def run(params: dict) -> dict:
    return {
        "ok": True,
        "engine": "macro_overlay",
        "params": params,
        "overlay": {"rates": "stub", "macro": "stub"}
    }

register(
    key="macro_overlay",
    fn=run,
    name="Macro Overlay",
    description="Apply macro scenarios and overlays to valuations/returns."
)