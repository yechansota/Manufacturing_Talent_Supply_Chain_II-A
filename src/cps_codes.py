"""CPS basic monthly file readers and occupation / industry code sets shared with II-B (DL-37, DL-40).

Copied verbatim from II-B's observed-moves module (DL-36a: neither repository reads the other's code or outputs).
The flows in src/cps_flows.py use the same record layout, maintenance codes, manufacturing industry codes, pandemic
window, allocation flags, linking keys and NCHS reporting rule.
"""
from __future__ import annotations

import re
import warnings
from pathlib import Path

import pandas as pd

from .config import repo_path

# 1-based inclusive positions; identical in the January 2020 and January 2025 record layouts
FIELDS = {"HRHHID": (1, 15), "HRMONTH": (16, 17), "HRYEAR4": (18, 21), "HRINTSTA": (57, 58), "HRMIS": (63, 64),
          "HRHHID2": (71, 75), "PRTAGE": (122, 123), "PESEX": (129, 130), "PULINENO": (147, 148),
          "PEMLR": (180, 181), "PUIODP1": (426, 427), "PXIO1ICD": (767, 768), "PXIO1OCD": (769, 770),
          "PWCMPWGT": (846, 855), "PEIO1ICD": (856, 859), "PTIO1OCD": (860, 863)}
MONTHS = "jan feb mar apr may jun jul aug sep oct nov dec".split()
M_CODES = {6355: "47-2111", 7330: "49-904X", 7340: "49-9071", 7350: "49-9043", 7360: "49-9044"}
C_CODES = {8030: "51-4041"}
MIXED = {7905: "51-9160", 8225: "51-4XXX"}
MOTOR_VEHICLES = 3570
EXCLUDE_WINDOW = (2020 * 12 + 2, 2021 * 12 + 11)          # March 2020 .. December 2021 (month index = 12*y + m - 1)
ALLOCATED = set(range(30, 44))


# ---------------------------------------------------------------------------------------------------------------
# Inputs
def census_codes(root: Path) -> tuple[set[int], set[int], dict[int, str]]:
    """P codes (SOC 51-), manufacturing industry codes (NAICS 31-33), and the SOC of every occupation code."""
    base = repo_path("data/raw/census_codes", root)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        occ = pd.read_excel(base / "2018-occupation-code-list-and-crosswalk.xlsx", sheet_name="2018 Census Occ Code List",
                            header=None, dtype=str)
    occ = occ.iloc[:, 1:4]; occ.columns = ["title", "code", "soc"]
    occ = occ[occ.code.fillna("").str.strip().str.fullmatch(r"\d{4}")]
    soc_of = {int(c): str(s).strip() for c, s in zip(occ.code, occ.soc)}
    p_codes = {c for c, s in soc_of.items() if s.startswith("51-")}
    mfg: set[int] = set()
    for f, sheet in (("2017-industry-code-list-with-crosswalk.xlsx", "2017 Census Industry Code List"),
                     ("2022-Census-Industry-Code-List-with-Crosswalk.xlsx", "2022 Census Ind Code List ")):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            t = pd.read_excel(base / f, sheet_name=sheet, header=None, dtype=str)
        t = t.iloc[:, 3:5]; t.columns = ["code", "naics"]
        t = t[t.code.fillna("").str.strip().str.fullmatch(r"\d{4}")]
        nai = t.naics.fillna("").str.strip()
        mfg |= {int(c) for c, n in zip(t.code, nai) if re.match(r"^(31|32|33)", n) or n.startswith("Part of 31")}
    for c, s in {**M_CODES, **C_CODES, **MIXED}.items():
        if soc_of.get(c) != s:
            raise ValueError(f"Census code {c}: expected SOC {s}, found {soc_of.get(c)}")
    if MOTOR_VEHICLES not in mfg:
        raise ValueError("industry 3570 not classified as manufacturing")
    return p_codes, mfg, soc_of


def month_files(root: Path) -> list[tuple[int, Path]]:
    d = repo_path("data/raw/cps/basic", root)
    out = []
    for p in sorted(d.glob("*pub.zip")):
        m = re.fullmatch(r"([a-z]{3})(\d{2})pub\.zip", p.name)
        if m:
            out.append(((2000 + int(m.group(2))) * 12 + MONTHS.index(m.group(1)), p))
    return sorted(out)


KEYS = ["hh", "hh2", "line"]


def nchs_rule(n: int, events: int, p: float, lo: float, hi: float) -> tuple[bool, str]:
    width = hi - lo
    if n < 30:
        return False, "n < 30"
    if events < 1:
        return False, "no event"
    if width >= 30:
        return False, "interval width >= 30 points"
    if width > 5 and (p <= 0 or width / p > 1.3):
        return False, "relative interval width > 130%"
    return True, ""
