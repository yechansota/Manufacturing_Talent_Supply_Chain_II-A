"""Output audit (E-checks): every reported number is re-derived from the raw files or cross-checked.

  E1  analysis log: copied DL entries are exactly the shared set and byte-identical to the copy made at the split;
      AL ids contiguous and unique
  E2  figures newer than the outputs they draw
  E3  CES series parsed correctly; its 2025 annual average equals the NEM 2025 industry total (DL-26)
  E4  BLS National Employment Matrix (NAICS 336300) parsed and internally consistent (DL-23)
  E5  NEM 2025 staffing pattern agrees with OEWS May 2025 inside 3363; levels differ by a common factor
  E6  projection track record (DL-38): archive totals re-read as raw text / openpyxl, CES annual averages with openpyxl;
      errors and directions recomputed; occupation metrics recomputed from the comparison file
  E7  industry output (DL-29): Table 2.11 agrees with Table 2.8 and with the NEM 336300 totals; ranks and output per job
  E8  BLS Table 1.12 factors present in the raw workbook as reported (DL-14)
  E9  two-stage NEM reading (DL-28): baseline occupations are exactly those without a BLS factor; adjustments and
      automation-factor counts re-derived from the raw files
  E10 adjusted NEM 336300 line items whose BLS factor mentions robots or automation (DL-39): re-derived from the raw
      Table 1.12 (openpyxl) and the raw NEM CSV (csv module)
  E11 BLS adjustment by Job Zone (DL-34): re-derived from the raw NEM CSV (csv module), the crosswalk workbook and
      job_zones.csv; counts, means, employment and Spearman rho
  E12 OEWS history (DL-29): May 2021 and 2025 values re-read from the raw zips; 2025 equals the ingest; SHA-256 in
      MANIFEST
  E13 skill shift (DL-30): level differences and software / task counts re-derived from the raw O*NET CSVs
  E14 multiple comparisons, endpoints and rule choice (DL-32): BH at decision_rules.fdr_q re-derived by a step-up
      search for the skill-shift comparison; premium z re-derived from the yearly OEWS file; floor-map no-close counts
      under four rules re-derived from the pair file; bootstrap pairs equal the eligible pairs
  E15 CPS age profile and flows (DL-44): A1 counts and weighted 55+ shares, A2 and A3 counts re-derived from the raw
      files with string slicing and dict-based linkers; A2 pairs employed at t equal the production -> maintenance
      pairs of an employed-records linker (internal consistency)
  E16 floor succession map (DL-31): D and P re-derived from the raw O*NET CSVs for two target positions; eligibility
      re-derived from OEWS and Job Zones; summary counts consistent with the pair file
  E17 cross-part link columns (DL-33): each position's count as a close source, its count over maintenance targets and
      the production share of each close pool re-derived from the pair file

Numbering of this repository (II-A); the mapping to the original single-repository numbering is in
docs/Technical Documentation.md.

Status: PASS / NOTE (true, must be disclosed) / FLAG (needs a decision).
Outputs: outputs/review/output_audit.csv, output_audit.md
Usage:   python -m src.output_audit
"""
from __future__ import annotations

import argparse
import hashlib
import math
import re
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pandas as pd

from .config import REPO_ROOT, load_config, repo_path

ROWS: list[dict[str, str]] = []
SHARED_DL = [14, 22, 23, 26, 28, 29, 30, 31, 32, 33, 34, 36, 37, 38, 39, 40, 41, 42, 44]   # verbatim from II-B (DL-36c, AL-1)
SHARED_DL_SHA256 = "d44f52c416be629ed43f6a8124ce5539289a66dadad0c2f9c81b75ddadc90704"   # of the DL rows joined by newlines, at the split


def check(cid: str, title: str, status: str, detail: str) -> None:
    ROWS.append({"id": cid, "check": title, "status": status, "detail": detail})


def run(cfg: dict[str, Any], root: Path = REPO_ROOT) -> pd.DataFrame:
    ROWS.clear()
    prc, trd = repo_path("outputs/mix", root), repo_path("outputs/trend", root)
    with duckdb.connect(str(repo_path(cfg["paths"]["duckdb"], root)), read_only=True) as con:
        oews = con.execute("SELECT * FROM oews_3363").df().set_index("OCC_CODE")

    # E1 ------------------------------------------------------------------------------------------
    log = repo_path("outputs/analysis_log.md", root).read_text(encoding="utf-8")
    dl = [int(x) for x in re.findall(r"^\| DL-(\d+) \|", log, flags=re.M)]
    al = [int(x) for x in re.findall(r"^\| AL-(\d+) \|", log, flags=re.M)]
    dl_text = "\n".join(l for l in log.splitlines() if re.match(r"^\| DL-\d+ \|", l))
    same = hashlib.sha256(dl_text.encode("utf-8")).hexdigest() == SHARED_DL_SHA256
    ok = dl == SHARED_DL and same and al == list(range(1, len(al) + 1)) and len(al) >= 1
    check("E1", "Analysis log: copied DL entries are the shared set, unchanged since the split; AL ids contiguous and unique",
          "PASS" if ok else "FLAG", f"DL rows {dl}; SHA-256 of the DL rows equals the split copy: {same}; "
          f"AL-1 … AL-{max(al) if al else 0} ({len(al)} rows)")

    # E2 ------------------------------------------------------------------------------------------
    fig = repo_path("figures", root)
    deps = {"fig1_observed_trend.png": trd / "ces_3363_annual.csv",
            "fig2_projection_track_record.png": repo_path("outputs/track_record", root) / "industry_vintages.csv",
            "fig3_automation_shift.png": prc / "nem_336300.csv",
            "fig4_maintenance_mix.png": repo_path("outputs/history", root) / "maintenance_mix.csv",
            "fig5_cps_aging_flows.png": repo_path("outputs/cps_flows", root) / "a3_balance.csv",
            "fig6_floor_bench.png": repo_path("outputs/floor_map", root) / "position_summary.csv",
            "figS1_adjustment_by_job_zone.png": prc / "bls_adjustment_by_occupation_job_zone.csv"}
    deps = {f: dep for f, dep in deps.items() if dep.exists()}          # optional layers may be absent
    stale = [f for f, dep in deps.items() if not (fig / f).exists() or (fig / f).stat().st_mtime < dep.stat().st_mtime]
    check("E2", "Figures are newer than the outputs they draw", "PASS" if not stale else "FLAG",
          "stale: " + ", ".join(stale) if stale else f"{len(deps)} figure/input pairs checked")

    # E4 -----------------------------------------------------------------------------------------
    from .mix import NEM_FILE, read_nem
    nem_path = repo_path(cfg["paths"]["raw_ep"], root) / NEM_FILE
    if not nem_path.exists():
        check("E4", "NEM 336300 within-industry projections (DL-23)", "NOTE", "optional input not present; layer skipped")
    else:
        t = read_nem(nem_path)
        raw_t = pd.read_csv(nem_path, dtype=str, keep_default_na=False)
        ti = t.set_index("code")
        lvl1 = raw_t["Display Level"].astype(str).eq("1").to_numpy()
        major = t[lvl1]
        sum_dev = abs(major.emp_2025_k.sum() - ti.loc["00-0000", "emp_2025_k"])
        grp_dev = abs(ti.loc[["49-9041", "49-9043", "49-9044"], "emp_2025_k"].sum() - ti.loc["49-9040", "emp_2025_k"])
        chg_dev = float((t.emp_2035_k - t.emp_2025_k - t.change_k).abs().max())
        big = t[t.emp_2025_k >= 5]
        pct_dev = float((100 * big.change_k / big.emp_2025_k - big.change_pct).abs().max())
        want = set(cfg["frame"]["targets_core"] + cfg["frame"]["feeders_core"])
        missing = sorted(want - set(t.code))
        man = pd.read_csv(repo_path("data/raw/MANIFEST.csv", root)).set_index("path").sha256
        h = hashlib.sha256(nem_path.read_bytes()).hexdigest()
        in_man = man.get(f"data/raw/ep/{NEM_FILE}") == h
        out_nem = pd.read_csv(prc / "nem_336300.csv").set_index("soc6")
        same = all(abs(out_nem.loc[c, "change_pct"] - ti.loc[c, "change_pct"]) < 1e-9 for c in want if c in ti.index)
        ok = sum_dev <= 0.5 and grp_dev <= 0.15 and chg_dev <= 0.15 and pct_dev <= 1.0 and not missing and in_man and same
        check("E4", "NEM 336300 parsed and internally consistent (DL-23)", "PASS" if ok else "FLAG",
              f"{len(t)} rows; Σ major groups − total = {sum_dev:.1f}k (rounding); 49-9040 parts − group = {grp_dev:.2f}k; "
              f"max |2035 − 2025 − change| = {chg_dev:.2f}k; max |recomputed % − published %| (≥5k jobs) = {pct_dev:.2f} pts; "
              f"frame codes missing: {missing or 'none'}; SHA-256 in MANIFEST={in_man}; output equals source={same}")

    # E5 -----------------------------------------------------------------------------------------
    if nem_path.exists():
        li = t[t.type == "Line Item"].set_index("code")
        o_all = oews.reset_index()
        tot_o = float(o_all.loc[o_all.OCC_CODE == "00-0000", "TOT_EMP"].iloc[0])
        lvl = o_all[o_all.O_GROUP.isin(["detailed", "broad"])].drop_duplicates("OCC_CODE").set_index("OCC_CODE")
        j = li.join(lvl[["TOT_EMP"]], how="inner").dropna(subset=["TOT_EMP"])
        j = j[j.index.isin(o_all[o_all.O_GROUP == "detailed"].OCC_CODE) | (j.index == "51-2090")]
        share_o = 100 * j.TOT_EMP / tot_o
        corr = float(np.corrcoef(share_o, j.pct_ind_2025)[0, 1])
        dmax = float((share_o - j.pct_ind_2025).abs().max())
        ratio_tot = float(ti.loc["00-0000", "emp_2025_k"] * 1000 / tot_o)
        big = j[j.TOT_EMP >= 5000]
        r_big = (big.emp_2025_k * 1000 / big.TOT_EMP)
        ok = corr > 0.999 and dmax < 0.1 and abs(r_big - ratio_tot).max() < 0.01
        check("E5", "NEM 2025 staffing pattern = OEWS May 2025 inside 3363; totals differ by a common factor",
              "PASS" if ok else "FLAG",
              f"{len(j)} matched occupations; share correlation {corr:.5f}; max |share difference| {dmax:.3f} pts "
              f"(NEM publishes shares to one decimal, so differences below 0.1 are within one rounding unit); NEM/OEWS total {ratio_tot:.4f}; occupations with ≥ 5,000 "
              f"jobs: level ratio {r_big.min():.3f}–{r_big.max():.3f}. Levels come from different control totals (NEM: CES-based "
              f"industry employment; OEWS: its own survey estimate); shares and percent changes are unaffected.")

    # E3 -----------------------------------------------------------------------------------------
    from .trend import SERIES, find_file, read_monthly
    ces = find_file(root)
    if ces is None:
        check("E3", "CES observed trend (DL-26)", "NOTE", "optional input not present; layer skipped")
    else:
        mm = read_monthly(ces)
        ann = pd.read_csv(trd / "ces_3363_annual.csv")
        redo = mm.assign(year=mm.date.dt.year).groupby("year").emp_k.agg(["mean", "size"])
        same = bool(np.allclose(redo["mean"].to_numpy(), ann.emp_k.to_numpy()) and (redo["size"].to_numpy() == ann.months.to_numpy()).all())
        months_ok = bool(mm.date.is_monotonic_increasing and not mm.date.duplicated().any()
                         and (mm.date.diff().dropna().dt.days.between(28, 31)).all())
        raw_head = pd.read_excel(ces, header=None, dtype=str).fillna("").astype(str) if ces.suffix == ".xlsx" else None
        nsa = raw_head is not None and raw_head.apply(lambda c: c.str.contains("Not Seasonally Adjusted", regex=False)).any().any()
        man = pd.read_csv(repo_path("data/raw/MANIFEST.csv", root)).set_index("path").sha256
        rel = ces.relative_to(root).as_posix()
        in_man = man.get(rel) == hashlib.sha256(ces.read_bytes()).hexdigest()
        a25 = float(ann.loc[(ann.year == 2025) & ann.complete, "emp_k"].iloc[0])
        nem25 = float(ti.loc["00-0000", "emp_2025_k"]) if nem_path.exists() else float("nan")
        ok = same and months_ok and in_man and (nsa or ces.suffix == ".csv") and abs(a25 - nem25) <= 0.05 + 1e-9
        check("E3", "CES parsed; 2025 annual average equals the NEM 2025 industry total (DL-26)", "PASS" if ok else "FLAG",
              f"{ces.name}: {len(mm)} months {mm.date.min():%Y-%m}–{mm.date.max():%Y-%m}, consecutive={months_ok}, "
              f"not seasonally adjusted={nsa}; annual averages re-derived={same}; 2025 CES average {a25:.2f}k vs NEM "
              f"2025 total {nem25:.1f}k; SHA-256 in MANIFEST={in_man}")

    # E8 ------------------------------------------------------------------------------------------
    path = repo_path(cfg["paths"]["raw_ep"], root) / cfg["data_versions"]["ep"]["occupation_file"]["file"]
    t12 = pd.read_excel(path, sheet_name="Table 1.12", header=1, dtype=str, keep_default_na=False)
    t12.columns = ["occ_title", "occ_code", "ind_title", "ind_code", "factor"]
    ind = t12.assign(c=t12.ind_code.str.strip()).drop_duplicates("c").set_index("c").ind_title.str.strip()
    bf = pd.read_csv(prc / "bls_factors.csv")
    bad = []
    for r in bf.itertuples():
        rows = t12[t12.occ_code.str.strip() == r.soc6]
        if r.factor_level == "no entry":
            if rows.ind_code.str.strip().isin(["336300", "TE1000"]).any():
                bad.append(f"{r.soc6} has a 336300/TE1000 row")
            if len(rows) != r.n_industry_rows:
                bad.append(f"{r.soc6} other-industry count {len(rows)} vs {r.n_industry_rows}")
        else:
            code = "336300" if r.factor_level.startswith("NAICS") else "TE1000"
            hit = rows[rows.ind_code.str.strip() == code]
            if hit.empty or hit.factor.iloc[0].strip() != str(r.factor_text).strip():
                bad.append(f"{r.soc6} text mismatch")
    check("E8", "BLS Table 1.12 factors match the raw workbook (DL-14)", "PASS" if not bad else "FLAG",
          f"{len(bf)} occupations checked; " + ("all match" if not bad else "; ".join(bad))
          + f"; 336300 = '{ind.get('336300', '?')}', TE1000 = '{ind.get('TE1000', '?')}'")

    # E9 -----------------------------------------------------------------------------------------
    if not nem_path.exists():
        check("E9", "Two-stage NEM reading (DL-28)", "NOTE", "optional NEM input not present; layer skipped")
    else:
        li = t[t["type"].str.contains("Line item", case=False)].set_index("code")
        base = float(li.change_pct.mode().iloc[0])
        occ_xlsx = repo_path(cfg["paths"]["raw_ep"], root) / cfg["data_versions"]["ep"]["occupation_file"]["file"]
        f12 = pd.read_excel(occ_xlsx, sheet_name="Table 1.12", header=1, dtype=str, keep_default_na=False)
        f12.columns = ["occ_title", "occ_code", "ind_title", "ind_code", "factor"]
        f12 = f12.apply(lambda c: c.str.strip())
        applies = set(f12.loc[f12.ind_code.isin(["336300", "TE1000"]), "occ_code"])
        at_base = li.change_pct == base
        has_f = li.index.isin(applies)
        exact = bool((at_base == ~has_f).all())
        nem_out = pd.read_csv(prc / "nem_336300.csv").set_index("soc6").drop(index="00-0000")
        adj = 100 * ((1 + nem_out.change_pct / 100) / (1 + base / 100) - 1)
        adj_ok = bool(np.allclose(adj, nem_out.bls_adjustment_pct) and (nem_out.baseline_change_pct == base).all())
        # automation-factor counts, re-derived row by row with plain Python
        occ_dir: dict[str, set] = {}
        n_rows = 0
        for code, text in zip(f12.occ_code, f12.factor):
            if not re.fullmatch(r"\d{2}-\d{4}", code) or not re.search(r"robot|automat", text, flags=re.I):
                continue
            n_rows += 1
            occ_dir.setdefault(code, set()).add("up" if "share increases" in text.lower() else "down")
        n_up = sum(v == {"up"} for v in occ_dir.values()); n_down = sum(v == {"down"} for v in occ_dir.values())
        summ = (prc / "mix_summary.md").read_text(encoding="utf-8")
        claim = f"{n_rows} rows, {len(occ_dir)} occupations: {n_down} down, {n_up} up"
        ok = exact and adj_ok and claim in summ
        check("E9", "Two-stage NEM reading: baseline = occupations without a BLS factor; adjustments and automation counts (DL-28)",
              "PASS" if ok else "FLAG",
              f"baseline {base:+.1f}% = mode of {len(li)} line items ({int(at_base.sum())} at baseline); "
              f"at baseline ⇔ no Table 1.12 row for 336300 or all industries: {exact} "
              f"({int((at_base & ~has_f).sum())} + {int((~at_base & has_f).sum())} of {len(li)}); "
              f"adjustments re-derived={adj_ok}; automation factors: {claim} (matches mix_summary.md: {claim in summ})")

    # E12 -----------------------------------------------------------------------------------------
    import io
    import warnings
    import zipfile
    from .history import zip_path
    man = pd.read_csv(repo_path("data/raw/MANIFEST.csv", root)).set_index("path").sha256
    hist = repo_path("outputs/history/maintenance_mix.csv", root)
    if not hist.exists():
        check("E12", "OEWS history (DL-29)", "NOTE", "optional input not present; layer skipped")
    else:
        mix = pd.read_csv(hist)
        codes = list(cfg["frame"]["targets_core"])
        ok_vals, notes = True, []
        for y in (2021, 2025):
            zp = zip_path(y, cfg, root)
            with zipfile.ZipFile(zp) as zf:
                mem = [n for n in zf.namelist() if n.endswith(f"nat4d_M{y}_dl.xlsx")]
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    raw = pd.read_excel(io.BytesIO(zf.read(mem[0])), dtype=str)
            raw.columns = [c.upper() for c in raw.columns]
            raw = raw[(raw.NAICS.str.strip() == "336300") & raw.OCC_CODE.isin(codes)].drop_duplicates("OCC_CODE").set_index("OCC_CODE")
            got = mix[mix.year.astype(str) == str(y)].set_index("soc6")
            e_ok = all(float(raw.loc[c, "TOT_EMP"].replace(",", "")) == float(got.loc[c, "emp"]) for c in codes)
            w_ok = all(np.isclose(float(raw.loc[c, "H_MEAN"]), float(got.loc[c, "h_mean"])) for c in codes)
            ok_vals &= e_ok and w_ok and len(mem) == 1
            notes.append(f"{y}: employment {e_ok}, mean wage {w_ok}")
        with duckdb.connect(str(repo_path(cfg["paths"]["duckdb"], root)), read_only=True) as con:
            reg = con.execute("SELECT OCC_CODE, TOT_EMP FROM oews_3363").df().set_index("OCC_CODE").TOT_EMP
        y25 = mix[mix.year.astype(str) == "2025"].set_index("soc6")
        same25 = all(float(reg[c]) == float(y25.loc[c, "emp"]) for c in codes)
        hashes = all(man.get(f"data/raw/oews_history/oesm{y % 100:02d}in4.zip") ==
                     hashlib.sha256(zip_path(y, cfg, root).read_bytes()).hexdigest() for y in (2021, 2022, 2023, 2024))
        ok = ok_vals and same25 and hashes
        check("E12", "OEWS history re-read from raw zips; 2025 equals the ingest (DL-29)", "PASS" if ok else "FLAG",
              "; ".join(notes) + f"; 2025 = oews_3363 ingest: {same25}; 2021–2024 SHA-256 in MANIFEST: {hashes}")

    # E13 -----------------------------------------------------------------------------------------
    lev_p = repo_path("outputs/skill_shift/level_differences.csv", root)
    if not lev_p.exists():
        check("E13", "Skill shift (DL-30)", "NOTE", "layer not run")
    else:
        lev = pd.read_csv(lev_p)
        ro = repo_path(cfg["paths"]["raw_onet"], root)
        lv_id = cfg["measurement"]["scales"]["level"]["id"]
        parts = []
        for f in ("knowledge.csv", "essential_skills.csv", "transferable_skills.csv"):
            r = pd.read_csv(ro / f, dtype=str, keep_default_na=False)
            parts.append(r[(r["Scale ID"] == lv_id) & r["O*NET-SOC Code"].isin(["49-9041.00", "49-9043.00"])])
        r = pd.concat(parts)
        r["v"] = r["Data Value"].astype(float); r["se"] = pd.to_numeric(r["Standard Error"], errors="coerce")
        pa = r[r["O*NET-SOC Code"] == "49-9041.00"].set_index("Element ID"); pb = r[r["O*NET-SOC Code"] == "49-9043.00"].set_index("Element ID")
        d = (pa.v - pb.v).dropna(); z = d / np.sqrt(pa.se ** 2 + pb.se ** 2)
        mine = lev[lev.other == "49-9043.00"].set_index("element_id")
        d_ok = bool(np.allclose(mine.loc[d.index, "diff"], d))
        zz = z.replace([np.inf, -np.inf], np.nan)
        z_ok = bool(np.allclose(mine.loc[zz.index, "z"].fillna(-999), zz.fillna(-999)))
        counts = (int((zz > 1.96).sum()), int((zz < -1.96).sum()))
        st_p = repo_path("outputs/skill_shift/software_and_tasks.csv", root)
        sw_ok = True
        if st_p.exists():
            import csv
            st = pd.read_csv(st_p).set_index("onet_code")
            n_ctl: dict[str, int] = {}
            with open(ro / "software_skills.csv", newline="", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    if row["Element Name"] == "Industrial control software":
                        n_ctl[row["O*NET-SOC Code"]] = n_ctl.get(row["O*NET-SOC Code"], 0) + 1
            sw_ok = all(int(st.loc[c, "industrial_control_examples"]) == n_ctl.get(c, 0) for c in st.index)
        ok = d_ok and z_ok and sw_ok
        check("E13", "Skill shift re-derived from the raw O*NET CSVs (DL-30)", "PASS" if ok else "FLAG",
              f"49-9041 vs 49-9043: {len(d)} elements, differences equal={d_ok}, z equal={z_ok}, z > 1.96: {counts[0]}, "
              f"z < −1.96: {counts[1]}; industrial-control counts re-derived with the csv module: {sw_ok}")

    # E7 -----------------------------------------------------------------------------------------
    io_p = prc / "industry_output.csv"
    if not io_p.exists():
        check("E7", "Industry output (DL-29)", "NOTE", "optional input not present; layer skipped")
    else:
        io_t = pd.read_csv(io_p).set_index("code")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            t28 = pd.read_excel(repo_path(cfg["paths"]["raw_ep"], root) / "industry.xlsx", sheet_name="Table 2.8", header=1, dtype=str)
        r28 = t28[t28.iloc[:, 0].astype(str).str.strip() == "Motor vehicle parts manufacturing"].iloc[0]
        p = io_t.loc["336300"]
        out_ok = float(r28.iloc[3]) == p.output_2025_bn and float(r28.iloc[4]) == p.output_2035_bn
        nem_ok = (abs(float(ti.loc["00-0000", "emp_2025_k"]) - p.emp_2025_k) < 1e-9
                  and abs(float(ti.loc["00-0000", "emp_2035_k"]) - p.emp_2035_k) < 1e-9) if nem_path.exists() else False
        opj = 100 * ((p.output_2035_bn / p.emp_2035_k) / (p.output_2025_bn / p.emp_2025_k) - 1)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            t11 = pd.read_excel(repo_path(cfg["paths"]["raw_ep"], root) / "industry.xlsx", sheet_name="Table 2.11", header=1, dtype=str)
        t11 = t11[t11.iloc[:, 2].astype(str).str.strip() == "Line item"]
        num = t11.iloc[:, [3, 4, 8, 9]].apply(pd.to_numeric, errors="coerce").dropna()
        g = (num.iloc[:, 3] / num.iloc[:, 1]) / (num.iloc[:, 2] / num.iloc[:, 0]) - 1
        cnt_ok = len(num) == p.n_industries_with_output and int((g < 0).sum()) == p.n_output_per_job_falling \
            and int(g.idxmin() == t11.index[t11.iloc[:, 1].astype(str).str.strip() == "336300"][0]) == (p.rank_output_per_job_change == 1)
        ok = (out_ok and nem_ok and np.isclose(opj, p.output_per_job_change_pct) and p["rank_2.8"] == 1 and p["rank_2.10"] == 1
              and cnt_ok)
        check("E7", "Industry output: Table 2.11 = Table 2.8 = NEM totals; ranks; output per job (DL-29)", "PASS" if ok else "FLAG",
              f"336300 output {p.output_2025_bn} → {p.output_2035_bn} bn (Table 2.8 match {out_ok}); jobs {p.emp_2025_k} → "
              f"{p.emp_2035_k}k (NEM match {nem_ok}); output per job {opj:+.1f}%; rank: largest employment declines "
              f"{int(p['rank_2.6'])}, most rapid output decline {int(p['rank_2.8'])}, largest output decline {int(p['rank_2.10'])}; "
              f"output per job falls in {int(p.n_output_per_job_falling)} of {int(p.n_industries_with_output)} industries with output, "
              f"336300 rank {int(p.rank_output_per_job_change)} (re-derived {cnt_ok}); "
              f"SHA-256 in MANIFEST={man.get('data/raw/ep/industry.xlsx') == hashlib.sha256((repo_path(cfg['paths']['raw_ep'], root) / 'industry.xlsx').read_bytes()).hexdigest()}")

    # E16 -----------------------------------------------------------------------------------------
    fm = repo_path("outputs/floor_map", root)
    if not (fm / "position_summary.csv").exists():
        check("E16", "Floor succession map (DL-31)", "NOTE", "layer not run")
    else:
        pos = pd.read_csv(fm / "position_summary.csv").set_index("soc6")
        prs = pd.read_csv(fm / "succession_pairs.csv")
        ro = repo_path(cfg["paths"]["raw_onet"], root)
        sk = pd.concat([pd.read_csv(ro / f, dtype=str, keep_default_na=False) for f in ("essential_skills.csv", "transferable_skills.csv")])
        sk["v"] = sk["Data Value"].astype(float)
        Lr = sk[sk["Scale ID"] == "LV"].pivot_table(index="O*NET-SOC Code", columns="Element ID", values="v")
        Ir = sk[sk["Scale ID"] == "IM"].pivot_table(index="O*NET-SOC Code", columns="Element ID", values="v").loc[Lr.index, Lr.columns]
        Zr = (Lr - Lr.mean()) / Lr.std(ddof=1); Wr = (Ir - 1).clip(0, 4)
        maxd = 0.0
        for t in ("49-9041", "51-1011"):
            tc = pos.at[t, "onet_codes"].split(";")
            zt, wt = Zr.loc[tc].mean(), Wr.loc[tc].mean()
            ref = Zr.drop(index=tc)
            dref = (wt * (zt - ref).clip(lower=0)).sum(axis=1) / wt.sum()
            g = prs[prs.target == t]
            for s_, Pg, Dg in zip(g.source, g.P, g.D):
                zs = Zr.loc[pos.at[s_, "onet_codes"].split(";")].mean()
                d = float((wt * (zt - zs).clip(lower=0)).sum() / wt.sum())
                p_ = 100 * float((dref <= d + 1e-12).mean())
                maxd = max(maxd, abs(d - Dg), abs(p_ - Pg))
        jz = pd.read_csv(ro / "job_zones.csv", dtype=str).set_index("O*NET-SOC Code")["Job Zone"].astype(int)
        jzs = {s_: max(int(jz[c]) for c in pos.at[s_, "onet_codes"].split(";")) for s_ in pos.index}
        el = [(pos.at[a_, "a_median"] < pos.at[b_, "a_median"]) and (jzs[a_] <= jzs[b_]) for a_, b_ in zip(prs.source, prs.target)]
        el_ok = bool((np.array(el) == prs.eligible.to_numpy()).all())
        cnt = prs[prs.eligible & (prs.P <= 25)].groupby("target").size().reindex(pos.index, fill_value=0)
        cnt_ok = bool((cnt == pos.n_close_sources).all())
        n_none, jobs_none = int(pos.flag_no_close_internal_source.sum()), int(pos[pos.flag_no_close_internal_source].jobs_2025.sum())
        ok = maxd < 1e-9 and el_ok and cnt_ok and len(pos) == 33
        check("E16", "Floor succession map: D, P re-derived from raw O*NET; eligibility and counts (DL-31)", "PASS" if ok else "FLAG",
              f"{len(pos)} positions, {len(prs)} pairs; targets 49-9041 and 51-1011 re-derived from the raw CSVs: max |diff| "
              f"{maxd:.2g}; eligibility re-derived={el_ok}; close counts match={cnt_ok}; no close internal successor: "
              f"{n_none} positions, {jobs_none:,} jobs; unrestricted nearest source earns more in "
              f"{int(pos.nearest_any_earns_more.sum())} of {len(pos)}")

    # E14 -----------------------------------------------------------------------------------------
    def step_up(p: np.ndarray, q: float) -> np.ndarray:
        """Benjamini-Hochberg as the textbook step-up search (independent of the adjusted-p code path)."""
        o = np.argsort(p, kind="stable"); n = len(p)
        ok_k = [k for k in range(1, n + 1) if p[o][k - 1] <= k * q / n]
        rej = np.zeros(n, bool)
        if ok_k:
            rej[o[:max(ok_k)]] = True
        return rej

    q_fdr = float(cfg["decision_rules"]["fdr_q"])

    notes, ok = [], True
    if lev_p.exists():
        lev = pd.read_csv(lev_p)
        g = lev[(lev.other == "49-9043.00") & lev.z.notna()]
        pz = np.array([math.erfc(abs(z) / math.sqrt(2)) for z in g.z])
        r2 = step_up(pz, q_fdr)
        bh_ok = bool((r2 == g.bh_reject.to_numpy()).all())
        hi, lo = int((r2 & (g.z > 0).to_numpy()).sum()), int((r2 & (g.z < 0).to_numpy()).sum())
        ok &= bh_ok
        notes.append(f"skill shift 49-9041 vs 49-9043: BH re-derived={bh_ok}, higher {hi}, lower {lo} of {len(g)}")
    if hist.exists():
        hh = pd.read_csv(repo_path("outputs/history/oews_3363_2021_2025.csv", root))
        w = hh.pivot_table(index="year", columns="OCC_CODE", values="H_MEAN", aggfunc="first")
        r_ = hh.pivot_table(index="year", columns="OCC_CODE", values="MEAN_PRSE", aggfunc="first")
        mix = pd.read_csv(hist)
        zs = []
        for y0 in (2021, 2022):
            d = math.log(w.at[2025, "49-9041"] / w.at[2025, "49-9043"]) - math.log(w.at[y0, "49-9041"] / w.at[y0, "49-9043"])
            se = math.sqrt(sum(r_.at[y, c] ** 2 for y in (y0, 2025) for c in ("49-9041", "49-9043"))) / 100
            got = float(mix[(mix.year.astype(str) == f"{y0}-2025") & (mix.soc6 == "49-9043")].premium_mean_change_z.iloc[0])
            zs.append((d / se, got))
        z_ok = all(abs(a_ - b_) < 1e-9 for a_, b_ in zs)
        ok &= z_ok
        notes.append(f"premium over 49-9043 re-derived from the yearly file: z 2021→25 {zs[0][0]:.1f}, "
                     f"2022→25 {zs[1][0]:.1f} (match {z_ok})")
    if (fm / "rule_variants.csv").exists():
        rv = pd.read_csv(fm / "rule_variants.csv")
        prs = pd.read_csv(fm / "succession_pairs.csv")
        pos = pd.read_csv(fm / "position_summary.csv").set_index("soc6")
        tw, tj = prs.target.map(pos.a_median), prs.target.map(pos.job_zone)
        redo = {}
        for key, wf, thr in (("base", 1.0, 25), ("stricter", 1.0, 15), ("looser", 1.0, 35), ("lateral", 1.10, 25)):
            el = (prs.source_wage < wf * tw) & (prs.source_job_zone <= tj) & (prs.P <= thr)
            redo[key] = len(pos) - prs[el].target.nunique()
        got = {k: int(rv[rv.variant.str.startswith(k)].n_no_close.iloc[0]) for k in redo}
        rv_ok = redo == got
        fb = pd.read_csv(fm / "floor_bootstrap.csv").merge(prs, on=["target", "source"], suffixes=("", "_pairs"))
        fb_ok = bool(np.allclose(fb.P, fb.P_pairs)) and len(fb) == int(prs.eligible.sum()) \
            and bool(fb.boot_share_close.between(0, 1).all())
        boot = rv[rv.variant.str.contains("bootstrap")].iloc[0]
        ok &= rv_ok and fb_ok
        notes.append(f"floor map: no-close counts re-derived from the pairs file {redo} (match {rv_ok}); bootstrap "
                     f"pairs = eligible pairs with the point-estimate P={fb_ok}; bootstrap no-close median "
                     f"{boot.n_no_close:.0f} [{boot.n_no_close_lo:.0f}, {boot.n_no_close_hi:.0f}]")
    check("E14", "Multiple comparisons (BH at fdr_q), endpoint z and floor-map rule variants re-derived (DL-32)",
          "PASS" if ok else "FLAG", "; ".join(notes))
    # E17 -----------------------------------------------------------------------------------------
    if not (fm / "position_summary.csv").exists():
        check("E17", "Cross-part link columns (DL-33)", "NOTE", "layer not run")
    else:
        pos = pd.read_csv(fm / "position_summary.csv").set_index("soc6")
        prs = pd.read_csv(fm / "succession_pairs.csv")
        cl = prs[prs.eligible & (prs.P <= 25)]
        n_src = cl.groupby("source").size().reindex(pos.index, fill_value=0)
        maint = {"49-9041", "49-9071", "47-2111", "49-9043", "49-9044"}
        n_m = cl[cl.target.isin(maint)].groupby("source").size().reindex(pos.index, fill_value=0)
        src_ok = bool((n_src == pos.n_positions_as_close_source).all() and (n_m == pos.n_maintenance_targets_as_close_source).all())
        identity = int(pos.n_positions_as_close_source.sum()) == int(pos.n_close_sources.sum())
        shares = {}
        for t_, g in cl.groupby("target"):
            shares[t_] = 100 * g[g.source.str[:2] == "51"].source_jobs.sum() / g.source_jobs.sum()
        sh_ok = bool(np.allclose(pd.Series(shares).reindex(pos.index), pos.close_source_jobs_soc51_pct, equal_nan=True))
        lo_ok = bool((pos.boot_n_positions_as_close_source_lo <= pos.boot_n_positions_as_close_source_hi).all())
        cnc = pos.loc["51-9161"]
        ok = src_ok and identity and sh_ok and lo_ok
        check("E17", "Cross-part link columns re-derived from the pair file (DL-33)", "PASS" if ok else "FLAG",
              f"close-source counts and maintenance counts match={src_ok}; Σ as-source = Σ close sources={identity}; "
              f"SOC-51 share of each close pool matches={sh_ok}; CNC tool operators close source for "
              f"{int(cnc.n_positions_as_close_source)} positions (bootstrap {cnc.boot_n_positions_as_close_source_lo:.0f}–"
              f"{cnc.boot_n_positions_as_close_source_hi:.0f}), {int(cnc.n_maintenance_targets_as_close_source)} of 5 "
              f"maintenance targets; production share of the 49-9041 close pool "
              f"{pos.at['49-9041', 'close_source_jobs_soc51_pct']:.0f}%")

    # E11 -----------------------------------------------------------------------------------------
    jz_out = prc / "bls_adjustment_by_job_zone.csv"
    if not jz_out.exists():
        check("E11", "BLS adjustment by Job Zone (DL-34)", "NOTE", "layer not run")
    else:
        import csv
        from scipy.stats import spearmanr
        raw_ep = repo_path(cfg["paths"]["raw_ep"], root)
        with open(raw_ep / "National_Employment_Matrix_IND_336300.csv", newline="", encoding="utf-8") as fh:
            nem_rows = [r for r in csv.DictReader(fh) if "line item" in r["Occupation Type"].lower()]
        chg = {re.sub(r'[="]', "", r["Occupation Code"]).strip(): float(r["Employment Percent Change, 2025-2035"]) for r in nem_rows}
        empk = {re.sub(r'[="]', "", r["Occupation Code"]).strip(): float(r["2025 Employment"]) for r in nem_rows}
        vals = list(chg.values()); base = max(set(vals), key=vals.count)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            xw = pd.read_excel(raw_ep / "nem-onet-to-soc-crosswalk.xlsx", sheet_name="Crosswalk", header=4, dtype=str)
        zones: dict[str, int] = {}
        with open(repo_path(cfg["paths"]["raw_onet"], root) / "job_zones.csv", newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                zones[r["O*NET-SOC Code"]] = int(r["Job Zone"].split("-")[-1])
        jz_of: dict[str, int] = {}
        for oc, nc in zip(xw["O*NET-SOC code"].astype(str).str.strip(), xw["NEM Code"].astype(str).str.strip()):
            if oc in zones and nc in chg:
                jz_of[nc] = max(jz_of.get(nc, 0), zones[oc])
        adj = {c: 100 * ((1 + v / 100) / (1 + base / 100) - 1) for c, v in chg.items()}
        codes = [c for c in chg if c in jz_of]
        rho = spearmanr([jz_of[c] for c in codes], [adj[c] for c in codes]).statistic
        saved = pd.read_csv(jz_out).set_index("job_zone")
        means = {z: np.mean([adj[c] for c in codes if jz_of[c] == z]) for z in sorted(set(jz_of[c] for c in codes))}
        counts = {z: sum(jz_of[c] == z for c in codes) for z in means}
        emps = {z: sum(empk[c] for c in codes if jz_of[c] == z) for z in means}
        ok = (len(codes) == int(saved.n_with_job_zone.iloc[0]) and len(chg) == int(saved.n_line_items.iloc[0])
              and abs(rho - float(saved.spearman_rho.iloc[0])) < 1e-9
              and all(abs(means[z] - saved.at[z, "mean_adjustment_pct"]) < 1e-9 and counts[z] == saved.at[z, "n"]
                      and abs(emps[z] - saved.at[z, "emp_2025_k"]) < 1e-6 for z in means))
        check("E11", "BLS adjustment by Job Zone re-derived from the raw NEM CSV, crosswalk workbook and Job Zones (DL-34)",
              "PASS" if ok else "FLAG",
              f"{len(codes)} of {len(chg)} line items with a Job Zone; baseline {base:+.1f}%; Spearman rho {rho:.3f}; "
              + "; ".join(f"zone {z}: n {counts[z]}, mean {means[z]:+.2f}%" for z in means))

    # E10 -----------------------------------------------------------------------------------------
    occ_p = prc / "bls_adjustment_by_occupation_job_zone.csv"
    if not occ_p.exists():
        check("E10", "Adjusted line items citing automation (DL-39)", "NOTE", "layer not run")
    else:
        import csv
        import openpyxl
        raw_ep = repo_path(cfg["paths"]["raw_ep"], root)
        with open(raw_ep / "National_Employment_Matrix_IND_336300.csv", newline="", encoding="utf-8") as fh:
            rows = [r for r in csv.DictReader(fh) if "line item" in r["Occupation Type"].lower()]
        chg = {re.sub(r'[="]', "", r["Occupation Code"]).strip(): float(r["Employment Percent Change, 2025-2035"]) for r in rows}
        empk = {re.sub(r'[="]', "", r["Occupation Code"]).strip(): float(r["2025 Employment"]) for r in rows}
        vals = list(chg.values()); base = max(set(vals), key=vals.count)
        adj = {c: 100 * ((1 + v / 100) / (1 + base / 100) - 1) for c, v in chg.items()}
        adjusted = [c for c in adj if abs(adj[c]) > 0.05]
        wb = openpyxl.load_workbook(raw_ep / cfg["data_versions"]["ep"]["occupation_file"]["file"], read_only=True)
        pat = re.compile(r"robot|automat", re.I)
        cites = set()
        for r in wb["Table 1.12"].iter_rows(min_row=3, values_only=True):
            if r[1] and r[3] and str(r[3]).strip() in ("336300", "TE1000") and r[4] and pat.search(str(r[4])):
                cites.add(str(r[1]).strip())
        n_cite = sum(c in cites for c in adjusted)
        jobs_adj = sum(empk[c] for c in adjusted); jobs_cite = sum(empk[c] for c in adjusted if c in cites)
        saved = pd.read_csv(occ_p)
        s_adj = saved[saved.direction != "none"]
        ok = (len(adjusted) == len(s_adj) and set(adjusted) == set(s_adj.code)
              and n_cite == int(s_adj.cites_automation.sum())
              and abs(jobs_cite - float(s_adj.loc[s_adj.cites_automation, "emp_2025_k"].sum())) < 1e-6)
        summ_txt = (prc / "mix_summary.md").read_text(encoding="utf-8")
        ok = ok and f"{n_cite} of them" in summ_txt and f"{len(adjusted)} are adjusted" in summ_txt
        check("E10", "Adjusted NEM 336300 line items citing automation re-derived from raw Table 1.12 (openpyxl) and the raw NEM CSV (DL-39)",
              "PASS" if ok else "FLAG",
              f"{len(adjusted)} of {len(chg)} line items adjusted; {n_cite} cite robots or automation for 336300 or all industries; "
              f"jobs {jobs_cite:.1f}k of {jobs_adj:.1f}k ({100 * jobs_cite / jobs_adj:.1f}%)")

    # E6 -----------------------------------------------------------------------------------------
    tr_p = repo_path("outputs/track_record/industry_vintages.csv", root)
    if not tr_p.exists():
        check("E6", "Projection track record (DL-38)", "NOTE", "layer not run")
    else:
        import io
        import zipfile
        import openpyxl
        from scipy.stats import spearmanr
        arch = repo_path("data/raw/ep_archive", root)
        tot: dict[str, tuple[float, float]] = {}
        for v in ("2008-18", "2010-20", "2012-22", "2014-24"):
            with zipfile.ZipFile(arch / f"{v}.zip") as zf:
                mem = next(n for n in zf.namelist() if n.lower().endswith(("matrix.txt", "matrix.csv", "matrix.xlsx")))
                raw = zf.read(mem)
            if mem.endswith(".xlsx"):
                ws = openpyxl.load_workbook(io.BytesIO(raw), read_only=True).worksheets[0]
                for r in ws.iter_rows(min_row=2, values_only=True):
                    if r[2] == "00-0000" and str(r[4]) == "336300":
                        tot[v] = (float(r[6]), float(r[9])); break
            else:
                for line in raw.decode("latin-1").splitlines():
                    f = [x.strip().strip('"').strip("=").strip('"') for x in re.split(r"[;\t,]", line)]
                    if len(f) > 7 and f[2] == "00-0000" and f[3] == "336300":
                        sc = 1000.0 if v == "2008-18" else 1.0
                        tot[v] = (float(f[4]) / sc, float(f[7]) / sc); break
        wb = openpyxl.load_workbook(sorted(repo_path("data/raw/ces_2008", root).glob("*.xlsx"))[-1])   # not read-only: the BLS export has no sheet dimension record
        ann = {}
        for r in wb.worksheets[0].iter_rows(values_only=True):
            if isinstance(r[0], (int, float)) and 2000 < r[0] < 2100 and all(isinstance(x, (int, float)) for x in r[1:13]):
                ann[int(r[0])] = sum(r[1:13]) / 12
        saved = pd.read_csv(tr_p).set_index("vintage")
        ok = True; parts = []
        for v, (b, p) in {"2008-18": (2008, 2018), "2010-20": (2010, 2020), "2012-22": (2012, 2022), "2014-24": (2014, 2024)}.items():
            err = 100 * (tot[v][1] / ann[p] - 1)
            dirc = (tot[v][1] - tot[v][0]) * (ann[p] - ann[b]) > 0
            ok = ok and abs(err - saved.at[v, "error_pct"]) < 1e-9 and bool(dirc) == bool(saved.at[v, "direction_correct"])
            parts.append(f"{v} {err:+.1f}% {'right' if dirc else 'wrong'}")
        occ = pd.read_csv(repo_path("outputs/track_record/occupation_2014_24.csv", root))
        c = occ[occ.reason == "compared"]
        rho = spearmanr(c.base_k.rdiv(c.proj_k) - 1, c.oews_2014.rdiv(c.oews_2024) - 1).statistic
        dir_share = float(np.mean(np.sign(c.proj_k - c.base_k) == np.sign(c.oews_2024 - c.oews_2014)))
        summ_txt = repo_path("outputs/track_record/track_record_summary.md", root).read_text(encoding="utf-8")
        ok = ok and f"Spearman rho {rho:.3f}" in summ_txt and f"({100 * dir_share:.1f}%)" in summ_txt
        check("E6", "Projection track record: archive totals (raw text / openpyxl) and CES annual averages (openpyxl) re-derived; "
              "occupation metrics recomputed from the comparison file (DL-38)", "PASS" if ok else "FLAG",
              "; ".join(parts) + f"; occupations compared {len(c)}, direction right {100 * dir_share:.1f}%, Spearman {rho:.3f}")

    # E15 -----------------------------------------------------------------------------------------
    if not repo_path("outputs/cps_flows/a2_production_destinations.csv", root).exists():
        check("E15", "CPS age profile and flows (DL-44)", "NOTE", "layer not run")
    else:
        _cps_stream_check(root)

    df = pd.DataFrame(ROWS)
    df = df.iloc[df.id.str[1:].astype(int).argsort(kind="stable")].reset_index(drop=True)
    out = repo_path("outputs/review", root)
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "output_audit.csv", index=False)
    md = ["# Output audit (E-checks)\n", df.to_markdown(index=False), "",
          f"PASS {int((df.status == 'PASS').sum())} · NOTE {int((df.status == 'NOTE').sum())} · FLAG {int((df.status == 'FLAG').sum())}"]
    (out / "output_audit.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return df


def _cps_stream_check(root: Path) -> None:
    """E15: one streaming pass over the raw CPS files with string slicing and dict-based linking."""
    import zipfile
    from .cps_codes import census_codes, M_CODES
    p_codes, mfg, soc_of = census_codes(root)
    files = sorted(repo_path("data/raw/cps/basic", root).glob("*pub.zip"),
                   key=lambda f: (int(f.name[3:5]), "jan feb mar apr may jun jul aug sep oct nov dec".split().index(f.name[:3])))
    mon = "jan feb mar apr may jun jul aug sep oct nov dec".split()
    A = set(range(30, 44))
    M = set(M_CODES)
    # employed-records linker (PEMLR 1-2, any age): production pairs in manufacturing at t-1 and moves into M at t
    den = num_any = 0
    young = [0, 0]                                      # of which a person under 16 in either month
    # civilian adults 16+ (PEMLR 1-7)
    a2 = {}; a2_den = {"all_pairs": 0, "headline_no_allocation": 0}
    a3 = {}; a3_den = {}
    a1 = {"M": [0, 0, 0.0, 0.0], "P": [0, 0, 0.0, 0.0]}
    emp_prev: dict | None = None; adl_prev: dict | None = None; m_prev = None
    for f in files:
        mi = (2000 + int(f.name[3:5])) * 12 + mon.index(f.name[:3])
        emp: dict[tuple, tuple] = {}; adl: dict[tuple, tuple] = {}
        with zipfile.ZipFile(f) as zf, zf.open(zf.namelist()[0]) as fh:
            for raw in fh:
                s_ = raw.decode("latin-1")
                emlr = s_[179:181].strip()
                key = (s_[0:15], s_[70:75], s_[146:148])
                age = int(s_[121:123])
                if emlr in ("1", "2"):
                    emp[key] = (int(s_[62:64]), s_[128:130], age, int(s_[859:863]), int(s_[855:859]), s_[425:427].strip(),
                                int(s_[768:770]), int(s_[766:768]))
                if s_[160:162].strip() == "2" and age >= 16 and emlr in tuple("1234567"):
                    e = emlr in ("1", "2")
                    w = float(s_[845:855].strip() or 0) / 1e4
                    adl[key] = (int(s_[62:64]), s_[128:130], age, int(emlr), int(s_[859:863]) if e else -1,
                                int(s_[855:859]) if e else -1, int(s_[768:770]) if e else 0, int(s_[766:768]) if e else 0,
                                int(s_[684:686]), w)
                    if e and int(s_[855:859]) in mfg:
                        occ = int(s_[859:863])
                        for g, inside in (("M", occ in M), ("P", occ in p_codes)):
                            if inside:
                                a1[g][0] += 1; a1[g][2] += w
                                if age >= 55:
                                    a1[g][1] += 1; a1[g][3] += w
        if emp_prev is not None and m_prev == mi - 1:
            for key, (mis, sex, age, occ, ind, iodp1, xo, xi) in emp.items():
                pv = emp_prev.get(key)
                if pv is None or mis in (1, 5) or mis != pv[0] + 1 or sex != pv[1] or age - pv[2] not in (0, 1):
                    continue
                if pv[3] in p_codes and pv[4] in mfg:
                    den += 1; num_any += occ in M
                    if min(age, pv[2]) < 16:
                        young[0] += 1; young[1] += occ in M
            for key, (mis, sex, age, emlr, occ, ind, xo, xi, xm, w) in adl.items():
                pv = adl_prev.get(key)
                if pv is None or mis in (1, 5) or mis != pv[0] + 1 or sex != pv[1] or age - pv[2] not in (0, 1):
                    continue
                emlr_p, occ_p, ind_p = pv[3], pv[4], pv[5]
                emp_t, emp_p = emlr in (1, 2), emlr_p in (1, 2)
                alloc = (emp_p and (pv[6] in A or pv[7] in A)) or (emp_t and (xo in A or xi in A)) or pv[8] in A or xm in A
                checks_ = ["all_pairs"] + ([] if alloc else ["headline_no_allocation"])
                if emp_p and occ_p in p_codes and ind_p in mfg:
                    if emp_t and ind in mfg:
                        d = ("mfg_same_occupation" if occ == occ_p else "mfg_other_production" if occ in p_codes
                             else "mfg_maintenance" if occ in M else "mfg_other_occupation")
                    elif emp_t:
                        d = "outside_mfg_maintenance" if occ in M else "outside_mfg_other"
                    else:
                        d = {3: "unemployed", 4: "unemployed", 5: "retired", 6: "disabled", 7: "other_nilf"}[emlr]
                    for ck in checks_:
                        a2_den[ck] += 1; a2[(ck, d)] = a2.get((ck, d), 0) + 1
                if emp_p and occ_p in M and ind_p in mfg:
                    for ck in checks_:
                        a3_den[(ck, "outflow")] = a3_den.get((ck, "outflow"), 0) + 1
                    if not (emp_t and occ in M):
                        d = ("production" if emp_t and occ in p_codes else "other_employed" if emp_t else
                             {3: "unemployed", 4: "unemployed", 5: "retired", 6: "disabled", 7: "other_nilf"}[emlr])
                        for ck in checks_:
                            a3[(ck, "outflow", d)] = a3.get((ck, "outflow", d), 0) + 1
                if emp_t and occ in M and ind in mfg:
                    for ck in checks_:
                        a3_den[(ck, "inflow")] = a3_den.get((ck, "inflow"), 0) + 1
                    if not (emp_p and occ_p in M):
                        o = ("production" if emp_p and occ_p in p_codes else "other_employed" if emp_p else
                             "unemployed" if emlr_p in (3, 4) else "not_in_labour_force")
                        for ck in checks_:
                            a3[(ck, "inflow", o)] = a3.get((ck, "inflow", o), 0) + 1
        emp_prev, adl_prev, m_prev = emp, adl, mi

    fl = repo_path("outputs/cps_flows", root)
    parts, ok = [], True
    t1 = pd.read_csv(fl / "a1_age_profile.csv")
    for g, lab in (("M", "maintenance_M"), ("P", "production_P")):
        r = t1[(t1.check == "all_records") & (t1.group == lab) & (t1.band == "55+")].iloc[0]
        ok &= (int(r.n_den), int(r.n_num)) == (a1[g][0], a1[g][1]) and abs(float(r.pct) - 100 * a1[g][3] / a1[g][2]) < 1e-6
    parts.append(f"A1 55+: maintenance {a1['M'][1]}/{a1['M'][0]} ({100 * a1['M'][3] / a1['M'][2]:.2f}%), production "
                 f"{a1['P'][1]}/{a1['P'][0]}")
    t2 = pd.read_csv(fl / "a2_production_destinations.csv")
    for ck in ("all_pairs", "headline_no_allocation"):
        sub = t2[(t2.check == ck) & (t2.age_band == "all")].set_index("category")
        ok &= int(sub.n_den.iloc[0]) == a2_den[ck]
        ok &= all(int(sub.at[d, "n_num"]) == a2.get((ck, d), 0) for d in sub.index)
        ok &= abs(sub.pct.sum() - 100) < 1e-9
    # internal consistency: A2 pairs employed at t equal the employed-linker pairs without persons under 16
    emp_den = sum(a2.get(("all_pairs", d), 0) for d in ("mfg_same_occupation", "mfg_other_production", "mfg_maintenance",
                                                        "mfg_other_occupation", "outside_mfg_maintenance", "outside_mfg_other"))
    emp_ev = a2.get(("all_pairs", "mfg_maintenance"), 0) + a2.get(("all_pairs", "outside_mfg_maintenance"), 0)
    cons = (emp_den, emp_ev) == (den - young[0], num_any - young[1])
    ok &= cons
    parts.append(f"A2 counts re-derived; employed-at-t pairs {emp_den:,} / moves {emp_ev} = employed-records linker "
                 f"{den:,} / {num_any} minus {young[0]} / {young[1]} pairs with a person under 16: {cons}")
    t3 = pd.read_csv(fl / "a3_maintenance_flows.csv")
    for ck in ("all_pairs", "headline_no_allocation"):
        for dr in ("outflow", "inflow"):
            sub = t3[(t3.check == ck) & (t3.direction == dr) & (t3.age_band == "all")]
            ok &= int(sub.n_den.iloc[0]) == a3_den.get((ck, dr), 0)
            ok &= all(int(r.n_num) == a3.get((ck, dr, r.category), 0) for r in sub.itertuples())
    bal = pd.read_csv(fl / "a3_balance.csv")
    b = bal[(bal.check == "headline_no_allocation") & bal.ratio.str.startswith("inflow from production")].iloc[0]
    ok &= (int(b.events_numerator), int(b.events_denominator)) == (a3.get(("headline_no_allocation", "inflow", "production"), 0),
                                                                    a3.get(("headline_no_allocation", "outflow", "retired"), 0))
    parts.append(f"A3 counts re-derived (headline: in from production {int(b.events_numerator)}, out to retirement "
                 f"{int(b.events_denominator)})")
    check("E15", "CPS age profile and flows (DL-44): A1 counts and weighted 55+ shares, A2 and A3 counts re-derived from the "
          "raw files with string slicing and dict-based linkers; A2 agrees with the employed-records linker",
          "PASS" if ok else "FLAG",
          "; ".join(parts))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=None)
    args = ap.parse_args(argv)
    df = run(load_config(args.config))
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 200)
    print(df.to_string(index=False))
    return int((df.status == "FLAG").sum() > 0)


if __name__ == "__main__":
    raise SystemExit(main())
