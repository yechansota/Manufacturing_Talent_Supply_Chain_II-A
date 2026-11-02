"""Multiple-comparison helper (Benjamini-Hochberg), copied verbatim from II-B (DL-36a)."""
from __future__ import annotations

import numpy as np


def bh_adjust(p) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values (step-up); reject where adjusted p <= q."""
    p = np.asarray(p, dtype=float)
    n = len(p)
    o = np.argsort(p, kind="stable")
    adj = np.minimum.accumulate((p[o] * n / np.arange(1, n + 1))[::-1])[::-1]
    out = np.empty(n)
    out[o] = np.minimum(adj, 1.0)
    return out

