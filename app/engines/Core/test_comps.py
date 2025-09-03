from __future__ import annotations
import json
from app.engines.Core import comps  # ensures register() runs
from app.engines import REGISTRY

def _coerce_jsonable(obj):
    if obj is Ellipsis:
        return None
    if isinstance(obj, dict):
        return {k: _coerce_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_coerce_jsonable(x) for x in obj]
    return obj

def pretty(x):
    try:
        return json.dumps(x, indent=2, sort_keys=True)
    except TypeError:
        return json.dumps(_coerce_jsonable(x), indent=2, sort_keys=True, default=str)

def main():
    run = REGISTRY.get("comps")
    if not run:
        raise RuntimeError("Comps engine not found in REGISTRY. Did comps.register(...) run?")

    params = {
        "address": "123 Test St, Sydney NSW",
        "radius_miles": 1.0,
        "limit": 6,
    }

    print("=== COMPS TEST ===")
    raw_result = run(params)

    # Coerce once and use the SAFE version for everything
    result = _coerce_jsonable(raw_result)
    print(pretty(result))

    comps_list = (result or {}).get("comps") or (result or {}).get("results") or []
    if not comps_list:
        print("\n(No comps returned — if your engine requires API keys, this is expected.)")
        return

    # Only use dict-like items
    pairs = []
    for c in comps_list:
        if not isinstance(c, dict):
            continue
        price = c.get("price")
        sqft = c.get("sqft") or c.get("living_area_sqft")
        if price and sqft:
            pairs.append(price / max(sqft, 1))

    if pairs:
        pairs.sort()
        mid = pairs[len(pairs)//2] if len(pairs) % 2 else 0.5*(pairs[len(pairs)//2 - 1] + pairs[len(pairs)//2])
        print(f"\nMedian $/sf from comps: {mid:,.2f}")
    else:
        print("\nNo price/sqft pairs found to compute $/sf.")

if __name__ == "__main__":
    main()