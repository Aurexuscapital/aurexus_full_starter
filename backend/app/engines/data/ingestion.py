from app.engines import register

def run(params: dict) -> dict:
    # e.g., pull from sources; stub.
    return {"ok": True, "engine": "data_ingestion", "params": params}

register(
    key="data_ingestion",
    fn=run,
    name="Data Ingestion / ETL",
    description="Load and normalize feeds from external sources."
)