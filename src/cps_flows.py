"""Age profile and labour-market flows of floor occupations in manufacturing, CPS 2020-2026 (DL-44; exploratory).

Context for succession planning: which floor occupations are oldest, where production workers go from one month to
the next, and how fast maintenance work is entered and left. Manufacturing as a whole (Census industry codes whose
NAICS is 31-33); NAICS 3363 alone cannot be identified in the CPS.

  Records  Every civilian adult (PRPERTYP 2, PRTAGE >= 16, PEMLR 1-7) of each monthly file.
  Groups   As in DL-37/DL-40: M = maintenance targets {6355, 7330, 7340, 7350, 7360}; P = codes whose SOC begins 51-;
           C = 8030; mixed 7905 and 8225; R = other P codes.
  A1       Employed person-months in manufacturing, pooled: weighted share aged 55+ (primary) and shares 16-34, 35-54,
           55-64, 65+ per group; references: all employed in manufacturing and in every industry. Secondary: share
           aged 55+ by calendar year for P and M.
  A2       Linked pairs employed in P and manufacturing at t-1: destination at t in ten exclusive categories, all ages
           and by age at t-1.
  A3       Inflow to M in manufacturing (origin P, other employed, unemployed, not in the labour force) and outflow
           from it (destination P, other employed, unemployed, retired, disabled, other not in the labour force), by
           age; ratio of the weighted inflow from P to the weighted outflow to retirement.
  Headline A1: all records; check without allocated occupation or industry codes. A2, A3: pairs without allocated
           occupation, industry (when employed) or labour-force status (PXMLR) in either month (DL-42); all pairs
           reported beside it. Checks: (i) reversal at t+1, (ii) excluding March 2020-December 2021.
  Uncertainty household-cluster bootstrap, B = 1,000, seed 20261029; NCHS proportion standards (DL-40e).

Linking, weights and reporting follow II-B's observed-moves module (DL-37, DL-40); the shared readers are copied
verbatim into src/cps_codes.py (DL-36a: neither repository reads the other's code or outputs).

Inputs:  data/raw/cps/basic/{mon}{yy}pub.zip, data/raw/census_codes/*.xlsx
Cache:   data/interim/cps_adults.npz (rebuilt with --rebuild)
Outputs: outputs/cps_flows/a1_age_profile.csv, a1_age_by_year.csv, a2_production_destinations.csv,
         a3_maintenance_flows.csv, a3_balance.csv, link_quality.csv, cps_flows_summary.md
Usage:   python -m src.cps_flows [--rebuild] [--draws B]
"""
from __future__ import annotations

import argparse
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .config import REPO_ROOT, load_config, repo_path
from .cps_codes import (ALLOCATED, C_CODES, EXCLUDE_WINDOW, FIELDS, KEYS, M_CODES, census_codes, month_files,
                        nchs_rule)

SEED, B_DEFAULT = 20261029, 1000
RECORD_LEN = 1001                                       # 1,000 characters + newline in every 2020-2026 file
EXTRA = {"PRPERTYP": (161, 162), "PXMLR": (685, 686)}
ALL_FIELDS = {**FIELDS, **EXTRA}
BANDS_A1 = [("16-34", 16, 34), ("35-54", 35, 54), ("55-64", 55, 64), ("65+", 65, 200), ("55+", 55, 200)]
BANDS_FLOW = [("all", 16, 200), ("16-34", 16, 34), ("35-54", 35, 54), ("55+", 55, 200)]
A2_DEST = ["mfg_same_occupation", "mfg_other_production", "mfg_maintenance", "mfg_other_occupation",
           "outside_mfg_maintenance", "outside_mfg_other", "unemployed", "retired", "disabled", "other_nilf"]
A3_IN = ["production", "other_employed", "unemployed", "not_in_labour_force"]
A3_OUT = ["production", "other_employed", "unemployed", "retired", "disabled", "other_nilf"]
CHECKS = ["headline_no_allocation", "all_pairs", "i_reversal", "ii_excl_2020_2021"]
ROLE = {"headline_no_allocation": "headline (DL-42 rule)", "all_pairs": "all pairs", "i_reversal": "check",
        "ii_excl_2020_2021": "check"}


# ---------------------------------------------------------------------------------------------------------------
# Reading
def _field(arr: np.ndarray, a: int, b: int, missing: int = -9) -> np.ndarray:
    s = np.ascontiguousarray(arr[:, a - 1:b]).view(f"S{b - a + 1}").ravel()
    s = np.char.strip(s)
    s = np.where(s == b"", str(missing).encode(), s)
    return s.astype(np.int64)


def parse_month_adults(path: Path, mindex: int) -> dict[str, np.ndarray]:
    """Civilian adults (PRPERTYP 2, age 16+, PEMLR 1-7) of one monthly file, read as fixed-width records."""
    with zipfile.ZipFile(path) as zf:
        raw = zf.read(zf.namelist()[0])
    n = len(raw) // RECORD_LEN
    if len(raw) - n * RECORD_LEN > 1:
        raise ValueError(f"{path.name}: record length is not {RECORD_LEN - 1}")
    arr = np.frombuffer(raw[:n * RECORD_LEN], dtype=np.uint8).reshape(n, RECORD_LEN)
    v = {k: _field(arr, *pos) for k, pos in ALL_FIELDS.items() if k != "PWCMPWGT"}
    w = np.char.strip(np.ascontiguousarray(arr[:, 845:855]).view("S10").ravel())
    keep = (v["PRPERTYP"] == 2) & (v["PRTAGE"] >= 16) & np.isin(v["PEMLR"], range(1, 8))
    if not keep.any():
        raise ValueError(f"{path.name}: no civilian adult records")
    if (v["HRYEAR4"][keep] * 12 + v["HRMONTH"][keep] - 1 != mindex).any():
        raise ValueError(f"{path.name}: year/month fields do not match the file name")
    emp = np.isin(v["PEMLR"], [1, 2])
    out = {"hh": v["HRHHID"], "hh2": v["HRHHID2"], "line": v["PULINENO"], "mis": v["HRMIS"], "age": v["PRTAGE"],
           "sex": v["PESEX"], "emlr": v["PEMLR"], "iodp1": v["PUIODP1"],
           "xind": np.where(emp, v["PXIO1ICD"], 0), "xocc": np.where(emp, v["PXIO1OCD"], 0), "xmlr": v["PXMLR"],
           "w": np.where(w == b"", b"0", w).astype(np.float64) / 1e4,
           "ind": np.where(emp, v["PEIO1ICD"], -1), "occ": np.where(emp, v["PTIO1OCD"], -1)}
    small = {"line": np.int16, "mis": np.int8, "age": np.int16, "sex": np.int8, "emlr": np.int8, "iodp1": np.int8,
             "xind": np.int16, "xocc": np.int16, "xmlr": np.int16, "ind": np.int16, "occ": np.int16}
    out = {k: (x[keep].astype(small[k]) if k in small else x[keep]) for k, x in out.items()}
    out["m"] = np.full(int(keep.sum()), mindex, dtype=np.int32)
    return out


def load_adults(root: Path, rebuild: bool = False) -> tuple[pd.DataFrame, list[str]]:
    files = month_files(root)
    cache = repo_path("data/interim", root) / "cps_adults.npz"
    names = [p.name for _, p in files]
    if cache.exists() and not rebuild:
        z = np.load(cache, allow_pickle=False)
        if list(z["files"]) == names:
            return pd.DataFrame({k: z[k] for k in z.files if k != "files"}), names
    parts = [parse_month_adults(p, mi) for mi, p in files]
    df = pd.DataFrame({k: np.concatenate([q[k] for q in parts]) for k in parts[0]})
    del parts
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache, files=np.array(names), **{k: df[k].to_numpy() for k in df.columns})
    return df, names


# ---------------------------------------------------------------------------------------------------------------
# Linking (DL-37, DL-40c), every civilian adult
def link_adults(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["m", "mis", "sex", "age", "emlr", "occ", "ind", "xocc", "xind", "xmlr"]
    prev = df[KEYS + cols].copy()
    prev["m"] = prev["m"] + 1
    pr = df.merge(prev, on=KEYS + ["m"], suffixes=("", "_p"))
    ok = (pr.mis == pr.mis_p + 1) & ~pr.mis.isin([1, 5]) & (pr.sex == pr.sex_p) & (pr.age - pr.age_p).isin([0, 1])
    pr = pr[ok].copy()
    nxt = df[KEYS + ["m", "mis", "sex", "age", "emlr", "occ", "ind"]].copy()
    nxt["m"] = nxt["m"] - 1
    nxt = nxt.rename(columns={c: c + "_n" for c in ["mis", "sex", "age", "emlr", "occ", "ind"]})
    pr = pr.merge(nxt, on=KEYS + ["m"], how="left")
    good = (pr.mis_n == pr.mis + 1) & (pr.sex_n == pr.sex) & (pr.age_n - pr.age).isin([0, 1])
    for c in ("emlr_n", "occ_n", "ind_n"):
        pr[c] = pr[c].where(good)
    return pr.reset_index(drop=True)


def link_quality(df: pd.DataFrame, pr: pd.DataFrame) -> pd.DataFrame:
    months = set(df.m.unique())
    elig = df[~df.mis.isin([1, 5]) & (df.m - 1).isin(months)]
    a = elig.groupby(elig.m // 12).size().rename("eligible_records")
    b = pr.groupby(pr.m // 12).size().rename("linked_pairs")
    q = pd.concat([a, b], axis=1).fillna(0).astype(int)
    q["link_rate_pct"] = 100 * q.linked_pairs / q.eligible_records
    return q.rename_axis("year").reset_index()


# ---------------------------------------------------------------------------------------------------------------
# Estimation helpers
def cluster_totals(hh: np.ndarray, hh2: np.ndarray, cols: dict[str, np.ndarray]) -> tuple[np.ndarray, list[str]]:
    """Household totals (H x C) of weighted columns, households = (HRHHID, HRHHID2)."""
    hid = pd.MultiIndex.from_arrays([hh, hh2]).factorize()[0]
    H = hid.max() + 1
    names = list(cols)
    X = np.empty((H, len(names)))
    for j, k in enumerate(names):
        X[:, j] = np.bincount(hid, weights=cols[k], minlength=H)
    return X, names


def replicate(X: np.ndarray, draws: int, seed: int = SEED) -> np.ndarray:
    H = X.shape[0]
    rng = np.random.default_rng(seed)
    out = np.empty((draws, X.shape[1]))
    for b in range(draws):
        out[b] = np.bincount(rng.integers(0, H, H), minlength=H) @ X
    return out


def summarize(meta: list[dict[str, Any]], X: np.ndarray, names: list[str], reps: np.ndarray) -> pd.DataFrame:
    idx = {c: i for i, c in enumerate(names)}
    tot = X.sum(axis=0)
    rows = []
    for mt in meta:
        k = mt["key"]
        num, den = tot[idx[k + "|num"]], tot[idx[k + "|den"]]
        p = 100 * num / den if den > 0 else np.nan
        with np.errstate(invalid="ignore", divide="ignore"):
            rp = 100 * reps[:, idx[k + "|num"]] / reps[:, idx[k + "|den"]]
        lo, hi = np.nanpercentile(rp, [2.5, 97.5]) if den > 0 else (np.nan, np.nan)
        ok, why = nchs_rule(mt["n_den"], mt["n_num"], p, lo, hi)
        rows.append({**{k2: v for k2, v in mt.items() if k2 != "key"}, "pct": p, "lo": lo, "hi": hi,
                     "reportable": ok, "not_reportable_reason": why})
    return pd.DataFrame(rows)


def band_mask(age: pd.Series, lo: int, hi: int) -> pd.Series:
    return (age >= lo) & (age <= hi)


# ---------------------------------------------------------------------------------------------------------------
# A1
def a1_groups(d: pd.DataFrame, p_codes: set[int], mfg: set[int] | None) -> dict[str, pd.Series]:
    """A1 groups over employed records `d`; with mfg=None the single all-industry reference group."""
    if mfg is None:
        return {"all_employed_all_industries": pd.Series(True, index=d.index)}
    P = d.occ.isin(list(p_codes))
    return {"maintenance_M": d.occ.isin(list(M_CODES)), "machinists_8030": d.occ.isin(list(C_CODES)),
            "mixed_7905": d.occ == 7905, "mixed_8225": d.occ == 8225,
            "rest_R": P & ~d.occ.isin(list(C_CODES) + [7905, 8225]), "production_P": P,
            "all_manufacturing": pd.Series(True, index=d.index)}


def a1_columns(d: pd.DataFrame, groups: dict[str, pd.Series], by_year: tuple[str, ...] = ()) -> tuple[dict, list[dict]]:
    """Weighted columns for A1 over employed records `d` (already restricted to the universe)."""
    alloc = d.xocc.isin(ALLOCATED) | d.xind.isin(ALLOCATED)
    w = d.w.to_numpy()
    year = d.m // 12
    cols, meta = {}, []
    for ck, keep in (("all_records", pd.Series(True, index=d.index)), ("no_allocation", ~alloc)):
        for g, gm in groups.items():
            base = keep & gm
            for b, lo, hi in BANDS_A1:
                k = f"a1|{ck}|{g}|{b}"
                hit = base & band_mask(d.age, lo, hi)
                cols[k + "|num"], cols[k + "|den"] = w * hit, w * base
                meta.append({"key": k, "kind": "pooled", "check": ck, "group": g, "band": b,
                             "n_den": int(base.sum()), "n_num": int(hit.sum())})
            if g in by_year:
                for y in sorted(year[base].unique()):
                    k = f"a1y|{ck}|{g}|{y}"
                    by = base & (year == y)
                    hit = by & band_mask(d.age, 55, 200)
                    cols[k + "|num"], cols[k + "|den"] = w * hit, w * by
                    meta.append({"key": k, "kind": "by_year", "check": ck, "group": g, "band": "55+", "year": int(y),
                                 "n_den": int(by.sum()), "n_num": int(hit.sum())})
    return cols, meta


# ---------------------------------------------------------------------------------------------------------------
# A2 and A3
def pair_masks(pr: pd.DataFrame, p_codes: set[int], mfg: set[int]) -> dict[str, pd.Series]:
    emp_t, emp_p = pr.emlr.isin([1, 2]), pr.emlr_p.isin([1, 2])
    alloc = ((emp_p & (pr.xocc_p.isin(ALLOCATED) | pr.xind_p.isin(ALLOCATED)))
             | (emp_t & (pr.xocc.isin(ALLOCATED) | pr.xind.isin(ALLOCATED)))
             | pr.xmlr_p.isin(ALLOCATED) | pr.xmlr.isin(ALLOCATED))
    return {"emp_t": emp_t, "emp_p": emp_p, "alloc": alloc, "window": pr.m.between(*EXCLUDE_WINDOW),
            "mfg_t": emp_t & pr.ind.isin(list(mfg)), "mfg_p": emp_p & pr.ind_p.isin(list(mfg)),
            "M_t": emp_t & pr.occ.isin(list(M_CODES)), "M_p": emp_p & pr.occ_p.isin(list(M_CODES)),
            "P_t": emp_t & pr.occ.isin(list(p_codes)), "P_p": emp_p & pr.occ_p.isin(list(p_codes)),
            "linked_n": pr.emlr_n.notna(), "emp_n": pr.emlr_n.isin([1, 2]),
            "mfg_n": pr.emlr_n.isin([1, 2]) & pr.ind_n.isin(list(mfg)),
            "M_n": pr.emlr_n.isin([1, 2]) & pr.occ_n.isin(list(M_CODES))}


def a2_destination(pr: pd.DataFrame, k: dict[str, pd.Series], p_codes: set[int]) -> np.ndarray:
    same = pr.occ == pr.occ_p
    return np.select(
        [k["mfg_t"] & same, k["mfg_t"] & k["P_t"], k["mfg_t"] & k["M_t"], k["mfg_t"],
         k["emp_t"] & k["M_t"], k["emp_t"], pr.emlr.isin([3, 4]), pr.emlr == 5, pr.emlr == 6, pr.emlr == 7],
        A2_DEST, "unclassified")


def flow_columns(pr: pd.DataFrame, p_codes: set[int], mfg: set[int]) -> tuple[dict, list[dict]]:
    k = pair_masks(pr, p_codes, mfg)
    w = pr.w.to_numpy()
    dest = a2_destination(pr, k, p_codes)
    # reversal (i): back in the origin state at t+1
    a2_rev = k["linked_n"] & k["mfg_n"] & (pr.occ_n == pr.occ_p)
    out_rev = k["linked_n"] & k["M_n"] & k["mfg_n"]
    in_rev = k["linked_n"] & np.select([k["emp_p"], pr.emlr_p.isin([3, 4]), pr.emlr_p.isin([5, 6, 7])],
                                       [k["emp_n"] & (pr.occ_n == pr.occ_p), pr.emlr_n.isin([3, 4]),
                                        pr.emlr_n.isin([5, 6, 7])], False).astype(bool)
    in_origin = np.select([k["P_p"], k["emp_p"], pr.emlr_p.isin([3, 4]), pr.emlr_p.isin([5, 6, 7])], A3_IN, "none")
    out_dest = np.select([k["P_t"], k["emp_t"], pr.emlr.isin([3, 4]), pr.emlr == 5, pr.emlr == 6, pr.emlr == 7],
                         A3_OUT, "none")
    a2_base = k["P_p"] & k["mfg_p"]
    out_base = k["M_p"] & k["mfg_p"]
    in_stock = k["M_t"] & k["mfg_t"]
    entrant = in_stock & ~k["M_p"]
    leaver = out_base & ~k["M_t"]
    cols, meta = {}, []
    t = pd.Series(True, index=pr.index)
    f = pd.Series(False, index=pr.index)
    for ck in CHECKS:
        keep = {"headline_no_allocation": ~k["alloc"], "all_pairs": t, "i_reversal": ~k["alloc"],
                "ii_excl_2020_2021": ~k["alloc"] & ~k["window"]}[ck]
        rev = ck == "i_reversal"
        # (i) a reversed A2 move or A3 exit counts as no move; a reversed A3 entry leaves the inflow universe (as Q2)
        d = np.where(rev & a2_rev.to_numpy() & (dest != "mfg_same_occupation"), "mfg_same_occupation", dest)
        lv = leaver & ~(out_rev if rev else f)
        en = entrant & ~(in_rev if rev else f)
        stock = in_stock & ~((entrant & in_rev) if rev else f)
        for bname, lo, hi in BANDS_FLOW:
            bp, bt = band_mask(pr.age_p, lo, hi), band_mask(pr.age, lo, hi)
            g = keep & a2_base & bp
            for dn in A2_DEST:
                key = f"a2|{ck}|{bname}|{dn}"
                hit = g & (d == dn)
                cols[key + "|num"], cols[key + "|den"] = w * hit, w * g
                meta.append({"key": key, "q": "a2", "check": ck, "age_band": bname, "category": dn,
                             "n_den": int(g.sum()), "n_num": int(hit.sum())})
            g = keep & out_base & bp
            for dn in A3_OUT:
                key = f"a3out|{ck}|{bname}|{dn}"
                hit = g & lv & (out_dest == dn)
                cols[key + "|num"], cols[key + "|den"] = w * hit, w * g
                meta.append({"key": key, "q": "a3", "check": ck, "direction": "outflow", "age_band": bname,
                             "category": dn, "n_den": int(g.sum()), "n_num": int(hit.sum())})
            g = keep & stock & bt
            for on in A3_IN:
                key = f"a3in|{ck}|{bname}|{on}"
                hit = g & en & (in_origin == on)
                cols[key + "|num"], cols[key + "|den"] = w * hit, w * g
                meta.append({"key": key, "q": "a3", "check": ck, "direction": "inflow", "age_band": bname,
                             "category": on, "n_den": int(g.sum()), "n_num": int(hit.sum())})
        # balance: weighted inflow from P and outflow to retirement / all, over the same pairs (all ages)
        for lab, m in (("inflow_from_production", keep & en & (in_origin == "production")),
                       ("outflow_to_retirement", keep & lv & (out_dest == "retired")),
                       ("inflow_all", keep & en), ("outflow_all", keep & lv)):
            cols[f"bal|{ck}|{lab}"] = w * m
            meta.append({"key": f"bal|{ck}|{lab}", "q": "bal", "check": ck, "category": lab, "n": int(m.sum())})
    return cols, meta


# ---------------------------------------------------------------------------------------------------------------
def run(cfg: dict[str, Any], root: Path = REPO_ROOT, draws: int = B_DEFAULT, rebuild: bool = False) -> dict[str, Any] | None:
    files = month_files(root)
    if not files:
        print("[skip] CPS basic monthly files not present (optional input, DL-44)")
        return None
    p_codes, mfg, _ = census_codes(root)
    df, names = load_adults(root, rebuild)
    out = repo_path("outputs/cps_flows", root); out.mkdir(parents=True, exist_ok=True)

    # A1 — manufacturing groups (clusters: households with an employed manufacturing record) and the reference
    emp_df = df[df.emlr.isin([1, 2])]
    mfg_df = emp_df[emp_df.ind.isin(list(mfg))]
    cols, meta = a1_columns(mfg_df, a1_groups(mfg_df, p_codes, mfg), by_year=("production_P", "maintenance_M"))
    X, nm = cluster_totals(mfg_df.hh.to_numpy(), mfg_df.hh2.to_numpy(), cols)
    a1 = summarize(meta, X, nm, replicate(X, draws))
    del cols, X
    rcols, rmeta = a1_columns(emp_df, a1_groups(emp_df, p_codes, None))
    Xr, nr = cluster_totals(emp_df.hh.to_numpy(), emp_df.hh2.to_numpy(), rcols)
    a1 = pd.concat([a1, summarize(rmeta, Xr, nr, replicate(Xr, draws))], ignore_index=True)
    del rcols, Xr, emp_df
    a1["role"] = a1.check.map({"all_records": "headline", "no_allocation": "check"})
    a1_main = a1[a1.kind == "pooled"].drop(columns=["kind", "year"], errors="ignore").reset_index(drop=True)
    a1_year = a1[a1.kind == "by_year"].drop(columns="kind").reset_index(drop=True)

    # A2, A3 — linked pairs that can enter any universe
    pr_all = link_adults(df)
    lq = link_quality(df, pr_all)
    k = pair_masks(pr_all, p_codes, mfg)
    rel = (k["P_p"] & k["mfg_p"]) | (k["M_p"] & k["mfg_p"]) | (k["M_t"] & k["mfg_t"])
    pr = pr_all[rel].reset_index(drop=True)
    fcols, fmeta = flow_columns(pr, p_codes, mfg)
    Xf, nf = cluster_totals(pr.hh.to_numpy(), pr.hh2.to_numpy(), fcols)
    repf = replicate(Xf, draws)
    rate_meta = [m for m in fmeta if m["q"] in ("a2", "a3")]
    flows = summarize(rate_meta, Xf, nf, repf)
    flows.insert(2, "role", flows.check.map(ROLE))
    a2 = flows[flows.q == "a2"].drop(columns=["q", "direction"], errors="ignore").reset_index(drop=True)
    a3 = flows[flows.q == "a3"].drop(columns="q").reset_index(drop=True)
    idx = {c: i for i, c in enumerate(nf)}
    tot = Xf.sum(axis=0)
    bal = []
    nmeta = {m["key"]: m["n"] for m in fmeta if m["q"] == "bal"}
    for ck in CHECKS:
        for num, den, lab in (("inflow_from_production", "outflow_to_retirement", "inflow from production / outflow to retirement"),
                              ("inflow_all", "outflow_all", "all inflow / all outflow")):
            a, b = f"bal|{ck}|{num}", f"bal|{ck}|{den}"
            with np.errstate(invalid="ignore", divide="ignore"):
                rr = repf[:, idx[a]] / repf[:, idx[b]]
            fin = rr[np.isfinite(rr)]
            lo, hi = np.percentile(fin, [2.5, 97.5]) if fin.size else (np.nan, np.nan)
            bal.append({"check": ck, "role": ROLE[ck], "ratio": lab, "value": tot[idx[a]] / tot[idx[b]] if tot[idx[b]] > 0 else np.nan,
                        "lo": lo, "hi": hi, "weighted_numerator": tot[idx[a]], "weighted_denominator": tot[idx[b]],
                        "events_numerator": nmeta[a], "events_denominator": nmeta[b],
                        "share_draws_gt_1": float(np.mean(fin > 1)) if fin.size else np.nan,
                        "reportable": bool(nmeta[a] >= 1 and nmeta[b] >= 1)})
    bal = pd.DataFrame(bal)

    a1_main.to_csv(out / "a1_age_profile.csv", index=False)
    a1_year.to_csv(out / "a1_age_by_year.csv", index=False)
    a2.to_csv(out / "a2_production_destinations.csv", index=False)
    a3.to_csv(out / "a3_maintenance_flows.csv", index=False)
    bal.to_csv(out / "a3_balance.csv", index=False)
    lq.to_csv(out / "link_quality.csv", index=False)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    fmt = lambda d: d.round(4).to_markdown(index=False)
    md = [f"# Age profile and flows of floor occupations in manufacturing, matched CPS months (DL-44) — exploratory\n\nGenerated: {ts}\n",
          f"Files: {len(names)} monthly files, {names[0]} to {names[-1]}. Civilian adult records: {len(df):,}. "
          f"Linked pairs: {len(pr_all):,} ({len(pr):,} in an A2/A3 universe). Bootstrap: household clusters, B = {draws}, "
          f"seed {SEED}. Rates are percent per month. Manufacturing as a whole, not NAICS 3363; people who move house are "
          "not linked; monthly status transitions include classification error.\n",
          "## Link quality (all civilian adults)\n", fmt(lq),
          "\n## A1 — age profile, employed in manufacturing (pooled person-months)\n", fmt(a1_main),
          "\n## A1 — share aged 55+ by year\n", fmt(a1_year),
          "\n## A2 — destination at t of production workers in manufacturing at t-1\n", fmt(a2),
          "\n## A3 — inflow to and outflow from maintenance in manufacturing\n", fmt(a3),
          "\n## A3 — balance\n", fmt(bal)]
    (out / "cps_flows_summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return {"a1": a1_main, "a1_year": a1_year, "a2": a2, "a3": a3, "balance": bal, "link_quality": lq,
            "n_records": len(df), "n_pairs": len(pr_all), "files": names}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=None)
    ap.add_argument("--rebuild", action="store_true", help="re-read every monthly file instead of the cache")
    ap.add_argument("--draws", type=int, default=B_DEFAULT)
    args = ap.parse_args(argv)
    res = run(load_config(args.config), draws=args.draws, rebuild=args.rebuild)
    if res is None:
        return 0
    pd.set_option("display.width", 250)
    print(f"civilian adult records {res['n_records']:,}; linked pairs {res['n_pairs']:,}; files {len(res['files'])}")
    print(res["link_quality"].to_string(index=False))
    for key in ("a1", "a1_year", "a2", "a3", "balance"):
        print(res[key].round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
