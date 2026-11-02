"""O*NET rating arrays and rating-uncertainty draws used by the floor map (DL-31).

Copied verbatim from II-B's bootstrap module (DL-36a): the same Knowledge SE imputation (median Incumbent SE per
element and scale) and the same truncated-normal draws within the O*NET scale bounds.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import duckdb
import numpy as np
import pandas as pd
from scipy.stats import truncnorm

TIE_TOL = 1e-12   # D values are O(0.1–2); a position's own row in the reference set must count as a tie (DL-22)


@dataclass
class DomainArrays:
    domain: str
    codes: np.ndarray
    elements: np.ndarray
    L: np.ndarray
    I: np.ndarray
    seL: np.ndarray
    seI: np.ndarray
    n_imputed: int


def impute_missing_se(se: pd.DataFrame, source: pd.Series, reference_source: str = "Incumbent") -> tuple[pd.DataFrame, int]:
    """Fill missing SE with the median SE of `reference_source`-rated occupations, per element (one scale)."""
    missing = se.isna()
    n = int(missing.to_numpy().sum())
    if n == 0:
        return se, 0
    ref_rows = source.reindex(se.index) == reference_source
    med = se.loc[ref_rows].median(axis=0)
    if med.isna().any():
        raise ValueError(f"no {reference_source} SE available for elements {med[med.isna()].index.tolist()}")
    return se.fillna(med), n


def load_arrays(con: duckdb.DuckDBPyConnection, domain: str, cfg: dict[str, Any]) -> DomainArrays:
    lv = cfg["measurement"]["scales"]["level"]["id"]
    im = cfg["measurement"]["scales"]["importance"]["id"]
    r = con.execute("SELECT onet_code, element_id, scale_id, data_value, se, domain_source "
                    "FROM onet_ratings WHERE domain = ?", [domain]).df()
    piv = lambda s, v: r[r.scale_id == s].pivot(index="onet_code", columns="element_id", values=v)
    L = piv(lv, "data_value").sort_index()
    I = piv(im, "data_value").loc[L.index, L.columns]
    seL = piv(lv, "se").loc[L.index, L.columns]
    seI = piv(im, "se").loc[L.index, L.columns]
    source = r.drop_duplicates("onet_code").set_index("onet_code")["domain_source"]
    if domain == "K":
        seL, nL = impute_missing_se(seL, source)
        seI, nI = impute_missing_se(seI, source)
    else:
        nL = nI = 0
    if seL.isna().any().any() or seI.isna().any().any():
        raise ValueError(f"domain {domain}: missing SE outside the imputation scope shared with II-B")
    return DomainArrays(domain, L.index.to_numpy(), L.columns.to_numpy(), L.to_numpy(), I.to_numpy(),
                        seL.to_numpy(), seI.to_numpy(), nL + nI)



def sample_truncnorm(values: np.ndarray, se: np.ndarray, lo: float, hi: float,
                     rng: np.random.Generator) -> np.ndarray:
    out = values.astype(float).copy()
    mask = se > 0
    loc, sc = values[mask], se[mask]
    out[mask] = truncnorm.rvs((lo - loc) / sc, (hi - loc) / sc, loc=loc, scale=sc, random_state=rng)
    return out
