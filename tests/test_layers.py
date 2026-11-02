"""Unit tests for the II-A layers (synthetic data unless outputs exist; no download needed)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def test_read_nem_parses_bls_export(tmp_path):
    from src.mix import read_nem
    csv = tmp_path / "nem.csv"
    csv.write_text(
        '"Occupation Title","Occupation Code","Occupation Type","2025 Employment","2025 Percent of Industry",'
        '"2025 Percent of Occupation","Projected 2035 Employment","Projected 2035 Percent of Industry",'
        '"Projected 2035 Percent of Occupation","Employment Change, 2025-2035","Employment Percent Change, 2025-2035",'
        '"Occupation Sort","Display Level"\n'
        '"Total, all occupations","=""00-0000""","Summary","524.7","100.0","0.3","451.5","100.0","0.3","-73.2","-13.9","","0"\n'
        '"Industrial machinery mechanics","=""49-9041""","Line Item","12.9","2.5","2.9","13.4","3.0","2.6","0.6","4.5","885","4"\n',
        encoding="utf-8")
    t = read_nem(csv).set_index("code")
    assert list(t.index) == ["00-0000", "49-9041"]
    assert t.loc["49-9041", "change_pct"] == 4.5 and t.loc["00-0000", "emp_2035_k"] == 451.5


def test_read_ces_fred_csv_and_bls_xlsx(tmp_path):
    from src.trend import read_monthly
    fred = tmp_path / "CEU3133630001.csv"
    fred.write_text("observation_date,CEU3133630001\n2024-01-01,540.1\n2024-02-01,541.3\n", encoding="utf-8")
    m = read_monthly(fred)
    assert list(m.emp_k) == [540.1, 541.3] and str(m.date.iloc[0].date()) == "2024-01-01"
    rows = [["Series Id:", "CEU3133630001"], [], ["Year"] + ["Jan", "Feb", "Mar"], [2024, 540.1, 541.3, 542.0]]
    x = pd.DataFrame(rows)
    path = tmp_path / "SeriesReport.xlsx"
    x.to_excel(path, header=False, index=False)
    m2 = read_monthly(path)
    assert list(m2.emp_k) == [540.1, 541.3, 542.0]


def test_nem_baseline_is_mode_and_adjustment_formula():
    from src.mix import bls_adjustment_pct, nem_baseline
    t = pd.DataFrame({"type": ["Summary", "Line item", "Line item", "Line item", "Line item"],
                      "change_pct": [-13.9, -12.9, -12.9, 4.5, -21.6], "emp_2025_k": [10.0, 3.0, 2.0, 1.0, 4.0]})
    b = nem_baseline(t)
    assert b["baseline_change_pct"] == -12.9 and b["n_at_baseline"] == 2 and b["n_line_items"] == 4
    assert b["emp_2025_k_at_baseline"] == 5.0
    adj = bls_adjustment_pct([4.5, -12.9, -21.6], -12.9)
    assert np.allclose(adj, [100 * (1.045 / 0.871 - 1), 0.0, 100 * (0.784 / 0.871 - 1)])


def test_history_read_year_parses_zip_member(tmp_path):
    import zipfile
    from src.history import read_year
    cols = ["AREA", "NAICS", "NAICS_TITLE", "OCC_CODE", "OCC_TITLE", "O_GROUP", "TOT_EMP", "EMP_PRSE", "PCT_TOTAL",
            "H_MEAN", "MEAN_PRSE", "H_MEDIAN", "A_MEDIAN"]
    rows = [["99", "336300", "Parts", "00-0000", "All", "total", "1,000", "0.0", "100", "20", "0.1", "19", "40000"],
            ["99", "336300", "Parts", "49-9041", "IMM", "detailed", "50", "2.0", "5", "30", "0.4", "29", "60000"],
            ["99", "336300", "Parts", "51-2090", "Misc", "broad", "300", "1.0", "30", "18", "0.2", "17", "**"],
            ["99", "336300", "Parts", "51-2090", "Misc", "detailed", "300", "1.0", "30", "18", "0.2", "17", "**"],
            ["99", "336100", "Vehicles", "49-9041", "IMM", "detailed", "70", "2.0", "5", "31", "0.4", "30", "61000"]]
    x = tmp_path / "nat4d_M2021_dl.xlsx"
    pd.DataFrame(rows, columns=[c.lower() for c in cols]).to_excel(x, index=False)    # 2021 files use lower case
    z = tmp_path / "oesm21in4.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.write(x, "oesm21in4/nat4d_M2021_dl.xlsx")
    d = read_year(z, 2021).set_index("OCC_CODE")
    assert list(d.index) == ["00-0000", "49-9041", "51-2090"]           # other industry dropped, duplicate resolved
    assert d.loc["00-0000", "TOT_EMP"] == 1000 and np.isnan(d.loc["51-2090", "A_MEDIAN"])


def test_history_premium_z_on_log_ratio():
    from src.history import change_rows
    rows = []
    for y, (imm, mmw) in {2021: (30.0, 26.0), 2025: (33.0, 31.0)}.items():
        rows += [{"year": y, "soc6": "49-9041", "role": "maintenance target", "emp": 100.0, "emp_rse": 5.0,
                  "a_median": 60000.0, "h_mean": imm, "mean_prse": 1.0, "premium_mean_49_9041_over_pct": np.nan},
                 {"year": y, "soc6": "49-9043", "role": "maintenance target", "emp": 50.0, "emp_rse": 10.0,
                  "a_median": 50000.0, "h_mean": mmw, "mean_prse": 2.0,
                  "premium_mean_49_9041_over_pct": 100 * (imm / mmw - 1)}]
    mix = pd.DataFrame(rows).assign(title="")
    c = change_rows(mix, 2021, 2025).set_index("soc6")
    want = (np.log(33 / 31) - np.log(30 / 26)) / (np.sqrt(1 + 4 + 1 + 4) / 100)
    assert np.isclose(c.at["49-9043", "premium_mean_change_z"], want)
    assert np.isnan(c.at["49-9041", "premium_mean_change_z"])


def test_skill_shift_task_patterns():
    import re
    from src.skill_shift import TASK_PATTERNS
    hit = lambda k, s: bool(re.search(TASK_PATTERNS[k], s.lower()))
    assert hit("tasks_programming_plc_software_computer", "Program the PLC for a new line")
    assert hit("tasks_robot_automation", "Maintain robotic welding cells")
    assert hit("tasks_diagnose_troubleshoot_test", "Test hydraulic circuits") and not hit("tasks_diagnose_troubleshoot_test", "Read the latest manuals")


def test_floor_map_successor_rule():
    from src.floor_map import eligible
    assert eligible(45000, 64000, 2, 3)            # promotion: paid less, lower Job Zone
    assert eligible(45000, 64000, 3, 3)            # lateral in preparation, still paid less
    assert not eligible(70000, 64000, 3, 3)        # earns more: not a succession move
    assert not eligible(45000, 64000, 4, 3)        # needs more preparation than the target
    assert not eligible(float("nan"), 64000, 2, 3)  # wage withheld


def test_floor_map_eligibility_matrix_agrees_with_pair_rule():
    from src.floor_map import bench_counts, eligibility_matrix, eligible
    wage = np.array([40000.0, 52000.0, 64000.0, np.nan])
    jz = np.array([2, 3, 3, 2])
    E = eligibility_matrix(wage, jz)
    for t in range(4):
        for s in range(4):
            assert E[t, s] == (t != s and eligible(wage[s], wage[t], jz[s], jz[t]))
    assert eligibility_matrix(wage, jz, wage_factor=None)[0, 3]       # Job Zone rule only ignores the withheld wage
    assert eligibility_matrix(wage, jz, wage_factor=1.10)[1, 1] == False
    n, ratio = bench_counts(E, np.array([100.0, 50.0, 10.0, 5.0]))
    assert list(n) == [0, 1, 2, 0] and np.isclose(ratio[2], 15.0)


def test_bh_adjust_matches_hand_computation():
    from src.stats import bh_adjust
    adj = bh_adjust([0.01, 0.04, 0.03, 0.2])
    # sorted 0.01, 0.03, 0.04, 0.2 -> 0.04, 0.06, 0.0533, 0.2 -> running minimum from the top
    assert np.allclose(adj, [0.04, 0.04 * 4 / 3, 0.04 * 4 / 3, 0.2])
    assert np.allclose(bh_adjust([0.001] * 24), 0.001)            # ties at the bootstrap floor all survive


def test_floor_map_link_columns_are_consistent():
    """Real-data check when outputs exist: as-source counts sum to the close-source counts (DL-33)."""
    import pathlib
    f = pathlib.Path(__file__).resolve().parents[1] / "outputs/floor_map/position_summary.csv"
    if not f.exists():
        import pytest
        pytest.skip("floor map not run")
    pos = pd.read_csv(f)
    if "n_positions_as_close_source" not in pos.columns:
        import pytest
        pytest.skip("floor map output predates DL-33")
    assert pos.n_positions_as_close_source.sum() == pos.n_close_sources.sum()
    assert (pos.n_maintenance_targets_as_close_source <= pos.n_positions_as_close_source).all()


def test_job_zone_adjustment_outputs_consistent():
    """Real-data check when outputs exist (DL-34): zone counts add up and every zone mean lies inside its range."""
    import pathlib
    import pytest
    root = pathlib.Path(__file__).resolve().parents[1] / "outputs/mix"
    occ_p, sum_p = root / "bls_adjustment_by_occupation_job_zone.csv", root / "bls_adjustment_by_job_zone.csv"
    if not (occ_p.exists() and sum_p.exists()):
        pytest.skip("projection layer not run")
    occ, sm = pd.read_csv(occ_p), pd.read_csv(sum_p).set_index("job_zone")
    assert int(sm.n.sum()) == int(occ.job_zone.notna().sum()) == int(sm.n_with_job_zone.iloc[0])
    for z, g in occ.dropna(subset=["job_zone"]).groupby("job_zone"):
        assert np.isclose(g.bls_adjustment_pct.mean(), sm.at[z, "mean_adjustment_pct"])


def test_truncnorm_draws_respect_bounds_and_zero_se():
    from src.onet_arrays import sample_truncnorm
    rng = np.random.default_rng(5)
    v = np.array([0.2, 3.5, 6.9, 4.0]); se = np.array([0.5, 1.0, 0.4, 0.0])
    for _ in range(50):
        d = sample_truncnorm(v, se, 0.0, 7.0, rng)
        assert ((d >= 0) & (d <= 7)).all() and d[3] == 4.0      # zero SE keeps the published value


def test_impute_missing_se_uses_incumbent_median():
    from src.onet_arrays import impute_missing_se
    se = pd.DataFrame({"e1": [0.1, 0.3, np.nan], "e2": [0.2, np.nan, 0.4]}, index=["a", "b", "c"])
    src_ = pd.Series({"a": "Incumbent", "b": "Incumbent", "c": "Analyst"})
    out, n = impute_missing_se(se, src_)
    assert n == 2 and out.at["c", "e1"] == pytest.approx(0.2) and out.at["b", "e2"] == pytest.approx(0.2)
