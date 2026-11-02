"""Track record of BLS employment projections for NAICS 3363 (analysis log DL-38, readings DL-40).

  Industry    For each archived projection vintage (2008-18, 2010-20, 2012-22, 2014-24): base-year and projected
              target-year employment of industry 336300 (line item 00-0000 x 336300 of the archive's National
              Employment Matrix) against the CES annual average of the base and target years (CEU3133630001).
              Error = projected / actual - 1; direction correct = projected and actual change from the base year
              have the same sign; base-year gap = archive base / CES base - 1. The 2020 target year is marked.
  Occupations 2014-24 vintage: NEM 336300 line items whose 2010 SOC code maps to exactly one 2018 SOC code with no
              other 2010 source (BLS 2010 -> 2018 SOC crosswalk) and that have numeric OEWS employment in NAICS
              336300 in May 2014 and May 2024. Projected 2014-24 change vs observed OEWS change; share with the
              correct direction (count and May 2014 employment-weighted); Spearman correlation; share error
              (sum of absolute differences of within-set shares) for BLS and for a constant-share naive model
              that holds each occupation's 2014 NEM share.

Inputs:  data/raw/ep_archive/<vintage>.zip, data/raw/ces_2008/<BLS series report>.xlsx,
         data/raw/oews_history/oesm14in4.zip, oesm24in4.zip, data/raw/soc/soc_2010_to_2018_crosswalk.xlsx
Outputs: outputs/track_record/industry_vintages.csv, occupation_2014_24.csv, frame_2014_24.csv,
         ces_annual_2008_2026.csv (figure input), track_record_summary.md
Usage:   python -m src.track_record
"""
from __future__ import annotations

import argparse
import io
import warnings
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from .config import REPO_ROOT, load_config, repo_path
from .history import read_year

VINTAGES = {"2008-18": (2008, 2018), "2010-20": (2010, 2020), "2012-22": (2012, 2022), "2014-24": (2014, 2024)}
INDUSTRY = "336300"
PANDEMIC_TARGET = 2020
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _clean(s: pd.Series) -> pd.Series:
    return s.astype(str).str.replace('"', "", regex=False).str.replace("=", "", regex=False).str.strip()


def read_matrix(path: Path, vintage: str) -> pd.DataFrame:
    """One archived matrix as columns line_item (occupation), occ_code, ind_code, base_k, proj_k (thousands)."""
    with zipfile.ZipFile(path) as zf:
        member = next(n for n in zf.namelist() if n.lower().endswith(("matrix.txt", "matrix.csv", "matrix.xlsx")))
        raw = zf.read(member)
    if vintage == "2008-18":       # semicolon delimited, no header, employment in jobs
        t = pd.read_csv(io.BytesIO(raw), sep=";", header=None, dtype=str, encoding="latin-1")
        t = t.iloc[:, :8]
        t.columns = ["occ_type", "ind_type", "occ_code", "ind_code", "base", "_b1", "_b2", "proj"]
        scale = 1000.0
    elif member.lower().endswith(".xlsx"):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            t = pd.read_excel(io.BytesIO(raw), sheet_name=0, dtype=str)
        t = t.rename(columns={"Occupation type": "occ_type", "Industry type": "ind_type", "Occupation code": "occ_code",
                              "Industry code": "ind_code", "Occupation title": "occ_title"})
        b, p = VINTAGES[vintage]
        t = t.rename(columns={f"{b} Employment": "base", f"{p} Employment": "proj"})
        scale = 1.0
    else:                          # 2010-20 tab delimited, 2012-22 comma delimited; thousands
        sep = "\t" if member.lower().endswith(".txt") else ","
        t = pd.read_csv(io.BytesIO(raw), sep=sep, dtype=str, encoding="latin-1")
        b, p = VINTAGES[vintage]
        cols = {c: c.strip() for c in t.columns}
        t = t.rename(columns=cols)
        low = {c.lower(): c for c in t.columns}
        t = t.rename(columns={low["occupation type"]: "occ_type", low["industry type"]: "ind_type",
                              low["occupation code"]: "occ_code", low["industry code"]: "ind_code",
                              low[f"{b} employment"]: "base", low[f"{p} employment"]: "proj"})
        scale = 1.0
    for c in ("occ_type", "ind_type", "occ_code", "ind_code"):
        t[c] = _clean(t[c])
    t["line_item"] = t["occ_type"].str.lower().isin(["0", "line item"])
    t["base_k"] = pd.to_numeric(_clean(t["base"]).str.replace(",", "", regex=False), errors="coerce") / scale
    t["proj_k"] = pd.to_numeric(_clean(t["proj"]).str.replace(",", "", regex=False), errors="coerce") / scale
    keep = ["line_item", "occ_code", "ind_code", "base_k", "proj_k"] + (["occ_title"] if "occ_title" in t.columns else [])
    return t[keep].assign(vintage=vintage, source=f"{path.name}:{member}")


def ces_annual(path: Path) -> pd.Series:
    """Annual averages (thousands) of complete calendar years from a BLS series-report workbook."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        x = pd.read_excel(path, header=None)
    hdr_row = next(i for i in range(len(x)) if str(x.iloc[i, 0]).strip() == "Year")
    body = x.iloc[hdr_row + 1:].copy()
    body.columns = [str(c).strip() for c in x.iloc[hdr_row]]
    body = body[pd.to_numeric(body["Year"], errors="coerce").notna()]
    m = body.set_index(body["Year"].astype(int))[MONTHS].apply(pd.to_numeric, errors="coerce")
    full = m.notna().sum(axis=1) == 12
    return m[full].mean(axis=1)


def industry_vintages(cfg: dict[str, Any], root: Path) -> pd.DataFrame:
    arch = repo_path("data/raw/ep_archive", root)
    ces_file = sorted(repo_path("data/raw/ces_2008", root).glob("*.xlsx"))[-1]
    ces = ces_annual(ces_file)
    rows = []
    for v, (b, p) in VINTAGES.items():
        m = read_matrix(arch / f"{v}.zip", v)
        r = m[(m.occ_code == "00-0000") & (m.ind_code == INDUSTRY)]
        if len(r) == 0:
            rows.append({"vintage": v, "base_year": b, "target_year": p, "available": False})
            continue
        r = r.iloc[0]
        proj_chg = 100 * (r.proj_k / r.base_k - 1)
        act_chg = 100 * (ces[p] / ces[b] - 1)
        rows.append({"vintage": v, "base_year": b, "target_year": p, "available": True,
                     "archive_base_k": r.base_k, "archive_proj_k": r.proj_k, "ces_base_k": ces[b], "ces_target_k": ces[p],
                     "base_gap_pct": 100 * (r.base_k / ces[b] - 1), "projected_change_pct": proj_chg,
                     "actual_change_pct": act_chg, "error_pct": 100 * (r.proj_k / ces[p] - 1),
                     "direction_correct": bool(np.sign(proj_chg) == np.sign(act_chg)),
                     "pandemic_target_year": p == PANDEMIC_TARGET, "ces_file": ces_file.name, "source": r.source})
    return pd.DataFrame(rows)


def soc_one_to_one(path: Path) -> dict[str, str]:
    """2010 SOC -> 2018 SOC for codes that map one-to-one in both directions."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        x = pd.read_excel(path, header=None, dtype=str)
    hdr = next(i for i in range(len(x)) if str(x.iloc[i, 0]).strip() == "2010 SOC Code")
    t = x.iloc[hdr + 1:, :4].copy()
    t.columns = ["c10", "t10", "c18", "t18"]
    t = t.dropna(subset=["c10", "c18"])
    t["c10"], t["c18"] = t.c10.str.strip(), t.c18.str.strip()
    n10 = t.groupby("c10").c18.nunique(); n18 = t.groupby("c18").c10.nunique()
    one = t[t.c10.map(n10).eq(1) & t.c18.map(n18).eq(1)]
    return dict(zip(one.c10, one.c18))


def occupation_2014_24(cfg: dict[str, Any], root: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    m = read_matrix(repo_path("data/raw/ep_archive", root) / "2014-24.zip", "2014-24")
    nem = m[(m.ind_code == INDUSTRY) & m.line_item & (m.occ_code != "00-0000")].copy()
    o14 = read_year(repo_path("data/raw/oews_history", root) / "oesm14in4.zip", 2014)
    o24 = read_year(repo_path("data/raw/oews_history", root) / "oesm24in4.zip", 2024)
    e14 = o14[o14.O_GROUP == "detailed"].set_index("OCC_CODE").TOT_EMP
    e24 = o24[o24.O_GROUP == "detailed"].set_index("OCC_CODE").TOT_EMP
    one = soc_one_to_one(repo_path("data/raw/soc", root) / "soc_2010_to_2018_crosswalk.xlsx")
    nem["soc2018"] = nem.occ_code.map(one)
    nem["oews_2014"] = nem.occ_code.map(e14)
    nem["oews_2024"] = nem.soc2018.map(e24)
    nem["reason"] = np.select(
        [nem.soc2018.isna(), nem.oews_2014.isna(), nem.oews_2024.isna()],
        ["no one-to-one 2010->2018 SOC match", "no numeric OEWS May 2014 employment", "no numeric OEWS May 2024 employment"],
        "compared")
    nem["projected_change_pct"] = 100 * (nem.proj_k / nem.base_k - 1)
    nem["observed_change_pct"] = 100 * (nem.oews_2024 / nem.oews_2014 - 1)
    c = nem[nem.reason == "compared"].copy()
    c["direction_correct"] = np.sign(c.projected_change_pct) == np.sign(c.observed_change_pct)
    c["share_proj"] = c.proj_k / c.proj_k.sum()
    c["share_naive"] = c.base_k / c.base_k.sum()
    c["share_actual"] = c.oews_2024 / c.oews_2024.sum()
    nem = nem.merge(c[["occ_code", "direction_correct", "share_proj", "share_naive", "share_actual"]], on="occ_code", how="left")
    rho = spearmanr(c.projected_change_pct, c.observed_change_pct)
    summ = {"n_line_items": len(nem), "n_compared": len(c),
            "excluded": nem[nem.reason != "compared"].reason.value_counts().to_dict(),
            "direction_correct_n": int(c.direction_correct.sum()),
            "direction_correct_share_pct": 100 * float(c.direction_correct.mean()),
            "direction_correct_emp_weighted_pct": 100 * float((c.direction_correct * c.oews_2014).sum() / c.oews_2014.sum()),
            "spearman_rho": float(rho.statistic), "spearman_p": float(rho.pvalue),
            "share_error_bls_pts": 100 * float((c.share_proj - c.share_actual).abs().sum()),
            "share_error_naive_pts": 100 * float((c.share_naive - c.share_actual).abs().sum()),
            "industry_projected_change_pct": None}
    tot = m[(m.occ_code == "00-0000") & (m.ind_code == INDUSTRY)].iloc[0]
    summ["industry_projected_change_pct"] = float(100 * (tot.proj_k / tot.base_k - 1))
    return nem, summ


def frame_listing(cfg: dict[str, Any], occ: pd.DataFrame, root: Path) -> pd.DataFrame:
    """The five maintenance targets and the twelve production feeders of II-B's frame (2018 codes) in the 2014-24 comparison."""
    roles = [(c, "maintenance target") for c in cfg["frame"]["targets_core"]] + \
            [(c, "production feeder (II-B frame)") for c in cfg["frame"]["feeders_core"]]
    rows = []
    for code18, role in roles:
        hit = occ[occ.soc2018 == code18]
        if len(hit):
            r = hit.iloc[0]
            rows.append({"soc2018": code18, "role": role, "nem_code_2010": r.occ_code, "status": r.reason,
                         "projected_change_pct": r.projected_change_pct, "observed_change_pct": r.observed_change_pct,
                         "direction_correct": r.direction_correct, "oews_2014": r.oews_2014, "oews_2024": r.oews_2024})
        else:
            rows.append({"soc2018": code18, "role": role, "nem_code_2010": None,
                         "status": "no one-to-one 2010 SOC source in the 2014-24 matrix"})
    return pd.DataFrame(rows)


def run(cfg: dict[str, Any], root: Path = REPO_ROOT) -> dict[str, Any] | None:
    need = [repo_path("data/raw/ep_archive", root) / f"{v}.zip" for v in VINTAGES] + [
        repo_path("data/raw/oews_history", root) / "oesm14in4.zip", repo_path("data/raw/soc", root) / "soc_2010_to_2018_crosswalk.xlsx"]
    missing = [p.name for p in need if not p.exists()] + ([] if list(repo_path("data/raw/ces_2008", root).glob("*.xlsx")) else ["ces_2008"])
    if missing:
        print(f"[skip] projection track record: inputs missing {missing} (DL-38)")
        return None
    out = repo_path("outputs/track_record", root); out.mkdir(parents=True, exist_ok=True)
    ind = industry_vintages(cfg, root)
    occ, summ = occupation_2014_24(cfg, root)
    fr = frame_listing(cfg, occ, root)
    ind.to_csv(out / "industry_vintages.csv", index=False)
    ces = ces_annual(sorted(repo_path("data/raw/ces_2008", root).glob("*.xlsx"))[-1])
    ces.rename("emp_k").rename_axis("year").reset_index().to_csv(out / "ces_annual_2008_2026.csv", index=False)
    occ.to_csv(out / "occupation_2014_24.csv", index=False)
    fr.to_csv(out / "frame_2014_24.csv", index=False)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    s = summ
    md = [f"# Track record of BLS projections for NAICS 3363 (DL-38, DL-40) — descriptive\n\nGenerated: {ts}\n",
          "## Industry employment: archived projections vs CES annual averages (thousands)\n",
          ind.drop(columns=["source", "ces_file"]).round(2).to_markdown(index=False),
          f"\n\nDirection correct in {int(ind.direction_correct.sum())} of {int(ind.available.sum())} vintages; "
          f"error range {ind.error_pct.min():+.1f}% to {ind.error_pct.max():+.1f}%.\n",
          "\n## Occupations, 2014-24 vintage: projected vs observed OEWS change inside NAICS 336300\n",
          f"Line items: {s['n_line_items']}; compared: {s['n_compared']}; excluded: {s['excluded']}.\n\n"
          f"Direction correct: {s['direction_correct_n']} of {s['n_compared']} ({s['direction_correct_share_pct']:.1f}%); "
          f"weighted by May 2014 employment {s['direction_correct_emp_weighted_pct']:.1f}%. Spearman rho "
          f"{s['spearman_rho']:.3f} (p = {s['spearman_p']:.2g}). Share error (sum of |share difference|, points): BLS "
          f"{s['share_error_bls_pts']:.2f}, constant-share naive model {s['share_error_naive_pts']:.2f}. "
          f"Industry projected change 2014-24 in the matrix: {s['industry_projected_change_pct']:+.1f}%.\n",
          "\n### Maintenance targets and production feeders (II-B frame)\n", fr.round(1).to_markdown(index=False)]
    (out / "track_record_summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return {"industry": ind, "occupations": occ, "summary": summ, "frame": fr}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=None)
    args = ap.parse_args(argv)
    res = run(load_config(args.config))
    if res is None:
        return 0
    pd.set_option("display.width", 220)
    print(res["industry"].drop(columns=["source", "ces_file"]).round(2).to_string(index=False))
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in res["summary"].items()})
    print(res["frame"].round(1).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
