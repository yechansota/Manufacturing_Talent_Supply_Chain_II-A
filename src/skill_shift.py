"""Skill content inside the maintenance family (analysis log DL-30; exploratory).

Question: what separates the maintenance occupation BLS expects automation to grow (49-9041 industrial machinery
mechanics) from the maintenance occupations that shrink?

  levels    49-9041 minus each other target on every Skills and Knowledge element (O*NET Level scale), with
            SE = sqrt(SE_1^2 + SE_2^2) from the published rating SEs (no imputation: an element without an SE on
            either side gets no z). Elements are correlated and occupations were rated in different years, so the
            counts of |z| > 1.96 describe a pattern, not independent tests. Two-sided p-values are also corrected
            within each comparison with Benjamini-Hochberg at decision_rules.fdr_q and with Bonferroni (DL-32).
  software  O*NET 31.0 Software Skills: examples, categories, Hot Technology / In Demand flags, and the examples in
            the category 'Industrial control software' (PLC, SCADA, ...).
  tasks     O*NET 31.0 Task Statements: number of tasks, core tasks, and tasks matching fixed keyword patterns.

Inputs:  DuckDB onet_ratings (O*NET ingest); data/raw/onet/software_skills.csv, task_statements.csv (optional)
Outputs: outputs/skill_shift/level_differences.csv, software_and_tasks.csv
Usage:   python -m src.skill_shift
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pandas as pd
from scipy.stats import norm

from .config import REPO_ROOT, load_config, repo_path
from .stats import bh_adjust

ANCHOR = "49-9041.00"
COMPARE = ["49-9043.00", "49-9071.00", "49-9044.00", "47-2111.00"]
PROFILE_SET = {
    "49-9041.00": "maintenance target", "49-9043.00": "maintenance target", "49-9071.00": "maintenance target",
    "49-9044.00": "maintenance target", "47-2111.00": "maintenance target",
    "51-9161.00": "close feeder (Skills H1)", "51-4081.00": "close feeder (Skills H1)", "51-4041.00": "close feeder (Skills H1)",
    "51-9162.00": "context", "17-3024.00": "context", "17-3024.01": "context (O*NET detail of 17-3024)",
}
TASK_PATTERNS = {
    "tasks_programming_plc_software_computer": r"program|\bplc\b|software|computer",
    "tasks_electrical_electronic": r"electric|electron",
    "tasks_robot_automation": r"robot|automat",
    "tasks_diagnose_troubleshoot_test": r"diagnos|troubleshoot|malfunction|\btest",
}
CONTROL_CATEGORY = "Industrial control software"


def level_differences(cfg: dict[str, Any], root: Path) -> pd.DataFrame:
    lv = cfg["measurement"]["scales"]["level"]["id"]
    codes = [ANCHOR] + COMPARE
    with duckdb.connect(str(repo_path(cfg["paths"]["duckdb"], root)), read_only=True) as con:
        r = con.execute("SELECT onet_code, title, domain, element_id, element_name, data_value, se, date_year "
                        "FROM onet_ratings WHERE scale_id = ? AND domain IN ('S', 'K')", [lv]).df()
    r = r[r.onet_code.isin(codes)]
    a = r[r.onet_code == ANCHOR].set_index(["domain", "element_id"])
    rows = []
    for c in COMPARE:
        b = r[r.onet_code == c].set_index(["domain", "element_id"])
        j = a.join(b, lsuffix="_a", rsuffix="_b", how="inner")
        se = np.sqrt(j.se_a ** 2 + j.se_b ** 2)
        d = j.data_value_a - j.data_value_b
        z = np.where(se > 0, d / se, np.nan)
        for (dom, eid), row, dd, ss, zz in zip(j.index, j.itertuples(), d, se, z):
            rows.append({"anchor": ANCHOR, "other": c, "other_title": row.title_b, "domain": dom, "element_id": eid,
                         "element_name": row.element_name_a, "level_anchor": row.data_value_a, "level_other": row.data_value_b,
                         "diff": dd, "se_diff": ss, "z": zz, "year_anchor": row.date_year_a, "year_other": row.date_year_b})
    out = pd.DataFrame(rows)
    q = float(cfg["decision_rules"]["fdr_q"])
    out["p_two_sided"] = 2 * norm.sf(np.abs(out.z))
    out["bh_adj_p"] = np.nan
    for c, g in out[out.z.notna()].groupby("other"):
        out.loc[g.index, "bh_adj_p"] = bh_adjust(g.p_two_sided.to_numpy())
        out.loc[g.index, "n_tests"] = len(g)
    out["bh_reject"] = out.bh_adj_p <= q
    out["bonferroni_reject"] = out.p_two_sided <= q / out.n_tests
    return out


def software_and_tasks(cfg: dict[str, Any], root: Path) -> pd.DataFrame | None:
    raw = repo_path(cfg["paths"]["raw_onet"], root)
    sw_p, tk_p = raw / "software_skills.csv", raw / "task_statements.csv"
    if not (sw_p.exists() and tk_p.exists()):
        print("[skip] software_skills.csv / task_statements.csv not found (optional inputs, DL-30)")
        return None
    sw = pd.read_csv(sw_p, dtype=str, keep_default_na=False)
    tk = pd.read_csv(tk_p, dtype=str, keep_default_na=False)
    rows = []
    for c, role in PROFILE_SET.items():
        g, t = sw[sw["O*NET-SOC Code"] == c], tk[tk["O*NET-SOC Code"] == c]
        text = t["Task"].str.lower()
        ctl = g[g["Element Name"] == CONTROL_CATEGORY]
        r = {"onet_code": c, "title": (g.Title.iloc[0] if len(g) else (t.Title.iloc[0] if len(t) else "")), "role": role,
             "software_examples": len(g), "software_categories": g["Element Name"].nunique(),
             "hot_technology": int((g["Hot Technology"] == "Y").sum()), "in_demand": int((g["In Demand"] == "Y").sum()),
             "industrial_control_examples": len(ctl), "industrial_control_list": "; ".join(ctl["Workplace Example"]),
             "tasks": len(t), "core_tasks": int((t["Task Type"] == "Core").sum()),
             "task_rating_date": ";".join(sorted(set(t["Date"]) - {""}))}
        for k, pat in TASK_PATTERNS.items():
            r[k] = int(text.str.contains(pat, regex=True).sum())
        rows.append(r)
    return pd.DataFrame(rows)


def run(cfg: dict[str, Any], root: Path = REPO_ROOT) -> dict[str, pd.DataFrame]:
    out = repo_path("outputs/skill_shift", root)
    out.mkdir(parents=True, exist_ok=True)
    lev = level_differences(cfg, root)
    lev.to_csv(out / "level_differences.csv", index=False)
    st = software_and_tasks(cfg, root)
    if st is not None:
        st.to_csv(out / "software_and_tasks.csv", index=False)
    return {"levels": lev, "software_tasks": st}


def summarize_levels(lev: pd.DataFrame) -> pd.DataFrame:
    g = lev.groupby(["other", "other_title"])
    cnt = lambda col, sign: g.apply(lambda d: int((d[col] & (np.sign(d.z) == sign)).sum()), include_groups=False)
    return pd.DataFrame({"elements": g.size(), "with_se": g.z.count(),
                         "anchor_higher_z_gt_1.96": g.z.apply(lambda s: int((s > 1.96).sum())),
                         "anchor_lower_z_lt_-1.96": g.z.apply(lambda s: int((s < -1.96).sum())),
                         "anchor_higher_bh": cnt("bh_reject", 1), "anchor_lower_bh": cnt("bh_reject", -1),
                         "anchor_higher_bonferroni": cnt("bonferroni_reject", 1),
                         "anchor_lower_bonferroni": cnt("bonferroni_reject", -1)}).reset_index()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=None)
    args = ap.parse_args(argv)
    res = run(load_config(args.config))
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 80)
    print(summarize_levels(res["levels"]).to_string(index=False))
    if res["software_tasks"] is not None:
        print(res["software_tasks"].drop(columns=["industrial_control_list"]).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
