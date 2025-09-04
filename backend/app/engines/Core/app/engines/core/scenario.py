# app/engines/Core/scenario.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from app.engines import register, REGISTRY
import math

@dataclass
class Person:
    income: float
    savings: float
    savings_rate_pct: float
    deposit_pct: float
    max_dti: float

@dataclass
class Mortgage:
    term_years: int = 30
    risk_tolerance: str = "medium"

def _annuity_rate(apr: float, years: int) -> float:
    # yearly payment per $1 principal
    r = apr
    n = max(1, years)
    if r <= 0: return 1.0 / n
    return (r * (1 + r)**n) / ((1 + r)**n - 1)

def _safe_until_rate(income: float, dti_max: float, lvr_income_share: float = 0.35) -> float:
    # crude: income * share → max annual repayment, invert annuity to find max rate (solve approx)
    # we’ll search 0%..12%
    repay_cap = income * lvr_income_share
    lo, hi = 0.0, 0.12
    for _ in range(48):
        mid = 0.5*(lo+hi)
        pay_per_dollar = _annuity_rate(mid, 30)
        # want: repay_cap >= pay_per_dollar * loan
        # but without loan we approximate with DTI → loan ~ income * dti_max
        loan_guess = income * dti_max
        if repay_cap >= pay_per_dollar * loan_guess: lo = mid
        else: hi = mid
    return round(lo*100, 2)  # percent

def _macro_path_array(path: Optional[List[float]], months: int, carry_last=True) -> List[float]:
    if not path: return [0.0]*months
    out = []
    steps = len(path)
    for m in range(months):
        i = min(int(m / (months/max(1,steps))), steps-1)
        out.append(path[i])
    if carry_last and out: out[-1] = path[-1]
    return out

def _project_affordability(person: Person, macros: Dict[str, Any], months: int = 36) -> List[float]:
    # Build monthly affordability (max purchase price) under macro paths
    cash_bps = _macro_path_array(macros.get("cash_rate_path_bps"), months)
    wages = _macro_path_array(macros.get("wages_path_pct"), months)
    cpi = _macro_path_array(macros.get("cpi_path_pct"), months)
    wages_mult = 1.0
    savings = person.savings

    series = []
    for m in range(months):
        wages_mult *= (1 + (wages[m]/100.0)/12.0)
        income_now = person.income * wages_mult
        # update savings with savings rate and mild CPI drag on real power
        savings += (income_now * person.savings_rate_pct) / 12.0
        deposit = savings * person.deposit_pct

        # crude mortgage rate: cash + 250 bps margin
        annual_rate = max(0.0, (cash_bps[m]/10000.0) + 0.025)
        pay_rate = _annuity_rate(annual_rate, 30)
        repay_cap = income_now * 0.35   # 35% of income
        loan_cap = repay_cap / max(pay_rate, 1e-6)
        price_cap = loan_cap + deposit

        # real terms tweak: if CPI high, trim 0.5% real affordability per 1% CPI>3
        over_cpi = max(0.0, cpi[m]-3.0)
        real_trim = 1 - 0.005 * over_cpi
        series.append(max(0.0, price_cap * real_trim))
    return series

def _unlock_year(price_series: List[float], target_price: float, start_year: int = 2025) -> Optional[int]:
    for i, p in enumerate(price_series):
        if p >= target_price:
            return start_year + int((i+1)/12)
    return None

def run(params: Dict[str, Any]) -> Dict[str, Any]:
    body = params or {}
    person_in = body.get("person") or {}
    mort_in = body.get("mortgage") or {}
    targets = body.get("targets") or []
    macros  = body.get("macros") or {}
    scenarios = body.get("scenarios") or ["baseline"]

    person = Person(
        income=float(person_in.get("income") or 0.0),
        savings=float(person_in.get("savings") or 0.0),
        savings_rate_pct=float(person_in.get("savings_rate_pct") or 0.0),
        deposit_pct=float(person_in.get("deposit_pct") or 0.2),
        max_dti=float(person_in.get("max_dti") or 6.0),
    )
    mort = Mortgage(
        term_years=int(mort_in.get("term_years") or 30),
        risk_tolerance=str(mort_in.get("risk_tolerance") or "medium"),
    )

    months = 36
    # baseline affordability
    aff_base = _project_affordability(person, macros, months=months)

    # scenario variants
    aff_faster = aff_base[:]
    if "faster_savings" in scenarios:
        aff_faster = _project_affordability(
            Person(person.income, person.savings, person.savings_rate_pct*1.4, person.deposit_pct, person.max_dti),
            macros, months
        )
    aff_windfall = aff_base[:]
    if "windfall" in scenarios:
        # 50k one-off in month 3
        p2 = Person(person.income, person.savings+50000, person.savings_rate_pct, person.deposit_pct, person.max_dti)
        aff_windfall = _project_affordability(p2, macros, months)

    # target suburb pricing (ask comps engine for an anchor)
    anchor_prices = []
    for tgt in targets[:3]:
        suburb = tgt.get("suburb") or "Unknown"
        comps = REGISTRY.get("comps")
        med_price = None
        if comps:
            resp = comps({"address": f"{suburb}", "radius_miles": 1.0, "limit": 8}) or {}
            comp_list = resp.get("comps") or []
            psf = [c["price"]/max(c["sqft"] or 1, 1) for c in comp_list if c.get("price") and c.get("sqft")]
            if psf:
                med_psf = sorted(psf)[len(psf)//2]
                med_price = med_psf * 1500  # assume 1500 sqft target for now
        anchor_prices.append({"suburb": suburb, "median_guess": med_price})

    # unlock years for each scenario vs first target
    first_target = anchor_prices[0] if anchor_prices else {"median_guess": None, "suburb": "N/A"}
    target_price = float(first_target["median_guess"] or 2000000.0)

    unlock = {
        "baseline": _unlock_year(aff_base, target_price),
        "faster_savings": _unlock_year(aff_faster, target_price),
        "windfall": _unlock_year(aff_windfall, target_price),
    }

    safe_rate = _safe_until_rate(person.income, person.max_dti)
    gauge = "green" if safe_rate >= 7.0 else "amber" if safe_rate >= 5.5 else "red"

    return {
        "status": "ok",
        "series": {
            "months": months,
            "affordability_baseline": aff_base,
            "affordability_faster": aff_faster,
            "affordability_windfall": aff_windfall,
            "safe_until_rate": safe_rate
        },
        "targets": [{"suburb": a["suburb"], "unlock_year": unlock.get("baseline"), "current_median": target_price}],
        "stress_gauge": gauge,
        "ai_summary": "stub"  # replaced by ai_explainer later
    }

register(
    key="scenario",
    fn=run,
    name="Scenario Simulator",
    description="Projects affordability under macro & personal scenarios; provides unlock year and stress gauge."
)