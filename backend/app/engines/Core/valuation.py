# app/engines/core/valuation.py
from __future__ import annotations
import math, random, statistics
from typing import Any, Dict, Optional, Sequence, Tuple
from pydantic import BaseModel, Field, ValidationError

from app.engines import register, REGISTRY

# -------------------------- Pydantic Schemas --------------------------

class Progress(BaseModel):
    stage: Optional[str] = Field(None, description="planning|finance|groundworks|structure|services|fitout|pc|settlements")
    percent: Optional[float] = Field(0.0, ge=0.0, le=1.0)
    planned_completion_months: Optional[float] = 12.0
    expected_completion_months: Optional[float] = None  # if None, we derive via climate_signals

class Sales(BaseModel):
    presold_pct: Optional[float] = Field(None, ge=0.0, le=1.0)
    avg_price_vs_model: Optional[float] = Field(1.0, description="Multiplier vs feasibility model, e.g. 1.02 = +2%")

class Costs(BaseModel):
    build_cost: Optional[float] = None
    soft_costs: Optional[float] = None
    actual_vs_budget: Optional[float] = Field(1.0, description=">1 means over budget")
    contingency_remaining_pct: Optional[float] = Field(None, ge=0.0, le=1.0)

class Liquidity(BaseModel):
    spread_bps: Optional[int] = 120
    depth_units: Optional[int] = 0
    turnover_24h_pct: Optional[float] = 0.0
class ClimateSignals(BaseModel):
    enso_phase: Optional[str] = Field(None, description="el_nino|la_nina|neutral")
    rain_anom_pct: Optional[float] = Field(0.0, description="Percent rainfall anomaly vs median, e.g. 15 = +15%")

class MacroOverlay(BaseModel):
    discount_rate_delta_bps: Optional[int] = 0  # e.g., +25 bps raises discount rate => lower value

class Collateral(BaseModel):
    value_override: Optional[float] = None
    noi_annual: Optional[float] = None        # for DSCR/ICR if income-producing
    capex_remaining: Optional[float] = None

class Covenants(BaseModel):
    max_ltv: Optional[float] = None
    min_dscr: Optional[float] = None
    min_icr: Optional[float] = None




class MarketDemand(BaseModel):
    # Simple signals — you can feed these from your marketplace later
    watchlist_count: Optional[int] = 0
    bids_24h: Optional[int] = 0
    bid_volume: Optional[float] = 0.0
    ask_volume: Optional[float] = 0.0
    active_users_24h: Optional[int] = 0
    external_index: Optional[float] = Field(1.0, description="Optional exogenous demand index around 1.0")

def _compute_demand_index(demand: MarketDemand | None, liq: Liquidity | None) -> float:
    """
    Returns a multiplier ~ 0.7 .. 1.5 (1.0 = neutral).
    Combines marketplace demand with liquidity conditions.
    """
    if demand is None:
        demand = MarketDemand()
    if liq is None:
        liq = Liquidity()

    # Normalize demand signals
    wl = min((demand.watchlist_count or 0) / 500.0, 1.0)         # 0..1 at 500 watchlists
    bids = min((demand.bids_24h or 0) / 100.0, 1.0)               # 0..1 at 100 bids/day
    users = min((demand.active_users_24h or 0) / 200.0, 1.0)      # 0..1 at 200 actives
    vol_sum = (demand.bid_volume or 0.0) + (demand.ask_volume or 0.0)
    imb = 0.0
    if vol_sum > 0:
        imb = ((demand.bid_volume or 0.0) - (demand.ask_volume or 0.0)) / vol_sum   # -1..+1
    imb = (imb + 1) / 2.0  # map to 0..1 (buying pressure)

    # Liquidity modifiers (tighter spread + deeper book → higher effective demand)
    spread = float(liq.spread_bps or 120.0)
    depth  = float(liq.depth_units or 0.0)
    turn   = float(liq.turnover_24h_pct or 0.0)
    liq_boost = 1.0
    if spread < 30:  liq_boost += 0.05
    if depth  > 50000: liq_boost += 0.05
    if turn   > 3.0: liq_boost += 0.03

    ext = float(demand.external_index or 1.0)  # around 1.0

    # Blend: base 1.0 + weighted demand (0..1) then apply liq + external
    raw = 1.0 + 0.35*wl + 0.30*bids + 0.20*users + 0.15*imb
    out = raw * liq_boost * ext

    # Clamp to keep stable
    return max(0.7, min(1.5, out))

def _price_from_nav(nav_per_token: float, demand_idx: float, alpha: float = 0.6) -> float:
    """
    Translate NAV to a market price by tilting with demand:
      price = NAV * (1 + alpha * (demand_idx - 1))
    alpha governs elasticity (0=no effect, 1=full).
    """
    if nav_per_token is None:
        return 0.0
    price = nav_per_token * (1.0 + alpha * (demand_idx - 1.0))
    return max(0.0, price)

# ----- UPDATE your ValuationParams: just add `demand` -----
# (Replace your current ValuationParams with this version)

class ValuationParams(BaseModel):
    # mode & core facts
    mode: str = Field(..., description="equity|credit")
    address: str
    bedrooms: Optional[int] = Field(None, ge=0)
    bathrooms: Optional[float] = Field(None, ge=0)
    living_area_sqft: Optional[int] = Field(None, ge=0)
    year_built: Optional[int] = Field(None, ge=1800, le=2100)

    # equity
    land_cost: Optional[float] = None
    build_cost: Optional[float] = None
    soft_costs: Optional[float] = None
    sales_revenue: Optional[float] = None
    exit_year: Optional[int] = None
    discount_rate_equity: Optional[float] = 0.12
    debt_outstanding: Optional[float] = 0.0

    # credit
    loan_amount: Optional[float] = None
    coupon_apr: Optional[float] = None        # decimal, e.g. 0.12
    tenor_months: Optional[int] = None
    schedule: Optional[str] = "bullet"         # bullet|amortising
    discount_rate_credit: Optional[float] = 0.10

    # options/overlays
    use_comps: Optional[bool] = False
    comps_radius_km: Optional[float] = 2.0
    blend_comps: Optional[float] = 0.6
    blend_hedonic: Optional[float] = 0.4

    progress: Optional[Progress] = None
    sales: Optional[Sales] = None
    costs: Optional[Costs] = None
    liquidity: Optional[Liquidity] = None
    climate_signals: Optional[ClimateSignals] = None
    macro: Optional[MacroOverlay] = None
    collateral: Optional[Collateral] = None
    covenants: Optional[Covenants] = None

    # demand signals for token pricing
    demand: Optional[MarketDemand] = None

    tokens_outstanding: Optional[int] = 1_000_000
# -------------------------- Utilities --------------------------

def _dump_model(m: BaseModel | None) -> Dict[str, Any] | None:
    if m is None: return None
    return m.model_dump() if hasattr(m, "model_dump") else m.dict()

def _percentiles(data: Sequence[float], qs: Sequence[float]) -> list[float]:
    if not data:
        return [math.nan for _ in qs]
    xs = sorted(data)
    n = len(xs)
    out = []
    for q in qs:
        if q <= 0: out.append(xs[0]); continue
        if q >= 1: out.append(xs[-1]); continue
        i = q * (n - 1)
        lo, hi = math.floor(i), math.ceil(i)
        if lo == hi:
            out.append(xs[lo])
        else:
            w = i - lo
            out.append(xs[lo]*(1-w) + xs[hi]*w)
    return out

def _lognormal_mult(mu_pct: float = 0.0, sigma_pct: float = 0.10) -> float:
    mu = math.log(1 + mu_pct)
    sigma = sigma_pct
    return math.exp(random.gauss(mu, sigma))


# -------------------------- Core valuation math (deterministic) --------------------------

# -------------------------- Equity DCF (cashflows, IRR/NPV) --------------------------

def compute_equity_cashflows_and_irr(
    land_cost: float | None,
    build_cost: float | None,
    soft_costs: float | None,
    sales_revenue: float | None,
    exit_year: int | None,
    discount_rate: float,
    timeline_months: int = 24,
    presale_pct: float = 0.0,
    presale_deposit_pct: float = 0.10,
    spend_curve: str = "s-curve",   # "linear"|"front"|"back"|"s-curve"
) -> dict:
    """
    Build a simple monthly pro forma for a development:
      - Month 0: land outflow (if provided)
      - Months 1..T: build + soft outflows on a spend curve
      - Presale deposits (inflows) during construction (non-recourse to revenue)
      - Settlement inflow at exit: remaining sales revenue
    Returns: cashflows (monthly), annual CF summary, equity IRR, NPV, equity multiple (EM)
    """
    T = max(1, int(timeline_months or 24))
    r_m = (1 + discount_rate) ** (1/12) - 1

    L = float(land_cost or 0.0)
    B = float(build_cost or 0.0)
    S = float(soft_costs or 0.0)
    R = float(sales_revenue or 0.0)

    # Spend curve weights over T months
    import math as _m
    if spend_curve == "linear":
        w = [_ for _ in [1]*T]
    elif spend_curve == "front":
        w = [max(1, int(T - i)) for i in range(T)]
    elif spend_curve == "back":
        w = [max(1, int(i + 1)) for i in range(T)]
    else:  # s-curve
        # normalized logistic-ish curve
        w = [1/(1+_m.exp(-12*((i+0.5)/T-0.5))) for i in range(T)]
    wsum = sum(w)
    w = [x/wsum for x in w]

    monthly_build = [B * wi for wi in w]
    monthly_soft  = [S * wi for wi in w]

    # Presale deposits during build (not full revenue)
    presale = min(max(presale_pct, 0.0), 1.0)
    depo = presale_deposit_pct
    presale_inflows = [ (R * presale * depo) / T for _ in range(T) ]

    # Settlement inflow at completion (remaining revenue)
    settlement = R * (1 - presale*depo)

        # Assemble monthly cashflows (equity perspective, negative = outflow)
    cfs_m = [-L]  # month 0 land
    for m in range(1, T + 1):  # months 1..T construction
        cfs_m.append(
            -monthly_build[m - 1]
            - monthly_soft[m - 1]
            + presale_inflows[m - 1]
        )
    cfs_m.append(settlement)  # month T+1: settlement inflow

    # IRR (monthly) via bisection, then annualize
    def _npv(rate_m: float) -> float:
        return sum(cf / ((1 + rate_m) ** t) for t, cf in enumerate(cfs_m))
    lo, hi = -0.95, 2.0
    f_lo, f_hi = _npv(lo), _npv(hi)
    irr_m = None
    if f_lo * f_hi <= 0:
        for _ in range(100):
            mid = 0.5*(lo+hi)
            f_mid = _npv(mid)
            if abs(f_mid) < 1e-10:
                irr_m = mid
                break
            if f_lo * f_mid < 0:
                hi, f_hi = mid, f_mid
            else:
                lo, f_lo = mid, f_mid
        if irr_m is None:
            irr_m = 0.5*(lo+hi)
    irr_a = (1 + (irr_m or 0.0))**12 - 1

    # NPV at equity discount rate
    npv = sum(cf / ((1 + r_m) ** t) for t, cf in enumerate(cfs_m))

    invested = -sum(min(0.0, cf) for cf in cfs_m)
    returned = sum(max(0.0, cf) for cf in cfs_m)
    em = (returned / invested) if invested > 0 else None

    # Group to simple annual view
    annual = {}
    for t, cf in enumerate(cfs_m):
        yr = t // 12
        annual[yr] = annual.get(yr, 0.0) + cf

    return {
        "cashflows_monthly": cfs_m,
        "cashflows_annual": [{"year": y, "cf": v} for y, v in sorted(annual.items())],
        "irr_annual": irr_a,
        "npv": npv,
        "equity_multiple": em,
        "assumptions": {
            "timeline_months": T,
            "spend_curve": spend_curve,
            "presale_pct": presale,
            "presale_deposit_pct": depo,
            "discount_rate_equity": discount_rate,
        },
    }


def compute_hedonic(p: ValuationParams) -> float:
    addr = (p.address or "").lower()
    base_psf = 9500 if "sydney" in addr else 8000 if "melbourne" in addr else 6500 if "brisbane" in addr else 6000
    sqft = float(p.living_area_sqft or 1000)
    beds = float(p.bedrooms or 0)
    baths = float(p.bathrooms or 0.0)
    year = int(p.year_built or 2000)

    v = base_psf * sqft
    v *= (1 + 0.05 * beds)
    v *= (1 + 0.03 * baths)
    age = max(0, 2025 - year)
    if age > 40: v *= 0.90
    elif age > 20: v *= 0.95
    return float(v)

def compute_residual_land_value(p: ValuationParams) -> Optional[float]:
    if p.sales_revenue is None or p.build_cost is None:
        return None
    soft = p.soft_costs or 0.0
    finance = 0.05 * (p.build_cost + soft)    # placeholder
    dev_margin = 0.15 * p.sales_revenue       # placeholder
    return float(p.sales_revenue - (p.build_cost + soft + finance + dev_margin))

def compute_comps_value(p: ValuationParams) -> tuple[Optional[float], list[dict]]:
    """
    Try to call a 'comps' engine if present; else return None.
    Expect comps engine: run({"address":..., "radius_miles":..., "limit":...}) -> list of sales with price/size.
    """
    if not p.use_comps:
        return None, []
    comps_run = REGISTRY.get("comps")
    if not comps_run:
        return None, []
    try:
        resp = comps_run({
            "address": p.address,
            "radius_miles": max(0.1, float((p.comps_radius_km or 2.0) * 0.621371)),
            "limit": 8
        }) or {}
        comps = resp.get("comps") or resp.get("results") or []
        # naive median psf → value
        sqft = float(p.living_area_sqft or 1000)
        psfs = [
            c.get("price", 0.0) /
            max(c.get("sqft") or c.get("living_area_sqft") or 1, 1)
            for c in comps if c.get("price")
        ]
        if not psfs:
            return None, comps
        psf_med = statistics.median(psfs)
        return float(psf_med * sqft), comps
    except Exception:
        return None, []

def apply_macro_delta(value: float, macro: MacroOverlay | None) -> float:
    """
    Simple sensitivity: every +100 bps on discount rate reduces value by ~5% (tunable).
    """
    if not macro or not macro.discount_rate_delta_bps:
        return value
    bps = macro.discount_rate_delta_bps or 0
    sens_per_100bps = -0.05
    factor = 1.0 + sens_per_100bps * (bps / 100.0)
    return max(0.0, value * factor)

def progress_delay_months(progress: Progress | None, climate: ClimateSignals | None) -> float:
    if not progress:
        return 0.0
    planned = float(progress.planned_completion_months or 12.0)
    if progress.expected_completion_months is not None:
        return max(0.0, float(progress.expected_completion_months) - planned)

    # derive from climate signals (very rough starter)
    rain = float((climate or ClimateSignals()).rain_anom_pct or 0.0)
    enso = (climate.enso_phase.lower() if (climate and climate.enso_phase) else "neutral")
    stage = (progress.stage or "structure").lower()
    base_by_stage = {"groundworks": 0.8, "structure": 0.5, "services": 0.3, "fitout": 0.2}
    base = base_by_stage.get(stage, 0.3)
    phase_adj = {"el_nino": 0.2, "la_nina": 0.6, "neutral": 0.0}.get(enso, 0.0)
    k = 0.01  # months per +1% rainfall anomaly
    extra = k * max(0.0, rain)
    return base + phase_adj + extra

def liquidity_premium(liq: Liquidity | None) -> float:
    if not liq:
        return 0.0
    spread = int(liq.spread_bps or 120)
    depth = int(liq.depth_units or 0)
    turnover = float(liq.turnover_24h_pct or 0.0)
    if spread < 20 and depth > 100000 and turnover > 5:
        return +0.005   # +0.5%
    if spread > 150 or depth < 5000:
        return -0.015   # -1.5%
    return 0.0

def apply_progress_and_delay(value: float, progress: Progress | None, finance_apr: float = 0.10, climate: ClimateSignals | None = None) -> tuple[float, dict]:
    pct = float((progress.percent if progress and progress.percent is not None else 0.0))
    base_disc = 0.08
    disc_progress = base_disc * (1 - max(0.0, min(1.0, pct)))
    delta_m = progress_delay_months(progress, climate)
    penalty_delay = (finance_apr / 12.0) * max(0.0, delta_m)
    v = value * (1 - disc_progress) * (1 - penalty_delay)
    return v, {"progress_discount": disc_progress, "delay_months": delta_m, "delay_penalty": penalty_delay}

def build_token_nav(project_value: float, debt: float = 0.0, tokens_out: int = 1_000_000) -> Dict[str, float]:
    nav_equity = max(project_value - (debt or 0.0), 0.0)
    nav_per_token = nav_equity / max(tokens_out, 1)
    return {"nav_equity": nav_equity, "nav_per_token": nav_per_token}
   

def _tokenize_from_value(core_value: float, tokens_out: int) -> Dict[str, Any]:
    """MVP: base token price = equity NAV / tokens_out."""
    base_price = max(core_value, 0.0) / max(tokens_out, 1)
    return {
        "token_supply": int(max(tokens_out, 1)),
        "base_price": float(base_price),
        # hint for hourly pricing engine
        "hourly_mark_hint": {
            "formula": "final = base_price * (1 + demand_k) * (1 - macro_penalty_k)",
            "inputs_needed": ["demand_k", "macro_penalty_k"]
        }
    }

def _risk_score_from_band(low: float, mid: float, high: float) -> Dict[str, Any]:
    """Simple dispersion-based score: tighter band => lower risk. 0 (low) .. 100 (high)."""
    mid = float(mid or 0.0); low = float(low or 0.0); high = float(high or 0.0)
    spread = max(high - low, 0.0)
    denom = max(mid, 1.0)
    pct_spread = min(spread / denom, 1.0)   # cap at 100%
    score = int(round(100 * pct_spread))    # 0..100
    return {"risk_score": score, "band_spread_pct": pct_spread}

def _investor_summary(mode: str, band: Dict[str, float], irr=None, npv=None, em=None) -> str:
    l = band.get("low"); m = band.get("base"); h = band.get("high")
    if mode == "equity":
        irr_txt = f", IRR ~ {irr:.1%}" if isinstance(irr, (int, float)) and irr is not None else ""
        em_txt  = f", EM ~ {em:.2f}" if isinstance(em, (int, float)) and em is not None else ""
        return (
            f"Equity valuation: base ${m:,.0f} (range ${l:,.0f}–${h:,.0f}){irr_txt}{em_txt}. "
            f"Band reflects sales/cost/delay uncertainty. Liquidity & macro overlays applied."
        )
    else:
        irr_txt = f", IRR ~ {irr:.1%}" if isinstance(irr, (int, float)) and irr is not None else ""
        return (
            f"Credit valuation (price band): base ${m:,.0f} (range ${l:,.0f}–${h:,.0f}){irr_txt}. "
            f"Band reflects PD/LGD & rate spread shocks. Liquidity & macro overlays applied."
        )

def _developer_offer(core_value: float, leverage_ratio: float | None, risk_score: int) -> Dict[str, Any]:
    """Rough term sheet hint based on risk_score."""
    if risk_score <= 30:
        max_ltv, coupon = 0.55, 0.10
    elif risk_score <= 60:
        max_ltv, coupon = 0.50, 0.12
    else:
        max_ltv, coupon = 0.45, 0.14
    facility_cap = core_value * max_ltv
    suggested = {
        "max_ltv": max_ltv,
        "coupon_apr": coupon,
        "facility_cap": facility_cap,
        "notes": "Auto-hint; final terms subject to risk engine & credit committee."
    }
    if leverage_ratio is not None:
        suggested["observed_leverage"] = leverage_ratio
    return suggested



# -------------------------- Credit math --------------------------

def _annual_debt_service(loan: float, apr: float, tenor_m: int, schedule: str) -> float:
    schedule = (schedule or "bullet").lower()
    if schedule == "amortising":
        # annual annuity over N years
        n_years = max(1, tenor_m) / 12.0
        r = max(0.000001, apr)
        ann = loan * (r * (1 + r)**n_years) / ((1 + r)**n_years - 1)
        return float(ann)
    # bullet interest-only
    return float(loan * apr)

def _irr_bisection(cfs: Sequence[float], lo: float = -0.95, hi: float = 1.0, iters: int = 80) -> Optional[float]:
    def npv(rate: float) -> float:
        return sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cfs))
    try:
        f_lo, f_hi = npv(lo), npv(hi)
        if f_lo * f_hi > 0:
            return None
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            f_mid = npv(mid)
            if abs(f_mid) < 1e-10: return mid
            if f_lo * f_mid < 0:
                hi, f_hi = mid, f_mid
            else:
                lo, f_lo = mid, f_mid
        return 0.5 * (lo + hi)
    except Exception:
        return None

def compute_credit_cashflows_and_irr(loan: float, apr: float, tenor_m: int, schedule: str) -> Dict[str, float]:
    tenor_y = tenor_m / 12.0
    if (loan or 0) <= 0 or (apr or 0) < 0 or tenor_y <= 0:
        return {"irr": None, "npv": None, "apy": None}

    if (schedule or "bullet").lower() == "amortising":
        # annual periods
        years = int(max(1, round(tenor_y)))
        r = apr
        ann = _annual_debt_service(loan, apr, tenor_m, "amortising")
        cfs = [-loan] + [ann for _ in range(years - 1)] + [ann]  # simple annual annuity
    else:
        # bullet: annual interest, principal at maturity
        years = int(max(1, round(tenor_y)))
        cfs = [-loan] + [loan * apr for _ in range(years - 1)] + [loan * (1 + apr)]

    irr = _irr_bisection(cfs)
    # NPV at discount_rate_credit ~ apr as placeholder
    disc = apr if apr and apr > 0 else 0.10
    npv = sum(cf / ((1 + disc) ** t) for t, cf in enumerate(cfs))
    return {"irr": irr, "npv": npv, "apy": apr}

def credit_metrics(collateral_value: Optional[float], loan: float, apr: float, tenor_m: int, schedule: str, noi_annual: Optional[float], build: Optional[float], soft: Optional[float]) -> dict:
    ds = _annual_debt_service(loan, apr, tenor_m, schedule)
    dscr = (noi_annual / ds) if (noi_annual and ds > 0) else None
    icr  = (noi_annual / (loan * apr)) if (noi_annual and loan > 0 and apr > 0) else None
    ltv  = (loan / collateral_value) if (collateral_value and collateral_value > 0) else None
    ltc  = (loan / ( (build or 0) + (soft or 0) )) if ( (build or 0) + (soft or 0) ) > 0 else None
    return {"ltv": ltv, "ltc": ltc, "dscr": dscr, "icr": icr, "debt_service_annual": ds}

def covenant_eval(metrics: dict, covenants: Optional[Covenants]) -> dict:
    cov = _dump_model(covenants) or {}
    breaches = []
    if metrics.get("ltv") is not None and cov.get("max_ltv") is not None and metrics["ltv"] > cov["max_ltv"]:
        breaches.append(f"LTV {metrics['ltv']:.2f} > {cov['max_ltv']:.2f}")
    if metrics.get("dscr") is not None and cov.get("min_dscr") is not None and metrics["dscr"] < cov["min_dscr"]:
        breaches.append(f"DSCR {metrics['dscr']:.2f} < {cov['min_dscr']:.2f}")
    if metrics.get("icr") is not None and cov.get("min_icr") is not None and metrics["icr"] < cov["min_icr"]:
        breaches.append(f"ICR {metrics['icr']:.2f} < {cov['min_icr']:.2f}")
    headroom = {
        "to_max_ltv": None if metrics.get("ltv") is None or cov.get("max_ltv") is None else cov["max_ltv"] - metrics["ltv"],
        "to_min_dscr": None if metrics.get("dscr") is None or cov.get("min_dscr") is None else metrics["dscr"] - cov["min_dscr"],
        "to_min_icr": None if metrics.get("icr") is None or cov.get("min_icr") is None else metrics["icr"] - cov["min_icr"],
    }
    return {"covenants": cov, "breaches": breaches, "headroom": headroom}

# -------------------------- Monte Carlo --------------------------

def monte_carlo_equity(base_value: float,
                       planned_months: float,
                       expected_months: float,
                       finance_apr: float = 0.10,
                       sales_vol: float = 0.08,
                       cost_vol: float = 0.06,
                       delay_sd_months: float = 1.0,
                       liq_premium: float = 0.0,
                       n: int = 3000) -> Tuple[float, float, float, dict]:
    if base_value <= 0 or n <= 0:
        return (base_value, base_value, base_value, {"samples": 0})
    baseline_delay = max(0.0, (expected_months or planned_months) - (planned_months or 0.0))
    monthly_carry = finance_apr / 12.0
    samples = []
    for _ in range(n):
        sales_mult = _lognormal_mult(0.0, sales_vol)
        cost_mult  = _lognormal_mult(0.0, cost_vol)
        delay_noise = max(0.0, random.gauss(baseline_delay, delay_sd_months))
        delay_penalty = monthly_carry * delay_noise
        v = base_value * sales_mult / cost_mult
        v = v * (1 - delay_penalty)
        v = v * (1 + liq_premium)
        samples.append(max(0.0, v))
    p10, p50, p90 = _percentiles(samples, [0.10, 0.50, 0.90])
    return (p10, p50, p90, {"samples": len(samples), "baseline_delay_m": baseline_delay})

def monte_carlo_credit(par_value: float,
                       coupon_apr: float,
                       tenor_months: int,
                       pd_annual: float = 0.02,
                       lgd: float = 0.35,
                       rate_spread_vol_bps: float = 50.0,
                       n: int = 3000) -> Tuple[float, float, float, dict]:
    if par_value <= 0 or tenor_months <= 0 or n <= 0:
        return (par_value, par_value, par_value, {"samples": 0})
    horizon_years = tenor_months / 12.0
    pd_path = 1 - (1 - pd_annual) ** horizon_years
    samples = []
    for _ in range(n):
        spread_shock = random.gauss(0.0, rate_spread_vol_bps) / 10000.0
        if random.random() < pd_path:
            recovery = max(0.0, 1.0 - lgd + random.gauss(0.0, 0.03))
            price = par_value * recovery
        else:
            carry = coupon_apr * horizon_years * 0.2
            price = par_value * (1.0 - spread_shock + carry)
        samples.append(max(0.0, price))
    p10, p50, p90 = _percentiles(samples, [0.10, 0.50, 0.90])
    return (p10, p50, p90, {"samples": len(samples), "pd_path": pd_path, "lgd": lgd})

# -------------------------- AI Explainer (stub) --------------------------

def ai_explainer(summary: Dict[str, Any]) -> str:
    # Placeholder: later call OpenAI to turn 'summary' dict into investor-friendly prose.
    return "Valuation computed with deterministic math; risk band via Monte Carlo; progress/macro/liquidity overlays applied."


# -------------------------- Main entrypoint --------------------------

def run(params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        p = ValuationParams(**(params or {}))
    except ValidationError as ve:
        return {"status": "error", "errors": ve.errors()}

    # Common helpers/inputs
    tokens_out = int(p.tokens_outstanding or 1_000_000)
    macro_adj = p.macro or MacroOverlay()
    liq = p.liquidity or Liquidity()
    progress = p.progress or Progress()
    costs = p.costs or Costs()

    # ==================== CREDIT PATH ====================
    if p.mode.lower() == "credit":
        loan = float(p.loan_amount or 0.0)
        apr = float(p.coupon_apr or 0.0)
        tenor = int(p.tenor_months or 0)
        schedule = p.schedule or "bullet"

        # collateral value (override for now; later call equity valuation)
        coll_val = (p.collateral.value_override if p.collateral and p.collateral.value_override is not None else None)
        noi = (p.collateral.noi_annual if p.collateral else None)

        returns = compute_credit_cashflows_and_irr(loan, apr, tenor, schedule)
        metrics = credit_metrics(coll_val, loan, apr, tenor, schedule, noi, costs.build_cost, costs.soft_costs)
        cov = covenant_eval(metrics, p.covenants)

        # price band via credit MC (use par ~ loan as base)
        p10, p50, p90, diag = monte_carlo_credit(
            par_value=loan or 0.0,
            coupon_apr=apr or 0.0,
            tenor_months=tenor or 1,
            pd_annual=0.02,
            lgd=0.35,
            rate_spread_vol_bps=50.0,
            n=3000
        )

        # Macro & liquidity nudges on the mid
        base_mid = apply_macro_delta(p50, macro_adj)
        base_mid *= (1 + liquidity_premium(liq))

        # For credit tokens: NAV per token ≈ price / tokens
        nav = {"nav_equity": base_mid, "nav_per_token": (base_mid / max(tokens_out, 1))}
      
           # Demand-aware token pricing (credit)
        d_idx = _compute_demand_index(p.demand, liq)
        market_price = _price_from_nav(nav["nav_per_token"], d_idx, alpha=0.6)

        # ---- helpers before building the result ----
        risk_band = {
            "low": apply_macro_delta(p10, macro_adj),
            "base": base_mid,
            "high": apply_macro_delta(p90, macro_adj),
        }
        risk_meta = _risk_score_from_band(risk_band["low"], risk_band["base"], risk_band["high"])
        token_econ = _tokenize_from_value(core_value=risk_band["base"], tokens_out=tokens_out)
        summary = _investor_summary("credit", risk_band, irr=returns.get("irr"))

        result = {
            "status": "done",
            "mode": "credit",
            "inputs": {"params": p.model_dump() if hasattr(p, "model_dump") else p.dict()},
            "core_valuation": risk_band,
            "token_economics": token_econ,
            "investor_summary": summary,
            "developer_offer": _developer_offer(
                risk_band["base"], metrics.get("ltc"), risk_meta["risk_score"]
            ) if "_developer_offer" in globals() else None,
            "collateral": {
                "value": coll_val,
                "ltv": metrics["ltv"],
                "ltc": metrics["ltc"],
                "dscr": metrics["dscr"],
                "icr": metrics["icr"],
                "debt_service_annual": metrics["debt_service_annual"],
                "covenant_check": cov,
            },
            "expected_returns": returns,
            "risk_meta": risk_meta,
            "nav": nav,

            # ✅ put token_pricing here as a normal field:
            "token_pricing": {
                "nav_per_token": nav["nav_per_token"],
                "market_price_per_token": market_price,
                "demand_index": d_idx,
                "prediction_overlay": {"status": "none"}  # (credit doesn’t call prediction; add later if you want)
            },

            "links": {
                "risk_engine_ready": True,
                "contracts_engine_ready": True,
                "resale_engine_ready": True
            },
            "diagnostics": {"credit_mc": diag},
            "explain": ai_explainer({"mode": "credit", "metrics": metrics, "returns": returns}),
        }
        return result

       # ==================== EQUITY PATH ====================
    # components
    hedonic = compute_hedonic(p)
    residual = compute_residual_land_value(p)
    comps_val, comps_used = compute_comps_value(p)

    # blend (start: hedonic; if residual exists, average; if comps exists, blend by weights)
    if comps_val is not None:
        w_c = float(p.blend_comps or 0.6)
        w_h = float(p.blend_hedonic or 0.4)
        base_value = w_c * comps_val + w_h * hedonic
    else:
        base_value = hedonic

    if residual is not None:
        base_value = (base_value + residual) / 2.0

    # macro delta
    base_value = apply_macro_delta(base_value, macro_adj)

    # progress + delay penalties
    value_after_progress, prog_diag = apply_progress_and_delay(
        base_value,
        progress,
        finance_apr=float(p.discount_rate_equity or 0.12),
        climate=p.climate_signals,
    )

    # ---- equity Monte Carlo around that value ----
    planned = float(progress.planned_completion_months or 12.0)
    expected = float(
        progress.expected_completion_months
        if (progress and progress.expected_completion_months is not None)
        else planned + progress_delay_months(progress, p.climate_signals)
    )

    p10, p50, p90, diag = monte_carlo_equity(
        base_value=value_after_progress,
        planned_months=planned,
        expected_months=expected,
        finance_apr=float(p.discount_rate_equity or 0.12),
        sales_vol=0.08,
        cost_vol=0.06,
        delay_sd_months=1.0,
        liq_premium=liquidity_premium(liq),
        n=3000,
    )

    # define band vars for downstream use
    low, mid, high = p10, p50, p90

    # ---- Equity DCF result (monthly pro forma → IRR/NPV/EM) ----
    dcf = compute_equity_cashflows_and_irr(
        land_cost=p.land_cost,
        build_cost=p.build_cost,
        soft_costs=p.soft_costs,
        sales_revenue=p.sales_revenue,
        exit_year=p.exit_year,
        discount_rate=float(p.discount_rate_equity or 0.12),
        timeline_months=int(progress.planned_completion_months or 24),
        presale_pct=float(p.sales.presold_pct) if (p.sales and p.sales.presold_pct is not None) else 0.0,
        presale_deposit_pct=0.10,
        spend_curve="s-curve",
    )

    # Token NAV (equity)
    nav = build_token_nav(project_value=mid, debt=float(p.debt_outstanding or 0.0), tokens_out=tokens_out)
    # Demand-aware token pricing (equity)
    d_idx = _compute_demand_index(p.demand, liq)

    # ---- fetch prediction overlay (Market Prediction Engine) ----
    try:
        from app.engines.Core import market_prediction
        pred = market_prediction.run(
            p.model_dump() if hasattr(p, "model_dump") else p.dict()
        )
    except Exception:
        pred = {"status": "none"}

    nav_per_token = nav["nav_per_token"]
    demand_idx = d_idx
    market_price = _price_from_nav(nav_per_token, demand_idx, alpha=0.6)

    token_pricing = {
        "nav_per_token": nav_per_token,
        "market_price_per_token": market_price,
        "demand_index": demand_idx,
        "prediction_overlay": pred,
    }
    # Demand-aware token pricing (equity)
    d_idx = _compute_demand_index(p.demand, liq)
    market_price = _price_from_nav(nav["nav_per_token"], d_idx, alpha=0.6)

    # ---- helpers right before result ----
    core_band = {"low": low, "base": mid, "high": high}
    token_econ = {"tokens_outstanding": tokens_out, **nav}
    risk_meta = _risk_score_from_band(low, mid, high)

    summary = ai_explainer({
        "mode": "equity",
        "drivers": ["hedonic", "residual", ("comps" if p.use_comps else "hedonic-only")],
        "band": core_band,
    })

    debt_ratio = (float(p.debt_outstanding or 0.0) / max(mid, 1.0)) if (mid and mid > 0) else None

    # ---- build final result ----
    result = {
        "status": "done",
        "mode": "equity",
        "inputs": {"params": p.model_dump() if hasattr(p, "model_dump") else p.dict()},
        "components": {
            "hedonic": hedonic,
            "residual_land_value": residual,
            "comps_value": comps_val,
            "comps_used": comps_used,
        },
        "overlays": {
            "progress_discount": prog_diag["progress_discount"],
            "delay_months": prog_diag["delay_months"],
            "delay_penalty": prog_diag["delay_penalty"],
            "macro_delta_bps": (p.macro.discount_rate_delta_bps if p.macro else 0),
            "liquidity_premium": liquidity_premium(liq),
        }, 
        "core_valuation": core_band,
        "token_economics": token_econ,
        "investor_summary": summary,
        "developer_offer": (
            _developer_offer(mid, debt_ratio, risk_meta["risk_score"])
            if "_developer_offer" in globals() else None
        ),
        "expected_returns": {"equity_dcf": dcf},
        "risk_meta": risk_meta,
        "nav": nav,
        "token_pricing": token_pricing,
                       # ---- fetch prediction overlay (Market Prediction Engine) ---

},
    

    return result
# Register with the engine registry
register(
    key="valuation",
    fn=run,
    name="Valuation",
    description="Project & token valuation for equity and credit with risk/macro/liquidity overlays, demand-aware token pricing, and Monte Carlo."
)