"""Succession bench for every floor position in NAICS 3363 (README 3.5; DL-31 in outputs/analysis_log.md; exploratory).

Positions  every detailed occupation in SOC 51, 49, 53, 47 or 17-3 with >= 1,000 jobs in NAICS 336300 (OEWS May 2025)
           that has an O*NET Skills profile.
Distance   D(S -> T) on Skills with T's importance weights and z over the 910-occupation universe (the construction
           of II-B's registered estimator); P = percentile of D among all O*NET occupations except T's own codes.
Successor  S is an eligible successor of T when S earns less than T (OEWS May 2025 median annual wage in 336300) and
           its O*NET Job Zone is no higher than T's: a promotion or a lateral move. D counts only shortfalls, so
           without this rule more skilled occupations would be the "nearest successor" of almost every position.
Close      P <= 25 (point estimate). Stability = share of 200 random half-splits of the Skills elements (400 half-sets,
           seed 20261021) in which the pair stays at P <= 25.
Links      (DL-33) per position: how many other positions it is a close successor for (and how many maintenance
           targets), with the bootstrap range; the share of its own close-source jobs held by production roles (SOC 51).
Checks     (DL-32) measurement error: parametric bootstrap of the Skills ratings as in II-B's registered bootstrap
           (truncated normal with the published SE; B = 200, seed 20261022), z and every profile recomputed, wages and
           Job Zones fixed; rule choice: the same counts under six alternative rules (stricter / looser closeness,
           wage rule or Job Zone rule alone, lateral moves up to 110% of the target wage, Knowledge instead of Skills).

Inputs:  DuckDB onet_ratings, oews_3363, ep_onet_nem_crosswalk; data/raw/onet/job_zones.csv;
         data/raw/ep/National_Employment_Matrix_IND_336300.csv (optional); outputs/history/oews_3363_2021_2025.csv (optional)
Outputs: outputs/floor_map/succession_pairs.csv, position_summary.csv, floor_bootstrap.csv, rule_variants.csv
Usage:   python -m src.floor_map
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pandas as pd

from .onet_arrays import TIE_TOL, load_arrays, sample_truncnorm
from .config import REPO_ROOT, load_config, repo_path
from .deficit import contributions, importance_weights, total_deficit, zscore
from .mix import NEM_FILE, bls_adjustment_pct, nem_baseline, read_nem

FLOOR_PREFIXES = ("51-", "49-", "53-", "47-", "17-3")
MIN_JOBS = 1000
CLOSE_P = 25.0
SEED, N_SPLITS = 20261021, 200
BOOT_SEED, BOOT_B = 20261022, 200
SUPERVISORS = "51-1011"
# name, domain, close threshold on P, wage factor (None = no wage rule), Job Zone rule (DL-32)
RULE_VARIANTS = [
    ("base: earns less, Job Zone <= target, P <= 25 (Skills)", "S", 25.0, 1.0, True),
    ("stricter closeness: P <= 15", "S", 15.0, 1.0, True),
    ("looser closeness: P <= 35", "S", 35.0, 1.0, True),
    ("wage rule only (no Job Zone rule)", "S", 25.0, 1.0, False),
    ("Job Zone rule only (no wage rule)", "S", 25.0, None, True),
    ("lateral moves: earns < 110% of target, Job Zone <= target", "S", 25.0, 1.10, True),
    ("Knowledge instead of Skills (base rule)", "K", 25.0, 1.0, True),
]
# one-to-many codes not covered by the SOC -> O*NET overrides in config/project.yaml (DL-31)
EXTRA_CODES = {"17-3027": ["17-3027.00", "17-3027.01"],     # incl. automotive engineering technicians
               "53-1047": ["53-1042.00", "53-1043.00"]}     # supervisors of hand and machine material movers
MAINTENANCE = {"49-9041", "49-9071", "47-2111", "49-9043", "49-9044"}


def onet_codes(soc: str, cfg: dict[str, Any], cw: pd.DataFrame, rated: set[str]) -> list[str]:
    reg = cfg["onet_crosswalk"]["overrides"]
    if soc in reg:
        return list(reg[soc]["primary"])
    if soc in EXTRA_CODES:
        return EXTRA_CODES[soc]
    return [c for c in cw.loc[cw.nem_code == soc, "onet_code"] if c in rated]


def eligible(src_wage: float, tgt_wage: float, src_jz: int, tgt_jz: int) -> bool:
    """Promotion or lateral move: the source earns less and needs no more preparation (Job Zone)."""
    return bool(np.isfinite(src_wage) and np.isfinite(tgt_wage) and src_wage < tgt_wage and src_jz <= tgt_jz)


def eligibility_matrix(wage: np.ndarray, jz: np.ndarray, wage_factor: float | None = 1.0,
                       job_zone_rule: bool = True) -> np.ndarray:
    """E[t, s] = source s may succeed target t (rows targets, columns sources); the diagonal is False."""
    n = len(wage)
    E = np.ones((n, n), bool)
    if wage_factor is not None:
        E &= np.isfinite(wage)[None, :] & np.isfinite(wage)[:, None] & (wage[None, :] < wage_factor * wage[:, None])
    if job_zone_rule:
        E &= jz[None, :] <= jz[:, None]
    np.fill_diagonal(E, False)
    return E


def bench_counts(close: np.ndarray, jobs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Number of close sources and bench ratio (close-source jobs per target job) for every target."""
    return close.sum(axis=1), (close @ jobs) / jobs


def _percentiles(z_t, w_t, Z_ref, Z_src, cols=None) -> np.ndarray:
    if cols is not None:
        z_t, w_t, Z_ref, Z_src = z_t[cols], w_t[cols], Z_ref[:, cols], Z_src[:, cols]
    Dr = total_deficit(contributions(z_t, w_t, Z_ref), w_t)
    Ds = total_deficit(contributions(z_t, w_t, Z_src), w_t)
    return 100.0 * (Dr[None, :] <= Ds[:, None] + TIE_TOL).mean(axis=1), Ds


def pair_matrices(Z: np.ndarray, W: np.ndarray, members: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """P[t, s] and D[t, s] for every target t and source s; P ranks D among all occupations except t's codes."""
    S = np.stack([Z[m].mean(axis=0) for m in members])
    n = len(members)
    Pm, Dm = np.empty((n, n)), np.empty((n, n))
    for i, tc in enumerate(members):
        ref = np.ones(Z.shape[0], bool); ref[tc] = False
        Pm[i], Dm[i] = _percentiles(Z[tc].mean(axis=0), W[tc].mean(axis=0), Z[ref], S)
    return Pm, Dm


def _variant_row(name: str, close: np.ndarray, P: pd.DataFrame, keep: np.ndarray) -> dict[str, Any]:
    socs = np.array(P.index)[keep]
    jobs = P.jobs_2025.to_numpy(dtype=float)[keep]
    n_close, bench = bench_counts(close[np.ix_(keep, keep)], jobs)
    none = n_close == 0
    jz = P.job_zone.to_numpy()[keep]
    maint = P.maintenance_target.to_numpy()[keep]
    skilled = jz >= 3
    sup = list(socs).index(SUPERVISORS) if SUPERVISORS in socs else None
    return {"variant": name, "n_positions": int(keep.sum()), "n_no_close": int(none.sum()),
            "jobs_no_close": float(jobs[none].sum()), "share_jobs_no_close_pct": 100 * float(jobs[none].sum() / jobs.sum()),
            "no_close_positions": "; ".join(socs[none]),
            "n_single_close_source": int((n_close == 1).sum()),
            "maintenance_bench_min": float(bench[maint].min()), "maintenance_bench_max": float(bench[maint].max()),
            "supervisors_bench": float(bench[sup]) if sup is not None else np.nan,
            "supervisors_rank_thinnest_among_job_zone_3plus":
                int(1 + np.sum(bench[skilled] < bench[sup])) if sup is not None else np.nan,
            "n_job_zone_3plus": int(skilled.sum()),
            "thinnest_job_zone_3plus": socs[skilled][np.argmin(bench[skilled])]}


def run(cfg: dict[str, Any], root: Path = REPO_ROOT, boot_draws: int | None = None) -> dict[str, pd.DataFrame]:
    with duckdb.connect(str(repo_path(cfg["paths"]["duckdb"], root)), read_only=True) as con:
        a = load_arrays(con, "S", cfg)
        ak = load_arrays(con, "K", cfg)
        oews = con.execute("SELECT * FROM oews_3363").df().set_index("OCC_CODE")
        cw = con.execute("SELECT * FROM ep_onet_nem_crosswalk").df()
    rated = set(a.codes)
    jz_raw = pd.read_csv(repo_path(cfg["paths"]["raw_onet"], root) / "job_zones.csv", dtype=str).set_index("O*NET-SOC Code")["Job Zone"]
    jz_of = lambda codes: max(int(str(jz_raw[c]).split("-")[-1]) for c in codes if c in jz_raw.index)

    pos = oews[(oews.O_GROUP == "detailed") & oews.index.str.startswith(FLOOR_PREFIXES) & (oews.TOT_EMP >= MIN_JOBS)]
    rows, skipped = [], []
    for soc, r in pos.iterrows():
        codes = onet_codes(soc, cfg, cw, rated)
        if not codes or not all(c in rated for c in codes):
            skipped.append(soc); continue
        rows.append({"soc6": soc, "title": r.OCC_TITLE, "onet_codes": ";".join(codes), "jobs_2025": r.TOT_EMP,
                     "emp_rse": r.EMP_PRSE, "a_median": r.A_MEDIAN, "job_zone": jz_of(codes),
                     "maintenance_target": soc in MAINTENANCE})
    P = pd.DataFrame(rows).set_index("soc6")
    P.attrs["skipped"] = skipped

    nem_path = repo_path(cfg["paths"]["raw_ep"], root) / NEM_FILE
    if nem_path.exists():
        nem = read_nem(nem_path).set_index("code")
        base = nem_baseline(nem.reset_index())["baseline_change_pct"]
        P["nem_change_pct"] = nem.change_pct.reindex(P.index)
        P["bls_adjustment_pct"] = bls_adjustment_pct(P.nem_change_pct, base)
    else:
        P["nem_change_pct"] = P["bls_adjustment_pct"] = np.nan
    hist_path = repo_path("outputs/history/oews_3363_2021_2025.csv", root)
    hist = pd.read_csv(hist_path) if hist_path.exists() else None

    Z, _, _ = zscore(a.L)
    W = importance_weights(a.I)
    idx = {c: i for i, c in enumerate(a.codes)}
    prof = {s: Z[[idx[c] for c in P.at[s, "onet_codes"].split(";")]].mean(axis=0) for s in P.index}
    socs = list(P.index)
    S = np.stack([prof[s] for s in socs])
    rng = np.random.default_rng(SEED)
    E = Z.shape[1]
    splits = []
    for _ in range(N_SPLITS):
        h = np.zeros(E, bool); h[rng.permutation(E)[: E // 2]] = True
        splits += [h, ~h]

    pairs = []
    for t in socs:
        tc = [idx[c] for c in P.at[t, "onet_codes"].split(";")]
        z_t, w_t = Z[tc].mean(axis=0), W[tc].mean(axis=0)
        ref = np.ones(len(a.codes), bool); ref[tc] = False
        Pt, Dt = _percentiles(z_t, w_t, Z[ref], S)
        stab = np.mean([_percentiles(z_t, w_t, Z[ref], S, cols)[0] <= CLOSE_P for cols in splits], axis=0)
        for j, s in enumerate(socs):
            if s == t:
                continue
            el = eligible(P.at[s, "a_median"], P.at[t, "a_median"], P.at[s, "job_zone"], P.at[t, "job_zone"])
            pairs.append({"target": t, "source": s, "D": Dt[j], "P": Pt[j], "eligible": el,
                          "close": el and Pt[j] <= CLOSE_P, "stability": stab[j] if el else np.nan,
                          "source_jobs": P.at[s, "jobs_2025"], "source_wage": P.at[s, "a_median"],
                          "source_job_zone": P.at[s, "job_zone"], "source_nem_change_pct": P.at[s, "nem_change_pct"],
                          "source_bls_adjustment_pct": P.at[s, "bls_adjustment_pct"],
                          "source_more_paid": P.at[s, "a_median"] >= P.at[t, "a_median"]})
    X = pd.DataFrame(pairs)

    summ = []
    for t in socs:
        g = X[X.target == t].sort_values(["D", "source"])
        e = g[g.eligible]; c = e[e.close]
        top = e.head(3)
        r = {"soc6": t, **P.loc[t].to_dict(), "n_eligible_sources": len(e), "n_close_sources": len(c),
             "close_source_jobs": float(c.source_jobs.sum()), "close_sources": "; ".join(c.source),
             "bench_ratio": float(c.source_jobs.sum()) / P.at[t, "jobs_2025"],
             "nearest_any_source": g.source.iloc[0], "nearest_any_P": g.P.iloc[0],
             "nearest_any_earns_more": bool(g.source_more_paid.iloc[0]),
             "flag_no_close_internal_source": len(c) == 0,
             "flag_close_sources_all_below_baseline": bool(len(c) > 0 and (c.source_bls_adjustment_pct < 0).all())}
        for k in range(3):
            if k < len(top):
                rr = top.iloc[k]
                r.update({f"top{k+1}_source": rr.source, f"top{k+1}_P": rr.P, f"top{k+1}_stability": rr.stability,
                          f"top{k+1}_jobs": rr.source_jobs, f"top{k+1}_nem_change_pct": rr.source_nem_change_pct})
        if hist is not None and len(c):
            h = hist[hist.OCC_CODE.isin(c.source)].groupby("year").TOT_EMP.sum()
            r["close_pool_change_2021_2025_pct"] = 100 * (h.get(2025, np.nan) / h.get(2021, np.nan) - 1)
            # endpoint check: May 2022 and May 2025 estimates share no survey panel
            r["close_pool_change_2022_2025_pct"] = 100 * (h.get(2025, np.nan) / h.get(2022, np.nan) - 1)
        # cross-part links (DL-33): as a source, and the production share of this position's close pool
        as_src = X[(X.source == t) & X.close]
        r["n_positions_as_close_source"] = int(len(as_src))
        r["n_maintenance_targets_as_close_source"] = int(as_src.target.isin(MAINTENANCE).sum())
        r["close_source_jobs_soc51_pct"] = (100 * float(c[c.source.str.startswith("51-")].source_jobs.sum())
                                            / float(c.source_jobs.sum())) if len(c) else np.nan
        summ.append(r)
    S_df = pd.DataFrame(summ)

    # ---- DL-32: measurement error (parametric bootstrap) and rule choice
    members = [np.array([idx[c] for c in P.at[s, "onet_codes"].split(";")]) for s in socs]
    wage, jz = P.a_median.to_numpy(dtype=float), P.job_zone.to_numpy()
    jobs = P.jobs_2025.to_numpy(dtype=float)
    Pm, _ = pair_matrices(Z, W, members)
    E0 = eligibility_matrix(wage, jz)
    reg = X.set_index(["target", "source"])
    chk = np.array([[Pm[i, j] if i != j else np.nan for j in range(len(socs))] for i in range(len(socs))])
    assert np.allclose([chk[socs.index(t), socs.index(s_)] for t, s_ in reg.index], reg.P), "pair_matrices != pairs"
    assert (E0[[socs.index(t) for t, _ in reg.index], [socs.index(s_) for _, s_ in reg.index]] == reg.eligible).all()

    lv, im = cfg["measurement"]["scales"]["level"], cfg["measurement"]["scales"]["importance"]
    B = int(boot_draws or BOOT_B)
    rng = np.random.default_rng(BOOT_SEED)
    Pb = np.empty((B, len(socs), len(socs)))
    for b in range(B):
        Ls = sample_truncnorm(a.L, a.seL, lv["min"], lv["max"], rng)
        Is = sample_truncnorm(a.I, a.seI, im["min"], im["max"], rng)
        Zb, _, _ = zscore(Ls)
        Pb[b], _ = pair_matrices(Zb, importance_weights(Is), members)
    Cb = (Pb <= CLOSE_P) & E0[None]
    nc_b = Cb.sum(axis=2)                                          # B x targets
    bench_b = (Cb @ jobs) / jobs[None, :]
    none_b = (nc_b == 0).sum(axis=1)
    jobs_none_b = ((nc_b == 0) * jobs[None, :]).sum(axis=1)
    q = lambda x, p: np.quantile(x, p, axis=0)
    S_df["boot_share_no_close"] = (nc_b == 0).mean(axis=0)
    as_src_b = Cb.sum(axis=1)                                      # B x sources: positions each source is close to
    S_df["boot_n_positions_as_close_source_q50"] = q(as_src_b, .5)
    S_df["boot_n_positions_as_close_source_lo"] = q(as_src_b, .025)
    S_df["boot_n_positions_as_close_source_hi"] = q(as_src_b, .975)
    S_df["boot_n_close_q50"], S_df["boot_n_close_lo"], S_df["boot_n_close_hi"] = q(nc_b, .5), q(nc_b, .025), q(nc_b, .975)
    S_df["boot_bench_ratio_q50"] = q(bench_b, .5)
    S_df["boot_bench_ratio_lo"], S_df["boot_bench_ratio_hi"] = q(bench_b, .025), q(bench_b, .975)
    ti, si = np.where(E0)
    fb = pd.DataFrame({"target": np.array(socs)[ti], "source": np.array(socs)[si], "P": Pm[ti, si],
                       "close": Pm[ti, si] <= CLOSE_P, "boot_share_close": Cb[:, ti, si].mean(axis=0),
                       "boot_P_q50": q(Pb[:, ti, si], .5), "boot_P_lo": q(Pb[:, ti, si], .025),
                       "boot_P_hi": q(Pb[:, ti, si], .975), "source_jobs": jobs[si], "B": B, "seed": BOOT_SEED})

    keep_all = np.ones(len(socs), bool)
    var_rows = []
    for name, dom, thr, wf, jzr in RULE_VARIANTS:
        if dom == "S":
            Pv, keep = Pm, keep_all
        else:
            kidx = {c: i for i, c in enumerate(ak.codes)}
            keep = np.array([all(c in kidx for c in P.at[s, "onet_codes"].split(";")) for s in socs])
            Zk, _, _ = zscore(ak.L)
            mk = [np.array([kidx[c] for c in P.at[s, "onet_codes"].split(";")]) if k else np.array([0])
                  for s, k in zip(socs, keep)]
            Pv, _ = pair_matrices(Zk, importance_weights(ak.I), mk)
        close = eligibility_matrix(wage, jz, wf, jzr) & (Pv <= thr)
        var_rows.append({**_variant_row(name, close, P, keep), "domain": dom, "close_threshold_P": thr,
                         "wage_factor": wf, "job_zone_rule": jzr})
    var_rows.append({"variant": f"base rule, Skills ratings redrawn (bootstrap B = {B}, seed {BOOT_SEED})",
                     "n_positions": len(socs), "n_no_close": float(np.median(none_b)),
                     "n_no_close_lo": float(q(none_b, .025)), "n_no_close_hi": float(q(none_b, .975)),
                     "jobs_no_close": float(np.median(jobs_none_b)),
                     "share_jobs_no_close_pct": 100 * float(np.median(jobs_none_b)) / jobs.sum(),
                     "maintenance_bench_min": float(np.median(bench_b[:, P.maintenance_target.to_numpy()].min(axis=1))),
                     "supervisors_bench": float(np.median(bench_b[:, socs.index(SUPERVISORS)])),
                     "domain": "S", "close_threshold_P": CLOSE_P, "wage_factor": 1.0, "job_zone_rule": True})
    V = pd.DataFrame(var_rows)

    out = repo_path("outputs/floor_map", root)
    out.mkdir(parents=True, exist_ok=True)
    X.to_csv(out / "succession_pairs.csv", index=False)
    S_df.to_csv(out / "position_summary.csv", index=False)
    fb.to_csv(out / "floor_bootstrap.csv", index=False)
    V.to_csv(out / "rule_variants.csv", index=False)
    if skipped:
        print(f"positions without an O*NET Skills profile (excluded): {', '.join(skipped)}")
    return {"pairs": X, "positions": S_df, "bootstrap": fb, "variants": V}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=None)
    ap.add_argument("--draws", type=int, default=None, help="override the bootstrap B (smoke tests only)")
    args = ap.parse_args(argv)
    res = run(load_config(args.config), boot_draws=args.draws)
    s = res["positions"]
    pd.set_option("display.width", 260); pd.set_option("display.max_colwidth", 60)
    cols = ["soc6", "jobs_2025", "a_median", "job_zone", "nem_change_pct", "n_eligible_sources", "n_close_sources",
            "close_source_jobs", "top1_source", "top1_P", "top1_stability", "flag_no_close_internal_source",
            "flag_close_sources_all_below_baseline", "nearest_any_earns_more"]
    print(s.sort_values("jobs_2025", ascending=False)[cols].round(1).to_string(index=False))
    v = res["variants"]
    print("\nRule variants and bootstrap (DL-32)")
    print(v[["variant", "n_positions", "n_no_close", "n_no_close_lo", "n_no_close_hi", "jobs_no_close",
             "maintenance_bench_min", "supervisors_bench", "supervisors_rank_thinnest_among_job_zone_3plus",
             "thinnest_job_zone_3plus"]].round(2).to_string(index=False))
    fb = res["bootstrap"]
    c = fb[fb.close]
    print(f"\nclose pairs at the point estimate: {len(c)}; close in < 80% of draws: {int((c.boot_share_close < .8).sum())}; "
          f"not close at the point estimate but close in >= 50% of draws: {int(((~fb.close) & (fb.boot_share_close >= .5)).sum())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
