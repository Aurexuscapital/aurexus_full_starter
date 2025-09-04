from app.engines import register

def run(params: dict) -> dict:
    return {
        "ok": True,
        "engine": "notifications",
        "params": params,
        "sent": True
    }

register(
    key="notifications",
    fn=run,
    name="Notifications / Workflow",
    description="Route tasks and notifications to users/systems."
)