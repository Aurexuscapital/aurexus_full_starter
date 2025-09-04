# app/engines/Core/comps.py
from __future__ import annotations
import csv, math, random, statistics, os
from typing import Any, Dict, List, Optional, Tuple
from app.engines import register

# ----------------------------- Helpers -----------------------------

def _seed_from_address(addr: str) -> int:
    return abs(hash((addr or "").lower())) % (2**32)

def _fake_lat_lon(addr: str) -> tuple[float, float]:
    # Cheap, deterministic "geocode"
    h = _seed_from_address(addr)
    # Roughly AU-ish bbox; harmless for offline dev
    lat = -37.0 + (h % 1000) / 1000.0 * 10.0    # -37 .. -27
    lon = 144.0 + ((h >> 10) % 1000) / 1000.0 * 10.0  # 144 .. 154
    return (round(lat, 6), round(lon, 6))

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def _iqr_bounds(xs: List[float]) -> Tuple[float, float]:
    if len(xs) < 4:
        return (min(xs, default=0.0), max(xs, default=0.0))
    q1, q3 = statistics.quantiles(xs, n=4)[0], statistics.quantiles(xs, n=4)[2]
    iqr = q3 - q1
    return (q1 - 1.5*iqr, q3 + 1.5*iqr)

def _sim_score(subject_sqft: Optional[int], comp_sqft: Optional[int],
               beds_s: Optional[int], beds_c: Optional[int],
               baths_s: Optional[float], baths_c: Optional[float]) -> float:
    # Simple, bounded 0..1 similarity
    s_sf = subject_sqft or 1500
    c_sf = comp_sqft or s_sf
    ds = abs(c_sf - s_sf) / max(s_sf, 1)
    dbed = abs((beds_c or 0) - (beds_s or 0))
    dbath = abs((baths_c or 0.0) - (baths_s or 0.0))
    score = 1.0 - (0.5*ds + 0.25*dbed + 0.25*dbath)
    return max(0.0, min(1.0, score))

def _weighted_median(values: List[float], weights: List[float]) -> Optional[float]:
    if not values:
        return None
    pairs = sorted(zip(values, weights), key=lambda x: x[0])
    total = sum(max(w, 0.0) for _, w in pairs)
    if total <= 0:
        return statistics.median(values)
    cum = 0.0
    for v, w in pairs:
        cum += max(w, 0.0)
        if cum >= total / 2:
            return v
    return pairs[-1][0]

# ----------------------------- Providers -----------------------------

class BaseProvider:
    def fetch(self, *, address: str, lat: float, lon: float, radius_km: float, limit: int) -> List[Dict[str, Any]]:
        raise NotImplementedError

class LocalCsvProvider(BaseProvider):
    """
    Optional: read seed comps from CSV at app/data/comps_seed.csv
    Columns: address,lat,lon,price,sqft,beds,baths,months_ago,year_built
    """
    def __init__(self, csv_path: str):
        self.csv_path = csv_path

    def fetch(self, *, address: str, lat: float, lon: float, radius_km: float, limit: int) -> List[Dict[str, Any]]:
        if not os.path.exists(self.csv_path):
            return []
        out: List[Dict[str, Any]] = []
        with open(self.csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    clat = float(row.get("lat") or 0.0)
                    clon = float(row.get("lon") or 0.0)
                    d_km = _haversine_km(lat, lon, clat, clon)
                    if d_km <= radius_km:
                        out.append({
                            "address": row.get("address") or "Unknown",
                            "price": float(row.get("price") or 0.0),
                            "sqft": int(float(row.get("sqft") or 0)),
                            "lat": clat,
                            "lon": clon,
                            "beds": int(float(row.get("beds") or 0)),
                            "baths": float(row.get("baths") or 0.0),
                            "months_ago": int(float(row.get("months_ago") or 0)),
                            "year_built": int(float(row.get("year_built") or 0)) or None,
                            "source": "local_csv",
                        })
                except Exception:
                    continue
        # nearest & freshest first
        out.sort(key=lambda c: (_haversine_km(lat, lon, c["lat"], c["lon"]), c.get("months_ago", 999)))
        return out[:max(1, limit)]

class SyntheticProvider(BaseProvider):
    """Deterministic, city-aware generator so you can run offline."""
    def fetch(self, *, address: str, lat: float, lon: float, radius_km: float, limit: int) -> List[Dict[str, Any]]:
        rng = random.Random(_seed_from_address(address) + int(radius_km * 100))
        n = max(6, min(int(limit or 10), 25))
        al = (address or "").lower()
        if "sydney" in al:
            psf_mean, psf_sd = 11000, 900
        elif "melbourne" in al:
            psf_mean, psf_sd = 9000, 800
        elif "brisbane" in al:
            psf_mean, psf_sd = 7500, 700
        else:
            psf_mean, psf_sd = 6500, 700

        out: List[Dict[str, Any]] = []
        for i in range(n):
            sqft = int(rng.uniform(900, 2300))
            psf = max(1000, rng.gauss(psf_mean, psf_sd))
            price = float(int(psf * sqft))

            # jitter within radius
            dkm = rng.uniform(0, radius_km)
            bearing = rng.uniform(0, 2*math.pi)
            dlat = (dkm / 110.0) * math.cos(bearing)
            dlon = (dkm / (110.0 * max(1e-6, math.cos(math.radians(abs(lat)))))) * math.sin(bearing)
            clat, clon = lat + dlat, lon + dlon

            out.append({
                "address": f"Comp {i+1}, near {address}",
                "price": price,
                "sqft": sqft,
                "lat": round(clat, 6),
                "lon": round(clon, 6),
                "beds": rng.choice([2,3,3,4]),
                "baths": rng.choice([1.5,2.0,2.0,2.5]),
                "months_ago": rng.randint(0, 9),
                "year_built": rng.choice([1990, 2005, 2012, 2018, 2021]),
                "source": "synthetic_stub",
            })
        # nearer & more recent first
        out.sort(key=lambda c: (_haversine_km(lat, lon, c["lat"], c["lon"]), c.get("months_ago", 999)))
        return out[:max(1, limit)]

# ----------------------------- Core comps logic -----------------------------

def _adjust_psf(psf_raw: float, *, months_ago: int, subject_sqft: int, comp_sqft: int,
                subject_beds: Optional[int], beds: Optional[int],
                subject_baths: Optional[float], baths: Optional[float]) -> float:
    # time drift (bring comp forward to "today")
    monthly_drift = 0.002  # +0.2% per month baseline (tunable / city-specific)
    time_mult = (1.0 + monthly_drift) ** (-max(0, months_ago or 0))

    # size curvature: smaller units exhibit higher $/sf; normalize toward subject
    size_mult = 1.0 + 0.04 * ((subject_sqft - (comp_sqft or subject_sqft)) / max(subject_sqft, 1))

    # bedroom / bathroom nudges
    bed_mult = 1.0 + 0.02 * (((beds or 0) - (subject_beds or 0)))
    bath_mult = 1.0 + 0.015 * (((baths or 0.0) - (subject_baths or 0.0)))

    return max(0.0, psf_raw * time_mult * size_mult * bed_mult * bath_mult)

def _weight_for_comp(*, distance_km: float, months_ago: int, similarity: float) -> float:
    # Distance decay + recency + similarity
    w_dist = 1.0 / (1.0 + max(distance_km, 0.0))           # ~1 at 0 km, decays quickly
    w_time = 1.0 / (1.0 + 0.15 * max(0, months_ago or 0))  # mild penalty per month
    w_sim  = 0.5 + 0.5 * max(0.0, min(1.0, similarity))    # 0.5..1.0
    return w_dist * w_time * w_sim

def run(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Realistic comps engine (offline capable).
    Input:
      - address (str) REQUIRED
      - radius_miles (float) OPTIONAL (default 1.0)
      - limit (int) OPTIONAL (default 8)
      - subject_{sqft,beds,baths} OPTIONAL (improves adjustments)
    Output:
      { status, comps: [...], summary: [...] }
    """
    address: str = params.get("address") or "Unknown Address"
    radius_miles = float(params.get("radius_miles") or 1.0)
    limit = int(params.get("limit") or 8)
    subject_sqft = params.get("subject_sqft") or params.get("living_area_sqft") or 1500
    subject_beds = params.get("subject_beds") or params.get("bedrooms") or 3
    subject_baths = params.get("subject_baths") or params.get("bathrooms") or 2.0

    # "Geocode"
    lat0, lon0 = _fake_lat_lon(address)
    radius_km = max(0.05, radius_miles * 1.60934)

    # Providers: Local CSV (if present) → Synthetic fallback
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "comps_seed.csv")
    providers: List[BaseProvider] = [LocalCsvProvider(csv_path), SyntheticProvider()]

    raw: List[Dict[str, Any]] = []
    for prov in providers:
        try:
            got = prov.fetch(address=address, lat=lat0, lon=lon0, radius_km=radius_km, limit=limit*2)
            raw.extend(got)
        except Exception:
            continue

    # Deduplicate by address (first wins — already sorted by distance/recency)
    seen, comps = set(), []
    for c in raw:
        a = c.get("address") or ""
        if a in seen:
            continue
        seen.add(a)
        comps.append(c)
        if len(comps) >= limit:
            break

    # Compute psf_raw, adjusted psf, distance, similarity, weight
    enriched: List[Dict[str, Any]] = []
    psfs_adj_for_iqr: List[float] = []
    for c in comps:
        price, sqft = float(c.get("price") or 0.0), int(c.get("sqft") or 0)
        if price <= 0 or sqft <= 0:
            continue
        psf_raw = price / sqft
        months_ago = int(c.get("months_ago") or 0)
        dist_km = _haversine_km(lat0, lon0, float(c.get("lat") or lat0), float(c.get("lon") or lon0))
        sim = _sim_score(int(subject_sqft), sqft, int(subject_beds), c.get("beds"), float(subject_baths), c.get("baths"))
        psf_adj = _adjust_psf(psf_raw,
                              months_ago=months_ago,
                              subject_sqft=int(subject_sqft),
                              comp_sqft=sqft,
                              subject_beds=int(subject_beds),
                              beds=c.get("beds"),
                              subject_baths=float(subject_baths),
                              baths=c.get("baths"))
        w = _weight_for_comp(distance_km=dist_km, months_ago=months_ago, similarity=sim)
        row = dict(c)
        row.update({
            "psf_raw": psf_raw,
            "psf_adj": psf_adj,
            "distance_km": dist_km,
            "similarity": sim,
            "weight": w,
        })
        enriched.append(row)
        psfs_adj_for_iqr.append(psf_adj)

    # Outlier trimming on adjusted $/sf
    lo, hi = _iqr_bounds(psfs_adj_for_iqr)
    trimmed = [c for c in enriched if lo <= c["psf_adj"] <= hi] or enriched

    # Estimates
    psf_adj_list = [c["psf_adj"] for c in trimmed]
    weights = [c["weight"] for c in trimmed]
    median_psf = statistics.median(psf_adj_list) if psf_adj_list else None
    weighted_psf = _weighted_median(psf_adj_list, weights) if psf_adj_list else None

    estimate_simple = (median_psf or 0.0) * int(subject_sqft)
    estimate_weighted = (weighted_psf or 0.0) * int(subject_sqft)

    # Quality metrics
    quality = {
        "count_in_radius": len(enriched),
        "count_after_trim": len(trimmed),
        "radius_km": radius_km,
        "used_weighted": bool(weighted_psf is not None),
        "psf_spread_pct": ( (max(psf_adj_list)-min(psf_adj_list))/max(statistics.median(psf_adj_list),1.0)
                            if len(psf_adj_list) >= 2 else None),
    }

    summary = [{
        "address": address,
        "radius_miles": radius_miles,
        "count": len(trimmed),
        "median_psf": median_psf,
        "weighted_psf": weighted_psf,
        "estimate_simple": estimate_simple,
        "estimate_weighted": estimate_weighted,
        "subject_sqft": int(subject_sqft),
        "subject_beds": int(subject_beds),
        "subject_baths": float(subject_baths),
        "quality": quality,
    }]

    return {"status": "ok", "comps": trimmed, "summary": summary}

# Register so valuation can call REGISTRY.get("comps")
register(
    key="comps",
    fn=run,
    name="Comparable Sales",
    description="Comps engine with filtering, adjustments, weighting, outlier control, and quality metrics. CSV-backed with synthetic fallback.",
)