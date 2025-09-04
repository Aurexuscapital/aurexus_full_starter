# app/engines/Core/test_market_prediction.py
import json

# import the engine's run()
from app.engines.Core.market_prediction import run as predict

def pretty(x):
    return json.dumps(x, indent=2, sort_keys=True)

def main():
    params = {
        "mode": "equity",
        "address": "123 Test St, Sydney",
        # optional signals (same shapes your valuation engine passes in)
        "liquidity": {"spread_bps": 80, "depth_units": 30000, "turnover_24h_pct": 1.2},
        "macro": {"discount_rate_delta_bps": 0},
        "climate_signals": {"enso_phase": "neutral", "rain_anom_pct": 5},
        "demand": {
            "watchlist_count": 120,
            "bids_24h": 25,
            "active_users_24h": 60,
            "external_index": 1.05
        },
    }

    print("=== MARKET PREDICTION TEST ===")
    res = predict(params)
    print(pretty(res))

    # quick human summary
    f1w = res.get("forecast_1w")
    f1m = res.get("forecast_1m")
    if isinstance(f1w, (int, float)) and isinstance(f1m, (int, float)):
        print(f"\nΔ price (1w): {f1w:+.2%} | Δ price (1m): {f1m:+.2%}")

if __name__ == "__main__":
    main()
    