"""BLS projections for NAICS 3363 and their stated reasons — the projection side of II-A's job-mix question.

  Factors  What BLS says drives demand for each maintenance and production occupation (EP Table 1.12): the
           NAICS 336300 row if present, else the all-industry row, else 'no entry' (DL-14).
  Industry BLS National Employment Matrix, NAICS 336300: projected change inside the industry (DL-23), read in two
           stages (DL-28): the industry-scale baseline (modal change of line items = occupations BLS did not adjust)
           and each occupation's BLS adjustment relative to it.
  Automation  Table 1.12 rows that mention robots or automation, counted per occupation and per row (DL-28);
           among the NEM 336300 line items BLS adjusts, those whose 336300 or all-industry factor mentions them (DL-39).
  Output   BLS EP industry workbook (industry.xlsx): employment and real output for auto parts, motor vehicles,
           bodies and trailers, manufacturing and all industries; rank of auto parts in Tables 2.6 / 2.8 / 2.10 (DL-29).
  Skill    BLS adjustment by O*NET Job Zone for every NEM 336300 line item (DL-34): Job Zone = highest zone among the
           O*NET codes BLS maps to the NEM code; per-zone counts, means and shares; Spearman correlation.

The functions are copied verbatim from the original single repository's practice layer (DL-36a); the outputs are
identical to it (checked when the project was split, AL-1).

Outputs: outputs/mix/*.csv and mix_summary.md
Usage:   python -m src.mix
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from .config import REPO_ROOT, load_config, repo_path


def bls_factors(cfg: dict[str, Any], root: Path) -> pd.DataFrame:
    path = repo_path(cfg["paths"]["raw_ep"], root) / cfg["data_versions"]["ep"]["occupation_file"]["file"]
    t = pd.read_excel(path, sheet_name="Table 1.12", header=1, dtype=str, keep_default_na=False)
    t.columns = ["occ_title", "occ_code", "ind_title", "ind_code", "factor"]
    t = t.apply(lambda c: c.str.strip())
    with duckdb.connect(str(repo_path(cfg["paths"]["duckdb"], root)), read_only=True) as con:
        s = con.execute("SELECT * FROM ep_separations WHERE occupation_type = 'Line item'").df().set_index("nem_code")
    codes = cfg["frame"]["targets_core"] + cfg["frame"]["targets_sensitivity"] + cfg["frame"]["feeders_core"] + ["51-9162"]
    rows = []
    for c in codes:
        g = t[t.occ_code == c]
        pick = g[g.ind_code == "336300"]
        level = "NAICS 336300"
        if pick.empty:
            pick, level = g[g.ind_code == "TE1000"], "All industries"
        rows.append({"soc6": c, "title": s.loc[c, "nem_title"] if c in s.index else "",
                     "ep_change_pct": s.loc[c, "emp_change_pct"] if c in s.index else np.nan,
                     "ep_openings_k": s.loc[c, "openings_k"] if c in s.index else np.nan,
                     "factor_level": level if not pick.empty else "no entry",
                     "factor_text": pick.factor.iloc[0] if not pick.empty else "",
                     "n_industry_rows": len(g),
                     "other_industries": "; ".join(f"{i} {tt}" for i, tt in zip(g.ind_code, g.ind_title))
                                         if pick.empty else ""})
    return pd.DataFrame(rows)


NEM_FILE = "National_Employment_Matrix_IND_336300.csv"


def read_nem(path: Path) -> pd.DataFrame:
    """Parse the BLS NEM CSV export (codes are written as ="xx-xxxx"; employment in thousands)."""
    t = pd.read_csv(path, dtype=str, keep_default_na=False)
    t["code"] = t["Occupation Code"].str.replace(r'[="]', "", regex=True).str.strip()
    num = {"2025 Employment": "emp_2025_k", "Projected 2035 Employment": "emp_2035_k",
           "2025 Percent of Industry": "pct_ind_2025", "Projected 2035 Percent of Industry": "pct_ind_2035",
           "Employment Change, 2025-2035": "change_k", "Employment Percent Change, 2025-2035": "change_pct"}
    for src, dst in num.items():
        t[dst] = pd.to_numeric(t[src], errors="raise")
    return t.rename(columns={"Occupation Title": "title", "Occupation Type": "type"})[["code", "title", "type", *num.values()]]


def nem_baseline(t: pd.DataFrame) -> dict[str, float]:
    """Industry-scale baseline (DL-28): the modal percent change among line items.

    BLS rescales the shares of occupations it does not adjust when it changes others, so they all share one
    percent change; it is the mode as long as it covers the largest group of line items."""
    li = t[t["type"].str.contains("Line item", case=False)]
    vc = li.change_pct.value_counts()
    base = float(vc.index[0])
    at = li.change_pct == base
    return {"baseline_change_pct": base, "n_line_items": int(len(li)), "n_at_baseline": int(at.sum()),
            "emp_2025_k_at_baseline": float(li.emp_2025_k[at].sum()), "emp_2025_k_line_items": float(li.emp_2025_k.sum()),
            "second_mode_count": int(vc.iloc[1]) if len(vc) > 1 else 0}


def bls_adjustment_pct(change_pct, baseline_pct: float):
    """Occupation change relative to the industry-scale baseline, in percent: (1 + c) / (1 + b) - 1."""
    return 100.0 * ((1 + np.asarray(change_pct, float) / 100) / (1 + baseline_pct / 100) - 1)


def industry_projection(cfg: dict[str, Any], root: Path) -> pd.DataFrame | None:
    path = repo_path(cfg["paths"]["raw_ep"], root) / NEM_FILE
    if not path.exists():
        print(f"[skip] {NEM_FILE} not found in data/raw/ep (optional input, DL-23)")
        return None
    t = read_nem(path).set_index("code")
    base = nem_baseline(t)
    total = t.loc["00-0000"]
    roles = ([(c, "target_core") for c in cfg["frame"]["targets_core"]]
             + [(c, "feeder_core") for c in cfg["frame"]["feeders_core"]]
             + [(c, "context") for c in ("51-9162", "51-1011", "51-4111", "53-7062")])
    rows = [{"soc6": "00-0000", "role": "industry total", **total.drop(["title", "type"]).to_dict(), "title": total.title}]
    for c, role in roles:
        if c not in t.index:
            rows.append({"soc6": c, "role": role, "title": "(not in NEM 336300)"})
            continue
        r = t.loc[c]
        rows.append({"soc6": c, "role": role, "title": r.title, **r.drop(["title", "type"]).to_dict()})
    df = pd.DataFrame(rows)
    df["change_vs_industry_pts"] = df.change_pct - float(total.change_pct)
    df["baseline_change_pct"] = base["baseline_change_pct"]
    li = df.soc6 != "00-0000"
    df["bls_adjusted"] = np.where(li, df.change_pct != base["baseline_change_pct"], np.nan)
    df["bls_adjustment_pct"] = np.where(li, bls_adjustment_pct(df.change_pct, base["baseline_change_pct"]), np.nan)
    df.attrs["baseline"] = base
    return df


ADJ_TOL = 0.05     # adjustments within +/- 0.05 points count as "not adjusted" (floating-point rounding of BLS shares)


def adjustment_by_job_zone(cfg: dict[str, Any], root: Path) -> tuple[pd.DataFrame, pd.DataFrame] | None:
    """BLS adjustment vs O*NET Job Zone for every NEM 336300 line item (DL-34). Descriptive: adjustments are BLS's judgments."""
    path = repo_path(cfg["paths"]["raw_ep"], root) / NEM_FILE
    jz_path = repo_path(cfg["paths"]["raw_onet"], root) / "job_zones.csv"
    if not (path.exists() and jz_path.exists()):
        print("[skip] NEM 336300 or job_zones.csv not found (optional inputs, DL-34)")
        return None
    t = read_nem(path)
    base = nem_baseline(t)["baseline_change_pct"]
    li = t[t["type"].str.contains("Line item", case=False)].copy()
    li["bls_adjustment_pct"] = bls_adjustment_pct(li.change_pct, base)
    with duckdb.connect(str(repo_path(cfg["paths"]["duckdb"], root)), read_only=True) as con:
        cw = con.execute("SELECT nem_code, onet_code FROM ep_onet_nem_crosswalk").df()
    jz = pd.read_csv(jz_path, dtype=str, keep_default_na=False)
    jz["job_zone"] = jz["Job Zone"].str.split("-").str[-1].astype(int)        # O*NET 31.0 merged zone "1-2" -> 2
    m = cw.merge(jz[["O*NET-SOC Code", "job_zone"]], left_on="onet_code", right_on="O*NET-SOC Code")
    by = m.groupby("nem_code").agg(job_zone=("job_zone", "max"), n_onet_codes=("onet_code", "nunique"))
    li = li.join(by, on="code")
    li["direction"] = np.select([li.bls_adjustment_pct > ADJ_TOL, li.bls_adjustment_pct < -ADJ_TOL], ["up", "down"], "none")
    occ = li[["code", "title", "emp_2025_k", "change_pct", "bls_adjustment_pct", "direction", "job_zone", "n_onet_codes"]]
    d = occ.dropna(subset=["job_zone"])
    rows = []
    for z, g in d.groupby("job_zone"):
        rows.append({"job_zone": int(z), "n": len(g), "emp_2025_k": g.emp_2025_k.sum(),
                     "mean_adjustment_pct": g.bls_adjustment_pct.mean(),
                     "emp_weighted_mean_adjustment_pct": np.average(g.bls_adjustment_pct, weights=g.emp_2025_k),
                     "share_up_pct": 100 * (g.direction == "up").mean(), "share_down_pct": 100 * (g.direction == "down").mean()})
    rho, pval = spearmanr(d.job_zone, d.bls_adjustment_pct)
    summ = pd.DataFrame(rows)
    summ.attrs.update({"spearman_rho": float(rho), "spearman_p": float(pval), "n_with_job_zone": len(d),
                       "n_line_items": len(occ), "baseline_change_pct": base})
    return occ, summ


INDUSTRY_FILE = "industry.xlsx"
INDUSTRY_ROWS = {"TE1000": "all industries", "31-330": "manufacturing", "336100": "motor vehicles",
                 "336200": "motor vehicle bodies and trailers", "336300": "motor vehicle parts"}
RANK_TABLES = {"Table 2.6": "largest employment declines", "Table 2.8": "most rapidly declining output",
               "Table 2.10": "largest output declines"}


def industry_output(cfg: dict[str, Any], root: Path) -> pd.DataFrame | None:
    """Table 2.11 employment and real output (chained 2017 dollars) for the auto industries (DL-29)."""
    path = repo_path(cfg["paths"]["raw_ep"], root) / INDUSTRY_FILE
    if not path.exists():
        print(f"[skip] {INDUSTRY_FILE} not found in data/raw/ep (optional input, DL-29)")
        return None
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        book = pd.read_excel(path, sheet_name=None, header=1, dtype=str, keep_default_na=False)
    title = pd.read_excel(path, sheet_name="Table 2.11", header=None, nrows=1).iloc[0, 0]
    if "2025 and projected 2035" not in str(title):
        raise ValueError(f"{INDUSTRY_FILE}: Table 2.11 is not the 2025–35 release ({title})")
    t = book["Table 2.11"].iloc[:, :11]
    t.columns = ["title", "code", "type", "emp_2025_k", "emp_2035_k", "emp_change_k", "emp_change_pct",
                 "emp_cagr_pct", "output_2025_bn", "output_2035_bn", "output_cagr_pct"]
    t = t.apply(lambda c: c.str.strip())
    # all line items that report output: how many see output per job fall, and where 336300 ranks (1 = largest fall)
    li = t[t.type == "Line item"].copy()
    for c in ("emp_2025_k", "emp_2035_k", "output_2025_bn", "output_2035_bn"):
        li[c] = pd.to_numeric(li[c], errors="coerce")
    li = li.dropna(subset=["emp_2025_k", "emp_2035_k", "output_2025_bn", "output_2035_bn"])
    opj = (li.output_2035_bn / li.emp_2035_k) / (li.output_2025_bn / li.emp_2025_k) - 1
    opj_rank = int((opj < float(opj[li.code == "336300"].iloc[0])).sum()) + 1
    t = t[t.code.isin(INDUSTRY_ROWS)].copy()
    for c in t.columns[3:]:
        t[c] = pd.to_numeric(t[c], errors="raise")
    t["label"] = t.code.map(INDUSTRY_ROWS)
    t["output_change_pct"] = 100 * (t.output_2035_bn / t.output_2025_bn - 1)
    t["output_per_job_change_pct"] = 100 * ((t.output_2035_bn / t.emp_2035_k) / (t.output_2025_bn / t.emp_2025_k) - 1)
    t["n_industries_with_output"] = np.where(t.code == "336300", len(li), np.nan)
    t["n_output_per_job_falling"] = np.where(t.code == "336300", int((opj < 0).sum()), np.nan)
    t["rank_output_per_job_change"] = np.where(t.code == "336300", opj_rank, np.nan)
    for sheet, what in RANK_TABLES.items():
        r = book[sheet].iloc[:, 0].str.strip()
        r = r[r != ""].reset_index(drop=True)
        hits = r.index[r == "Motor vehicle parts manufacturing"].tolist()       # row 0 is the total
        t[f"rank_{sheet.split()[1]}"] = np.where(t.code == "336300", hits[0] if hits else np.nan, np.nan)
    return t.reset_index(drop=True)


AUTOMATION_PATTERN = r"robot|automat"


def _table_1_12(cfg: dict[str, Any], root: Path) -> pd.DataFrame:
    """BLS EP Table 1.12 (factors affecting occupational utilization), one row per occupation x industry."""
    path = repo_path(cfg["paths"]["raw_ep"], root) / cfg["data_versions"]["ep"]["occupation_file"]["file"]
    t = pd.read_excel(path, sheet_name="Table 1.12", header=1, dtype=str, keep_default_na=False)
    t.columns = ["occ_title", "occ_code", "ind_title", "ind_code", "factor"]
    t = t.apply(lambda c: c.str.strip())
    return t[t.occ_code.str.match(r"^\d{2}-\d{4}$")].copy()


def adjusted_citing_automation(cfg: dict[str, Any], root: Path, jz_occ: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Flag NEM 336300 line items whose Table 1.12 factor for 336300 or all industries mentions robots or automation,
    and count them among the line items BLS adjusts (DL-39)."""
    t = _table_1_12(cfg, root)
    rel = t[t.ind_code.isin(["336300", "TE1000"])]
    auto = set(rel[rel.factor.str.contains(AUTOMATION_PATTERN, case=False, regex=True)].occ_code)
    occ = jz_occ.assign(cites_automation=jz_occ.code.isin(auto))
    adj = occ[occ.direction != "none"]
    cite = adj[adj.cites_automation]
    summ = {"n_line_items": len(occ), "n_adjusted": len(adj), "n_adjusted_citing_automation": len(cite),
            "n_up_citing": int((cite.direction == "up").sum()), "n_down_citing": int((cite.direction == "down").sum()),
            "jobs_adjusted_k": float(adj.emp_2025_k.sum()), "jobs_citing_automation_k": float(cite.emp_2025_k.sum())}
    return occ, summ


def automation_factors(cfg: dict[str, Any], root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Table 1.12 rows whose factor text mentions robots or automation (DL-28).

    Direction comes from BLS's own wording ('share increases' / 'share decreases'). Counted per occupation
    (up, down or mixed across its matching rows) because the same sentence is repeated for many industries."""
    t = _table_1_12(cfg, root)
    t["direction"] = t.factor.str.lower().str.extract(r"share (increases|decreases)")[0].map(
        {"increases": "up", "decreases": "down"})
    if t.direction.isna().any():
        raise ValueError("Table 1.12: a factor without 'share increases/decreases' wording")
    hit = t[t.factor.str.contains(AUTOMATION_PATTERN, case=False, regex=True)].copy()
    hit["major_group"] = hit.occ_code.str[:2]
    occ = (hit.groupby(["major_group", "occ_code", "occ_title"])
           .agg(n_rows=("direction", "size"), n_up=("direction", lambda x: int((x == "up").sum())),
                n_down=("direction", lambda x: int((x == "down").sum())),
                n_distinct_texts=("factor", "nunique"), in_336300=("ind_code", lambda x: bool((x == "336300").any())))
           .reset_index())
    occ["direction"] = np.select([occ.n_down == 0, occ.n_up == 0], ["up", "down"], "mixed")
    by_group = (occ.groupby("major_group")
                .agg(occupations=("occ_code", "size"), occ_up=("direction", lambda x: int((x == "up").sum())),
                     occ_down=("direction", lambda x: int((x == "down").sum())),
                     occ_mixed=("direction", lambda x: int((x == "mixed").sum())),
                     rows=("n_rows", "sum"), rows_up=("n_up", "sum"), rows_down=("n_down", "sum"))
                .reset_index())
    return occ, by_group


def run(cfg: dict[str, Any], root: Path = REPO_ROOT) -> dict[str, Any]:
    out = repo_path("outputs/mix", root)
    out.mkdir(parents=True, exist_ok=True)
    fac = bls_factors(cfg, root)
    fac.to_csv(out / "bls_factors.csv", index=False)
    nem = industry_projection(cfg, root)
    if nem is not None:
        nem.to_csv(out / "nem_336300.csv", index=False)
    auto_occ, auto_grp = automation_factors(cfg, root)
    outp = industry_output(cfg, root)
    if outp is not None:
        outp.to_csv(out / "industry_output.csv", index=False)
    jzres = adjustment_by_job_zone(cfg, root)
    auto_adj = None
    if jzres is not None:
        jz_occ, jz_sum = jzres
        jz_occ, auto_adj = adjusted_citing_automation(cfg, root, jz_occ)
        jzres = (jz_occ, jz_sum)
        jz_occ.to_csv(out / "bls_adjustment_by_occupation_job_zone.csv", index=False)
        jz_sum.assign(spearman_rho=jz_sum.attrs["spearman_rho"], spearman_p=jz_sum.attrs["spearman_p"],
                      n_with_job_zone=jz_sum.attrs["n_with_job_zone"], n_line_items=jz_sum.attrs["n_line_items"]
                      ).to_csv(out / "bls_adjustment_by_job_zone.csv", index=False)
    auto_occ.to_csv(out / "automation_factor_occupations.csv", index=False)
    auto_grp.to_csv(out / "automation_factor_groups.csv", index=False)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    md = [f"# BLS projections for NAICS 3363 and their stated reasons (DL-14, DL-23, DL-28, DL-29, DL-34, DL-39)\n\n"
          f"Generated: {ts}\n",
          "\n## BLS EP Table 1.12 factors\n", fac[["soc6", "title", "ep_change_pct", "factor_level", "factor_text"]].to_markdown(index=False)]
    if nem is not None:
        b = nem.attrs["baseline"]
        md += ["\n\n## Projections inside NAICS 336300 (BLS National Employment Matrix, DL-23, DL-28)\n",
               f"Industry-scale baseline (modal change of line items, DL-28): {b['baseline_change_pct']:+.1f}% — "
               f"{b['n_at_baseline']} of {b['n_line_items']} line items, {b['emp_2025_k_at_baseline']:.1f}k of "
               f"{b['emp_2025_k_line_items']:.1f}k 2025 jobs ({100 * b['emp_2025_k_at_baseline'] / b['emp_2025_k_line_items']:.1f}%); "
               f"next most common value covers {b['second_mode_count']} line items. "
               "BLS adjustment = (1 + change) / (1 + baseline) − 1.\n",
               nem[["soc6", "role", "title", "emp_2025_k", "emp_2035_k", "change_pct", "change_vs_industry_pts",
                    "bls_adjustment_pct", "pct_ind_2025", "pct_ind_2035"]].round(1).to_markdown(index=False)]
    if outp is not None:
        md += ["\n\n## Industry employment and real output (BLS EP Table 2.11; ranks from Tables 2.6, 2.8, 2.10; DL-29)\n",
               outp.drop(columns=["type"]).round(2).to_markdown(index=False)]
    if jzres is not None:
        a = jz_sum.attrs
        md += ["\n\n## BLS adjustment by O*NET Job Zone, NEM 336300 line items (DL-34)\n",
               f"{a['n_with_job_zone']} of {a['n_line_items']} line items have a mapped Job Zone (zone 2 = O*NET 31.0's merged "
               f"'1–2'). Spearman rho = {a['spearman_rho']:.3f} (p = {a['spearman_p']:.2g}). Up / down: adjustment "
               f"> +{ADJ_TOL} / < −{ADJ_TOL} points.\n", jz_sum.round(2).to_markdown(index=False)]
        s = auto_adj
        md += ["\n\n## Adjusted line items whose BLS factor mentions robots or automation (DL-39)\n",
               f"Of {s['n_line_items']} NEM 336300 line items, {s['n_adjusted']} are adjusted (|adjustment| > {ADJ_TOL} points); "
               f"{s['n_adjusted_citing_automation']} of them ({s['n_up_citing']} up, {s['n_down_citing']} down) have a Table 1.12 "
               f"factor for 336300 or all industries matching `{AUTOMATION_PATTERN}`. Jobs 2025: "
               f"{s['jobs_citing_automation_k']:.1f}k of {s['jobs_adjusted_k']:.1f}k adjusted "
               f"({100 * s['jobs_citing_automation_k'] / s['jobs_adjusted_k']:.1f}%).\n"]
    md += ["\n\n## BLS Table 1.12 factors that mention robots or automation (DL-28)\n",
           f"Pattern: `{AUTOMATION_PATTERN}` (case-insensitive). {int(auto_grp.rows.sum())} rows, "
           f"{len(auto_occ)} occupations: {int((auto_occ.direction == 'down').sum())} down, "
           f"{int((auto_occ.direction == 'up').sum())} up, {int((auto_occ.direction == 'mixed').sum())} mixed. "
           "Row counts repeat one sentence per industry; read the occupation counts.\n",
           auto_grp.to_markdown(index=False),
           "\n\nOccupations whose share BLS raises in a factor that mentions robots or automation:\n",
           auto_occ[auto_occ.direction != "down"][["occ_code", "occ_title", "n_rows", "n_distinct_texts", "in_336300"]]
           .to_markdown(index=False)]
    (out / "mix_summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return {"factors": fac, "nem": nem, "automation_occ": auto_occ, "automation_groups": auto_grp,
            "industry_output": outp, "job_zone": jzres, "automation_adjusted": auto_adj}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=None)
    args = ap.parse_args(argv)
    res = run(load_config(args.config))
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
    if res["nem"] is not None:
        print(res["nem"][["soc6", "role", "title", "change_pct", "bls_adjustment_pct"]].round(1).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
