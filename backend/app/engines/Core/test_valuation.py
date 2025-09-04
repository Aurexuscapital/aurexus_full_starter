# app/engines/Core/test_valuation.py
from __future__ import annotations
import json

# Ensure the comps engine registers itself in the REGISTRY before we call valuation
import app.engines.Core.comps  # noqa: F401

from app.engines.Core.valuation import run

def pretty(x):
    return json.dumps(x, indent=2, sort_keys=False)

def main():
    print("\n=== EQUITY TEST ===")
    equity_params = {
        "mode": "equity",
        "address": "123 Test St, Sydney",
        "bedrooms": 3,
        "bathrooms": 2.0,
        "living_area_sqft": 1500,
        # project economics (for DCF & residual)
        "land_cost": 50_000,
        "build_cost": 700_000,
        "soft_costs": 150_000,
        "sales_revenue": 1_600_000,
        "exit_year": 2026,
        "discount_rate_equity": 0.12,
        # overlays
        "use_comps": True,            # use the comps engine (synthetic for now)
        "comps_radius_km": 1.6,       # ~1 mile
        "blend_comps": 0.8,           # weight comps higher than hedonic
        "blend_hedonic": 0.2,
        # optional market/demand signals (to move token price vs NAV a bit)
        "liquidity": {"spread_bps": 80, "depth_units": 30000, "turnover_24h_pct": 1.2},
        "demand": {"watchlist_count": 120, "bids_24h": 25, "active_users_24h": 60, "external_index": 1.05},
        "tokens_outstanding": 1_000_000,
    }
    print(pretty(run(equity_params)))

    print("\n=== CREDIT TEST ===")
    credit_params = {
        "mode": "credit",
        "address": "1 Example Rd, Sydney",     # required by the schema
        "loan_amount": 800_000,
        "coupon_apr": 0.10,
        "tenor_months": 24,
        "schedule": "bullet",
        "collateral": {"value_override": 1_500_000},
        "tokens_outstanding": 500_000,
        # optional demand/liquidity just to exercise pricing path
        "liquidity": {"spread_bps": 60, "depth_units": 50000, "turnover_24h_pct": 2.0},
        "demand": {"watchlist_count": 80, "bids_24h": 12, "active_users_24h": 40},
    }
    print(pretty(run(credit_params)))

if __name__ == "__main__":
    main()