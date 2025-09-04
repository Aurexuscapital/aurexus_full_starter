from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.api.deps import require_admin
from app.engines import REGISTRY, list_engines  # <-- from __init__.py

router = APIRouter(
    prefix="/engines",
    tags=["engines"],
    dependencies=[Depends(require_admin)],
)

class EngineRunIn(BaseModel):
    name: str   # engine key, e.g. "deal_screen"
    params: Optional[Dict[str, Any]] = None

class EngineRunOut(BaseModel):
    run_id: str
    name: str
    status: str
    params: Dict[str, Any] | None = None
    result: Dict[str, Any] | None = None
    error: str | None = None

RUNS: Dict[str, EngineRunOut] = {}

@router.get("/list")
def list_all_engines():
    """Return all registered engines (from __init__.py)"""
    return list_engines()

@router.post("/run")
def run_engine(payload: EngineRunIn):
    if payload.name not in REGISTRY:
        raise HTTPException(status_code=404, detail="Unknown engine")
    fn = REGISTRY[payload.name]

    try:
        result = fn(payload.params or {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    out = EngineRunOut(
        run_id=payload.name + "-dummy-id",  # replace later w/ uuid
        name=payload.name,
        status="done",
        params=payload.params,
        result=result,
        error=None
    )
    RUNS[out.run_id] = out
    return out

@router.get("/{run_id}/status")
def run_status(run_id: str):
    if run_id not in RUNS:
        raise HTTPException(status_code=404, detail="Run not found")
    return RUNS[run_id]