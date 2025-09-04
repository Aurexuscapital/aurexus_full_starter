from app.engines import register

def run(params: dict) -> dict:
    return {
        "ok": True,
        "engine": "data_quality",
        "params": params,
        "issues": []
    }

register(
    key="data_quality",
    fn=run,
    name="Data Quality / Anomaly",
    description="Rules and anomaly detection on ingested data."
)