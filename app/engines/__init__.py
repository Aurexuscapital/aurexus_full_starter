from __future__ import annotations

from typing import Callable, Dict, List, Optional
import importlib
import pkgutil
from pathlib import Path

# --- Engine registry ---
REGISTRY: Dict[str, Callable[[dict, object | None], dict]] = {}
META: Dict[str, dict] = {}

def register(key: str, fn: Callable[[dict, object | None], dict], description: str = "", name: Optional[str] = None) -> None:
    """Register an engine runner under a key."""
    REGISTRY[key] = fn
    META[key] = {
        "name": name or key.replace("_", " ").title(),
        "description": description or "",
    }

def list_engines() -> List[dict]:
    """Return a list of registered engines for /engines/list."""
    out: List[dict] = []
    for k in sorted(REGISTRY.keys()):
        meta = META.get(k, {})
        out.append({
            "key": k,
            "name": meta.get("name", k),
            "description": meta.get("description", ""),
        })
    return out

def discover() -> None:
    """
    Import all submodules under app.engines.* so each module can call register().
    """
    base_pkg = __name__               # "app.engines"
    base_path = Path(__file__).parent # app/engines/

    for _finder, modname, _ispkg in pkgutil.walk_packages([str(base_path)], prefix=base_pkg + "."):
        importlib.import_module(modname)
def discover_engines():
    """Auto-import all engine modules so they can self-register."""
    pkg_dir = Path(__file__).resolve().parent
    for _, module_name, _ in pkgutil.walk_packages([str(pkg_dir)], prefix="app.engines."):
        try:
            importlib.import_module(module_name)
        except Exception as e:
            print(f"[engine discovery] Failed loading {module_name}: {e}")

# Trigger discovery at import
discover_engines()
