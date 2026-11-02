"""Unit checks for the CPS age profile and flows (DL-44): linking, destinations, parser."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src import cps_flows as cf
from src.config import REPO_ROOT, repo_path

SOC = {8030: "51-4041", 8950: "51-9198", 7340: "49-9071", 7610: "49-9098", 6355: "47-2111", 6260: "47-2061",
       9130: "53-3032", 1545: "17-3026", 5000: "43-1011"}
MFG = {3570, 3580}


def _toy(rows):
    cols = ["hh", "hh2", "line", "m", "mis", "sex", "age", "emlr", "occ", "ind", "xocc", "xind", "xmlr", "w", "iodp1"]
    return pd.DataFrame(rows, columns=cols)


def test_link_adults_rules():
    df = _toy([
        (1, 1, 1, 100, 2, 1, 40, 1, 8030, 3570, 0, 0, 0, 1.0, -1),
        (1, 1, 1, 101, 3, 1, 40, 5, -1, -1, 0, 0, 0, 1.0, -1),      # linked: retired next month
        (2, 1, 1, 100, 4, 1, 40, 1, 8030, 3570, 0, 0, 0, 1.0, -1),
        (2, 1, 1, 101, 5, 1, 40, 1, 8030, 3570, 0, 0, 0, 1.0, -1),  # month in sample 5: not linked
        (3, 1, 1, 100, 2, 1, 40, 1, 8030, 3570, 0, 0, 0, 1.0, -1),
        (3, 1, 1, 101, 3, 2, 40, 1, 8030, 3570, 0, 0, 0, 1.0, -1),  # sex differs: not linked
        (4, 1, 1, 100, 2, 1, 40, 1, 8030, 3570, 0, 0, 0, 1.0, -1),
        (4, 1, 1, 101, 3, 1, 43, 1, 8030, 3570, 0, 0, 0, 1.0, -1),  # age jumps: not linked
    ])
    pr = cf.link_adults(df)
    assert list(pr.hh) == [1]
    assert int(pr.emlr_p.iloc[0]) == 1 and int(pr.emlr.iloc[0]) == 5


def test_a2_destinations():
    p_codes = {8030, 8950}
    base = dict(hh=1, hh2=1, line=1, m=101, mis=3, sex=1, age=40, xocc=0, xind=0, xmlr=0, w=1.0, iodp1=-1,
                mis_p=2, sex_p=1, age_p=40, emlr_p=1, occ_p=8030, ind_p=3570, xocc_p=0, xind_p=0, xmlr_p=0,
                emlr_n=np.nan, occ_n=np.nan, ind_n=np.nan)
    rows = [dict(base, emlr=1, occ=8030, ind=3570), dict(base, emlr=1, occ=8950, ind=3570),
            dict(base, emlr=1, occ=7340, ind=3570), dict(base, emlr=1, occ=5000, ind=3570),
            dict(base, emlr=1, occ=7340, ind=8000), dict(base, emlr=1, occ=5000, ind=8000),
            dict(base, emlr=3, occ=-1, ind=-1), dict(base, emlr=5, occ=-1, ind=-1),
            dict(base, emlr=6, occ=-1, ind=-1), dict(base, emlr=7, occ=-1, ind=-1)]
    pr = pd.DataFrame(rows)
    k = cf.pair_masks(pr, p_codes, MFG)
    assert list(cf.a2_destination(pr, k, p_codes)) == cf.A2_DEST


RAW = repo_path("data/raw/cps/basic", REPO_ROOT)


@pytest.mark.skipif(not (RAW / "jan20pub.zip").exists(), reason="CPS files not downloaded")
def test_fast_parser_matches_string_slicing():
    """Civilian adult records from the fixed-width numpy parser equal plain string slicing of the raw lines."""
    import zipfile
    mi = 2020 * 12
    b = cf.parse_month_adults(RAW / "jan20pub.zip", mi)
    occ, emlr, age, w = [], [], [], []
    with zipfile.ZipFile(RAW / "jan20pub.zip") as zf, zf.open(zf.namelist()[0]) as fh:
        for raw in fh:
            s = raw.decode("latin-1")
            a, e = int(s[121:123]), s[179:181].strip()
            if s[160:162].strip() == "2" and a >= 16 and e in tuple("1234567"):
                emlr.append(int(e)); age.append(a); w.append(float(s[845:855].strip() or 0) / 1e4)
                occ.append(int(s[859:863]) if e in ("1", "2") else -1)
    assert len(emlr) == len(b["emlr"])
    assert np.array_equal(np.array(emlr), b["emlr"]) and np.array_equal(np.array(age), b["age"])
    assert np.allclose(np.array(w), b["w"])
    e_ = np.isin(b["emlr"], [1, 2])
    assert np.array_equal(np.array(occ)[e_], b["occ"][e_])
