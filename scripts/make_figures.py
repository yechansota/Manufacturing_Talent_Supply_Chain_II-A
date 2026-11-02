"""Render the README figures of II-A from pipeline outputs (no computation here).

    python scripts/make_figures.py      -> figures/*.png

Figure numbers of this repository (II-A); the mapping to the original single-repository numbers is in
docs/Technical Documentation.md.

Palette: single categorical slot (blue #2a78d6, validated) plus neutral ink/grid tokens;
context is drawn in muted gray so identity never depends on hue alone — every highlighted
mark is also labelled or in the legend.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
PR, TRD = ROOT / "outputs/mix", ROOT / "outputs/trend"

BLUE, INK, INK2, MUTED, GRID, BASE, SURF = "#2a78d6", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
LABELS = {
    "51-9161": "CNC tool operators", "51-4081": "Multiple machine tool setters", "51-4041": "Machinists",
    "51-2031": "Engine & machine assemblers", "51-9061": "Inspectors & testers", "51-2090": "Assemblers (team, proxy)",
    "51-4031": "Press setters & operators", "51-9124": "Coating & painting setters", "51-4072": "Molding & casting setters",
    "51-4122": "Welding machine setters", "51-2028": "Electrical/electromech. assemblers",
    "51-4121": "Welders & cutters", "53-7062": "Hand laborers (neg. control)",
    "51-1011": "Production supervisors", "51-4111": "Tool & die makers", "51-9162": "CNC programmers",
    "51-8021": "Stationary engineers", "49-9041": "Industrial machinery mechanics",
    "49-9071": "Maintenance & repair, general", "47-2111": "Electricians", "49-9043": "Machinery maintenance workers",
    "49-9044": "Millwrights",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": BASE, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.facecolor": SURF, "figure.facecolor": SURF,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.8, "axes.axisbelow": True, "savefig.facecolor": SURF,
})


def titles(fig, title: str, subtitle: str) -> None:
    fig.text(0.012, 0.975, title, ha="left", va="top", fontsize=13, fontweight="bold", color=INK)
    fig.text(0.012, 0.925, subtitle, ha="left", va="top", fontsize=9.5, color=INK2)


def fig_trend() -> Path | None:
    """Figure 1 — observed CES employment (DL-26) and the BLS projection to 2035."""
    if not (TRD / "ces_3363_annual.csv").exists():
        return None
    a = pd.read_csv(TRD / "ces_3363_annual.csv")
    m = pd.read_csv(TRD / "ces_3363_monthly.csv", parse_dates=["date"])
    nem = pd.read_csv(PR / "nem_336300.csv").set_index("soc6").loc["00-0000"]
    full = a[a.complete]
    peak = full.loc[full.emp_k.idxmax()]
    last = full.iloc[-1]
    fig, ax = plt.subplots(figsize=(10.4, 5.6))
    fig.subplots_adjust(left=0.09, right=0.97, top=0.83, bottom=0.12)
    mx = m.date.dt.year + (m.date.dt.month - 0.5) / 12
    ax.plot(mx, m.emp_k, color=MUTED, lw=1, alpha=0.8, label="Monthly, not seasonally adjusted")
    # COVID-19 display window: March 2020 (U.S. national emergency) through December 2021 — a shading choice, not a BLS period
    ax.axvspan(2020 + 2 / 12, 2022.0, color=GRID, alpha=0.75, lw=0, zorder=0)
    ax.text(2021.0 + 1 / 12, 636, "COVID-19 period\nMar 2020 – Dec 2021", ha="center", va="top", fontsize=8.3, color=INK2)
    ax.plot(full.year + 0.5, full.emp_k, "-o", color=BLUE, lw=2.2, ms=5, label="Annual average")
    part = a[~a.complete]
    if len(part):
        pr = part.iloc[-1]
        ax.plot(pr.year + 0.5, pr.emp_k, "o", ms=7, mfc=SURF, mec=BLUE, mew=1.8,
                label=f"{int(pr.year)} average of {int(pr.months)} months")
    x0, y0 = last.year + 0.5, float(nem.emp_2025_k)
    ax.plot([x0, 2035.5], [y0, float(nem.emp_2035_k)], ls=(0, (5, 3)), color=INK2, lw=0.9,
            label="BLS projection (National Employment Matrix)")
    ax.annotate(f"{int(peak.year)} peak: {peak.emp_k:.1f}k", (peak.year + 0.5, peak.emp_k), (peak.year - 1.6, peak.emp_k + 14),
                fontsize=8.5, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax.annotate(f"{int(last.year)}: {last.emp_k:.1f}k\n(matrix base {float(nem.emp_2025_k):.1f}k)", (x0, last.emp_k),
                (x0 + 0.6, last.emp_k + 22), fontsize=8.5, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax.annotate(f"2035: {float(nem.emp_2035_k):.1f}k ({float(nem.change_pct):+.1f}%)", (2035.5, float(nem.emp_2035_k)),
                (2031.0, float(nem.emp_2035_k) - 22), fontsize=8.5, color=INK2)
    low = m.loc[m.emp_k.idxmin()]
    ax.annotate(f"{low.date:%b %Y}: {low.emp_k:.1f}k", (low.date.year + (low.date.month - 0.5) / 12, low.emp_k),
                (low.date.year + 0.9, low.emp_k + 4), fontsize=8.5, color=INK2)
    ticks = list(range(2016, 2036, 2))
    ax.set_xticks(ticks); ax.set_xticklabels([str(t) for t in ticks])      # tick = 1 January; annual average at mid-year
    ax.set_xlim(2015.5, 2036.5); ax.set_ylim(360, 640)
    ax.set_ylabel("Jobs in motor vehicle parts mfg. (thousands)")
    ax.legend(loc="upper right", frameon=False, fontsize=8.5)
    drop = 100 * (last.emp_k / peak.emp_k - 1)
    titles(fig, f"Auto-parts employment is {abs(drop):.1f}% below its {int(peak.year)} peak, and BLS projects a further "
                f"{abs(float(nem.change_pct)):.1f}% by 2035",
           "BLS Current Employment Statistics, series CEU3133630001 (NAICS 3363), observed 2016–2026 · dashed = projection, "
           "not an observation")
    p = OUT / "fig1_observed_trend.png"; fig.savefig(p, dpi=200); plt.close(fig); return p


TR = ROOT / "outputs/track_record"


def fig_track() -> Path | None:
    """Figure 2 — archived BLS projections for NAICS 3363: projected vs actual 10-year change (DL-38; dumbbell)."""
    if not (TR / "industry_vintages.csv").exists():
        return None
    v = pd.read_csv(TR / "industry_vintages.csv")
    v = v[v.available].reset_index(drop=True)
    nem = pd.read_csv(PR / "nem_336300.csv").set_index("soc6").loc["00-0000"] if (PR / "nem_336300.csv").exists() else None
    rows = [(r.vintage, r.projected_change_pct, r.actual_change_pct, r.error_pct, bool(r.direction_correct),
             bool(r.pandemic_target_year)) for r in v.itertuples()]
    if nem is not None:
        rows.append(("2025-35", float(nem.change_pct), np.nan, np.nan, None, False))
    fig, ax = plt.subplots(figsize=(10.4, 5.6))
    fig.subplots_adjust(left=0.11, right=0.70, top=0.78, bottom=0.14)
    ax.axvline(0, color=INK2, lw=1.1, zorder=1)
    n = len(rows)
    for i, (vin, proj, act, err, ok, pand) in enumerate(rows):
        y = n - 1 - i
        if np.isfinite(act):
            ax.plot([proj, act], [y, y], color=GRID, lw=5, solid_capstyle="round", zorder=2)
            ax.plot(act, y, "o", ms=10, color=BLUE, mec=SURF, mew=2, zorder=4)
        ax.plot(proj, y, "o", ms=10, mfc=SURF, mec=INK2, mew=2, zorder=5)
        if np.isfinite(act):
            note = f"projected {proj:+.1f}%, actual {act:+.1f}%\nerror {err:+.0f}% \u00b7 direction {'right' if ok else 'wrong'}"
            if pand:
                note += "\n(target year 2020: pandemic)"
        else:
            note = f"projected {proj:+.1f}%\nactual not yet observed"
        ax.text(1.02, y, note.replace("-", "\u2212"), transform=ax.get_yaxis_transform(), va="center", fontsize=8.4,
                color=INK if np.isfinite(act) else INK2)
    ax.set_yticks(range(n)); ax.set_yticklabels([r[0].replace("-", "\u2013") for r in rows][::-1], fontsize=9.5)
    ax.set_ylim(-0.6, n - 0.4)
    ax.set_xlim(-25, 32)
    ax.set_xlabel("10-year change in employment, NAICS 3363 (%)")
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:+.0f}%".replace("-", "\u2212") if x else "0"))
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Line2D([], [], ls="", marker="o", ms=9, mfc=SURF, mec=INK2, mew=2, label="BLS projection (archived matrix)"),
                       Line2D([], [], ls="", marker="o", ms=9, color=BLUE, mec=SURF, mew=2, label="Actual (CES annual averages)")],
              loc="lower right", frameon=False, fontsize=8.5)
    n_low = int((v.error_pct < 0).sum()); n_chk = len(v); n_wrong = int((~v.direction_correct).sum())
    words = {4: "four", 3: "three", 5: "five"}
    titles(fig, f"In all {words.get(n_chk, n_chk)} checkable vintages, BLS projected less growth for auto parts than occurred"
           if n_low == n_chk else "Archived BLS projections for auto parts against observed employment",
           f"Archived National Employment Matrix (industry 336300) vs CES CEU3133630001 \u00b7 direction of change wrong in "
           f"{n_wrong} of {n_chk}\nBase-year values match CES within 1% \u00b7 BLS does not project business cycles; two vintages "
           "start near the 2008\u201310 recession low")
    p = OUT / "fig2_projection_track_record.png"; fig.savefig(p, dpi=200); plt.close(fig); return p


def _factor_label(level: str, text, n_rows: int = 0) -> str:
    if not isinstance(text, str) or level == "no entry":
        return f"none for auto parts; {n_rows} other industr{'y' if n_rows == 1 else 'ies'}" if n_rows else "no BLS factor listed"
    kind = text.split(" - ")[0].replace(" change", "").replace("Occupational substitution", "Substitution")
    arrow = "↑" if "share increases" in text else "↓"
    where = "auto-parts row" if level.startswith("NAICS") else "all-industry row"
    return f"{kind} {arrow} ({where})"


def fig_automation() -> Path:
    """Figure 3 — two stages inside NAICS 3363 (DL-28): industry scale to the baseline, then the BLS adjustment (NEM);
    markers = same occupation, all industries (EP); right column = BLS Table 1.12 factor."""
    b = pd.read_csv(PR / "bls_factors.csv").set_index("soc6")
    nem = pd.read_csv(PR / "nem_336300.csv").set_index("soc6")
    ind = float(nem.loc["00-0000", "change_pct"])
    base = float(nem.loc["49-9041", "baseline_change_pct"])
    tg = ["49-9041", "49-9071", "47-2111", "49-9043", "49-9044"]
    fd = ["51-9161", "51-4081", "51-4041", "51-2031", "51-9061", "51-2090", "51-4031", "51-9124", "51-4072", "51-4122",
          "51-2028", "51-4121", "51-9162"]
    key = lambda c: (-nem.loc[c, "change_pct"], -b.loc[c, "ep_change_pct"])
    rows = [(c, "target") for c in sorted(tg, key=key)] + [(c, "feeder") for c in sorted(fd, key=key)]
    fig, ax = plt.subplots(figsize=(12.0, 7.2))
    fig.subplots_adjust(left=0.22, right=0.56, top=0.80, bottom=0.15)
    ys, y = [], 0
    for i, (c, grp) in enumerate(rows):
        if i == len(tg):
            y += 0.8
        v, nat = nem.loc[c, "change_pct"], b.loc[c, "ep_change_pct"]
        adj = float(nem.loc[c, "bls_adjustment_pct"])
        col = BLUE if grp == "target" else INK2
        ax.barh(y, base, height=0.62, color=GRID, zorder=1)                       # stage 1: industry scale
        if v != base:
            ax.barh(y, v - base, left=base, height=0.62, color=col, zorder=2)     # stage 2: BLS adjustment
        else:
            ax.plot([base, base], [y - 0.31, y + 0.31], color=col, lw=2.2, zorder=2)
        ax.text(1.03, y, f"{v:+.1f}%", transform=ax.get_yaxis_transform(), va="center", ha="left", fontsize=8.3, color=INK)
        ax.text(1.17, y, f"{adj:+.0f}%" if v != base else "—", transform=ax.get_yaxis_transform(), va="center",
                ha="left", fontsize=8.3, color=INK if v != base else MUTED, fontweight="bold" if v != base else "normal")
        ax.plot(nat, y, "D", ms=5.5, mfc=SURF, mec=INK, mew=1.3, zorder=3)
        ax.text(1.33, y, _factor_label(b.loc[c, "factor_level"], b.loc[c, "factor_text"], int(b.loc[c, "n_industry_rows"])),
                transform=ax.get_yaxis_transform(), va="center", fontsize=8, color=INK2)
        ys.append(y); y += 1
    ax.axvline(base, color=INK2, lw=1, ls=(0, (4, 3)), zorder=0)
    ax.set_yticks(ys); ax.set_yticklabels([LABELS[c] + ("  (context)" if c == "51-9162" else "") for c, _ in rows],
                                          fontsize=8.5, color=INK)
    ax.invert_yaxis(); ax.axvline(0, color=INK2, lw=1); ax.grid(axis="y", visible=False)
    ax.set_xlim(-30, 24); ax.set_xlabel("Projected employment change 2025–35 (%)")
    for xx, head in ((1.03, "Change"), (1.17, "BLS adj."), (1.33, "BLS factor (EP Table 1.12)")):
        ax.text(xx, -1.1, head, transform=ax.get_yaxis_transform(), fontsize=8.5, color=INK, fontweight="bold")
    ax.text(base - 0.6, -1.0, f"industry scale {base:+.1f}%", fontsize=8, color=INK2, ha="right", va="center")
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=GRID, label=f"Stage 1 · industry scale ({base:+.1f}%, every occupation)"),
                       plt.Rectangle((0, 0), 1, 1, color=BLUE, label="Stage 2 · BLS adjustment, maintenance"),
                       plt.Rectangle((0, 0), 1, 1, color=INK2, label="Stage 2 · BLS adjustment, production"),
                       Line2D([], [], marker="D", lw=0, ms=5.5, mfc=SURF, mec=INK, mew=1.3, label="Same occupation, all industries")],
              loc="upper center", bbox_to_anchor=(0.85, -0.09), ncol=2, frameon=False, fontsize=8.3)
    titles(fig, "Auto-parts jobs shrink across the board; BLS then shifts the mix toward machinery mechanics",
           f"BLS projections 2025–35 inside motor vehicle parts mfg. (National Employment Matrix; industry total {ind:+.1f}%)\n"
           f"Stage 1 = the {base:+.1f}% shared by every occupation BLS did not adjust · Stage 2 = BLS's adjustment for that "
           "occupation (column 'BLS adj.') · ◇ all industries (EP)")
    p = OUT / "fig3_automation_shift.png"; fig.savefig(p, dpi=200); plt.close(fig); return p


def _spread(ys: dict, gap: float) -> dict:
    """Nudge end-of-line label positions apart (top-down) so labels do not overlap."""
    items = sorted(ys.items(), key=lambda kv: -kv[1])
    out, last = {}, None
    for k, v in items:
        if last is not None and last - v < gap:
            v = last - gap
        out[k] = v; last = v
    return out


def fig_mix() -> Path | None:
    """Figure 4 — observed mix inside NAICS 3363, OEWS May 2021–2025 (DL-29): employment index of the maintenance
    family and its five jobs, and the mean-wage premium of industrial machinery mechanics over the other four."""
    path = ROOT / "outputs/history/maintenance_mix.csv"
    if not path.exists():
        return None
    m = pd.read_csv(path)
    yr = m[m.year.astype(str).str.fullmatch(r"\d{4}")].copy(); yr["year"] = yr.year.astype(int)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.4, 5.2), gridspec_kw={"width_ratios": [1.35, 1]})
    fig.subplots_adjust(left=0.06, right=0.97, top=0.78, bottom=0.13, wspace=0.42)
    series = [("49-9041", LABELS["49-9041"], BLUE, 2.4, "-"), ("FAMILY", "Maintenance family (5)", INK, 1.6, "-"),
              ("49-9071", LABELS["49-9071"], MUTED, 1.2, "-"),
              ("49-9044", LABELS["49-9044"], MUTED, 1.2, "-"), ("47-2111", LABELS["47-2111"], MUTED, 1.2, "-"),
              ("49-9043", LABELS["49-9043"], MUTED, 1.2, "-")]
    ends = {}
    for code, lab, col, lw, ls in series:
        g = yr[yr.soc6 == code].sort_values("year")
        idx = 100 * g.emp / g.emp.iloc[0]
        a1.plot(g.year, idx, color=col, lw=lw, ls=ls, marker="o" if code == "49-9041" else None, ms=5, zorder=3 if code == "49-9041" else 2)
        ends[code] = (float(idx.iloc[-1]), lab, col)
    pos = _spread({k: v[0] for k, v in ends.items()}, 6.5)
    for code, (v, lab, col) in ends.items():
        a1.text(2025.15, pos[code], f"{lab}  {v - 100:+.0f}%", va="center", fontsize=8,
                color=INK if col != MUTED else INK2, fontweight="bold" if code == "49-9041" else "normal")
    a1.plot([2020.8, 2025.2], [100, 100], color=INK2, lw=0.8, zorder=1)
    a1.grid(axis="y", visible=False); a1.grid(axis="x", visible=True)
    a1.set_xticks(range(2021, 2026)); a1.set_xlim(2020.8, 2027.9); a1.set_ylim(40, 125)
    a1.spines["bottom"].set_bounds(2020.8, 2025.2)
    a1.set_ylabel("Jobs in NAICS 3363, index (May 2021 = 100)")
    a1.set_title("Employment", loc="left", fontsize=10, color=INK)
    a1.spines["right"].set_visible(False)

    comp = ["49-9043", "49-9071", "49-9044", "47-2111"]
    pr = yr[yr.soc6.isin(comp)].pivot_table(index="soc6", columns="year", values="premium_mean_49_9041_over_pct")
    order = sorted(comp, key=lambda c: -pr.loc[c, 2021])
    for i, c in enumerate(order):
        v0, v1 = pr.loc[c, 2021], pr.loc[c, 2025]
        a2.annotate("", xy=(v1, i), xytext=(v0, i), arrowprops=dict(arrowstyle="->", color=INK2, lw=1.2), zorder=2)
        a2.plot(v0, i, "o", ms=7, mfc=SURF, mec=INK2, mew=1.5, zorder=3)
        a2.plot(v1, i, "o", ms=7, color=BLUE, zorder=4)
        a2.text(max(v0, v1) + 2.0, i, f"{v0:+.0f} → {v1:+.0f}", va="center", fontsize=8, color=INK)
    a2.set_yticks(range(len(order)))
    a2.set_yticklabels([("vs " + LABELS[c]) for c in order], fontsize=8.5, color=INK)
    a2.invert_yaxis(); a2.axvline(0, color=INK2, lw=1); a2.grid(axis="y", visible=False)
    a2.set_xlim(-32, 34); a2.set_xlabel("Mean hourly wage of industrial machinery mechanics vs. … (%)")
    a2.set_title("Pay edge of industrial machinery mechanics", loc="left", fontsize=10, color=INK)
    a2.legend(handles=[Line2D([], [], marker="o", lw=0, ms=7, mfc=SURF, mec=INK2, mew=1.5, label="May 2021"),
                       Line2D([], [], marker="o", lw=0, ms=7, color=BLUE, label="May 2025")],
              loc="lower right", frameon=False, fontsize=8.3)
    titles(fig, "Maintenance jobs are moving to machinery mechanics, but their pay relative to other maintenance jobs is falling",
           "BLS OEWS May 2021–2025, NAICS 3363 · same estimation method in all five years, but BLS does not encourage OEWS "
           "time-series use\nmaintenance family = the five maintenance jobs shown · mean hourly wages (published standard errors)")
    p = OUT / "fig4_maintenance_mix.png"; fig.savefig(p, dpi=200); plt.close(fig); return p


def _interval_row(ax, y, r, col, open_marker=None, fmt="{:.1f}%", dx=0.0):
    ax.plot([r.lo, r.hi], [y, y], color=col, lw=2, solid_capstyle="round", zorder=3)
    ax.plot(r.pct, y, "o", ms=8, color=col, mec=SURF, mew=2, zorder=4)
    if open_marker is not None:
        ax.plot(open_marker, y, "D", ms=6, mfc=SURF, mec=INK2, mew=1.4, zorder=5)


FL = ROOT / "outputs/cps_flows"
A1_LABELS = {"maintenance_M": "Maintenance (5 target jobs)", "machinists_8030": "Machinists",
             "mixed_7905": "CNC operators + programmers", "mixed_8225": "Multi-machine setters +",
             "rest_R": "Other production jobs", "production_P": "All production jobs",
             "all_manufacturing": "All jobs in manufacturing", "all_employed_all_industries": "All jobs, every industry"}
A2_LABELS = {"mfg_other_production": "Other production job (mfg.)", "mfg_maintenance": "Maintenance job (mfg.)",
             "mfg_other_occupation": "Other job (mfg.)", "outside_mfg_maintenance": "Maintenance job, other industry",
             "outside_mfg_other": "Other job, other industry", "unemployed": "Unemployed", "retired": "Retired",
             "disabled": "Not working: disability", "other_nilf": "Not working: other"}


def fig_flows() -> Path | None:
    """Figure 5 — age profile and monthly flows of floor occupations in manufacturing (DL-44)."""
    if not (FL / "a1_age_profile.csv").exists():
        return None
    a1 = pd.read_csv(FL / "a1_age_profile.csv"); a2 = pd.read_csv(FL / "a2_production_destinations.csv")
    a3 = pd.read_csv(FL / "a3_maintenance_flows.csv"); bal = pd.read_csv(FL / "a3_balance.csv")
    H = "headline_no_allocation"
    fig, axs = plt.subplots(1, 3, figsize=(16.0, 6.2), gridspec_kw={"width_ratios": [1.05, 1.1, 0.95]})
    fig.subplots_adjust(left=0.13, right=0.985, top=0.74, bottom=0.16, wspace=0.85)
    # A1
    ax = axs[0]
    order = list(A1_LABELS)
    ref = a1[(a1.check == "all_records") & (a1.group == "all_employed_all_industries") & (a1.band == "55+")].iloc[0]
    ax.axvline(ref.pct, color=MUTED, lw=1, ls=(0, (3, 3)), zorder=1)
    for i, g in enumerate(order):
        r = a1[(a1.check == "all_records") & (a1.group == g) & (a1.band == "55+")].iloc[0]
        y = len(order) - 1 - i
        col = BLUE if g in ("maintenance_M", "machinists_8030") else INK2
        _interval_row(ax, y, r, col)
        ax.text(r.hi + 0.4, y, f"{r.pct:.0f}%", va="center", fontsize=8.5, color=INK)
    ax.set_yticks(range(len(order))); ax.set_yticklabels([A1_LABELS[g] for g in order][::-1], fontsize=8.6)
    ax.set_xlim(18, 37); ax.set_xlabel("Share of workers aged 55+ (%)")
    ax.set_title("Who is oldest on the floor?\n(employed in manufacturing)", fontsize=10, color=INK, loc="left")
    # A2
    ax = axs[1]
    cats = list(A2_LABELS)
    for i, c in enumerate(cats):
        r = a2[(a2.check == H) & (a2.age_band == "all") & (a2.category == c)].iloc[0]
        y = len(cats) - 1 - i
        col = BLUE if c == "mfg_maintenance" else INK2
        ax.barh(y, r.pct, height=0.62, color=col if c == "mfg_maintenance" else BASE, zorder=3)
        ax.plot([r.lo, r.hi], [y, y], color=INK, lw=1, zorder=4)
        ax.text(r.hi + 0.04, y, f"{r.pct:.2f}%", va="center", fontsize=8.3, color=INK)
    ax.set_yticks(range(len(cats))); ax.set_yticklabels([A2_LABELS[c] for c in cats][::-1], fontsize=8.6)
    stay = a2[(a2.check == H) & (a2.age_band == "all") & (a2.category == "mfg_same_occupation")].iloc[0]
    ax.set_xlim(0, 2.75); ax.set_xlabel("Share of production workers, next month (%)")
    ax.set_title(f"Where production workers are a month later\n({stay.pct:.0f}% stay in the same job, not shown)",
                 fontsize=10, color=INK, loc="left")
    # A3
    ax = axs[2]
    bands = ["16-34", "35-54", "55+"]
    xs = np.arange(len(bands))
    for j, (direction, cat, col, lab) in enumerate((("inflow", "production", BLUE, "In from production"),
                                                     ("outflow", "retired", INK2, "Out to retirement"))):
        for k_, b in enumerate(bands):
            r = a3[(a3.check == H) & (a3.direction == direction) & (a3.category == cat) & (a3.age_band == b)].iloc[0]
            x = xs[k_] + (j - 0.5) * 0.36
            ax.bar(x, r.pct, width=0.34, color=col, zorder=3, label=lab if k_ == 0 else None)
            ax.plot([x, x], [r.lo, r.hi], color=INK, lw=1, zorder=4)
            ax.text(x, r.hi + 0.05, f"{r.pct:.1f}", ha="center", va="bottom", fontsize=8, color=INK)
    ax.set_xticks(xs); ax.set_xticklabels(["16\u201334", "35\u201354", "55+"], fontsize=9)
    ax.set_ylim(0, 2.9); ax.set_ylabel("Per 100 maintenance workers, per month")
    ax.set_xlabel("Age group")
    b = bal[(bal.check == H) & (bal.ratio.str.startswith("inflow from production"))].iloc[0]
    ax.set_title("Maintenance in manufacturing: in from\nproduction vs out to retirement", fontsize=10, color=INK, loc="left")
    ax.text(0.02, 0.97, f"all ages: in from production / out to\nretirement = {b.value:.1f} (95% {b.lo:.1f}\u2013{b.hi:.1f})",
            transform=ax.transAxes, va="top", fontsize=8.3, color=INK)
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.89), frameon=False, fontsize=8.5)
    ax.grid(axis="x", visible=False)
    titles(fig, "Maintenance and machinist jobs are the oldest on the floor; entries from production are about twice the exits to retirement",
           "Current Population Survey, Jan 2020 \u2013 Sep 2026 \u00b7 manufacturing as a whole, not NAICS 3363 \u00b7 A1 pools monthly records; "
           "A2\u2013A3 follow the same person over consecutive months (no imputed codes)\n95% intervals: household bootstrap \u00b7 "
           "people who move house are not followed; monthly status changes include reporting error \u00b7 exploratory (DL-44)")
    p = OUT / "fig5_cps_aging_flows.png"; fig.savefig(p, dpi=200); plt.close(fig); return p


FLOOR_NAMES = {
    "51-2090": "Assemblers (team, proxy)", "51-4031": "Press setters & operators", "51-1011": "Production supervisors",
    "51-9061": "Inspectors & testers", "51-2031": "Engine & machine assemblers", "53-7062": "Hand laborers & movers",
    "51-4121": "Welders & cutters", "51-4081": "Multiple machine tool setters", "49-9041": "Industrial machinery mechanics",
    "51-2028": "Electrical/electromech. assemblers", "53-7051": "Industrial truck operators", "51-4041": "Machinists",
    "51-9161": "CNC tool operators", "51-4111": "Tool & die makers", "51-4072": "Molding & casting setters",
    "49-9071": "Maintenance & repair, general", "17-3026": "Industrial engineering technicians",
    "51-9124": "Coating & painting setters", "51-4122": "Welding machine setters", "47-2111": "Electricians",
    "53-7065": "Stockers & order fillers", "49-1011": "Supervisors of mechanics", "51-9198": "Production helpers",
    "53-7064": "Hand packers", "51-4033": "Grinding & polishing setters", "51-6031": "Sewing machine operators",
    "17-3027": "Mechanical engineering technicians", "49-9043": "Machinery maintenance workers",
    "53-1047": "Material-moving supervisors", "49-3023": "Automotive service technicians", "49-9044": "Millwrights",
    "51-9162": "CNC tool programmers", "53-3032": "Heavy truck drivers"}


def fig_floor() -> Path | None:
    """Figure 6 — succession bench for every floor position (DL-31): close internal successors per job held."""
    path = ROOT / "outputs/floor_map/position_summary.csv"
    if not path.exists():
        return None
    s = pd.read_csv(path)
    s["name"] = s.soc6.map(FLOOR_NAMES).fillna(s.title.str[:30])
    s = s.sort_values(["bench_ratio", "jobs_2025"], ascending=[False, False]).reset_index(drop=True)
    n = len(s)
    fig, ax = plt.subplots(figsize=(12.4, 0.29 * n + 2.6))
    fig.subplots_adjust(left=0.235, right=0.50, top=1 - 1.55 / (0.29 * n + 2.6), bottom=0.9 / (0.29 * n + 2.6))
    NONE_X = 0.06
    ax.axvspan(0.04, 0.085, color=GRID, alpha=0.6, lw=0)
    ax.axvline(1, color=INK2, lw=1, ls=(0, (4, 3)))
    for i, r in s.iterrows():
        x = r.bench_ratio if r.bench_ratio > 0 else NONE_X
        col = BLUE if r.maintenance_target else (MUTED if r.bench_ratio > 0 else SURF)
        size = 18 + 260 * (r.jobs_2025 / s.jobs_2025.max()) ** 0.6
        ax.scatter(x, i, s=size, color=col, edgecolor=BLUE if r.maintenance_target else INK2, lw=1.0, zorder=3)
        tr = ax.get_yaxis_transform()
        ax.text(1.03, i, f"{r.jobs_2025 / 1000:.1f}k", transform=tr, va="center", ha="left", fontsize=7.8, color=INK)
        adj = r.bls_adjustment_pct
        ax.text(1.17, i, "—" if abs(adj) < 0.05 else f"{adj:+.0f}%", transform=tr, va="center", ha="left", fontsize=7.8,
                color=INK if abs(adj) >= 0.05 else MUTED, fontweight="bold" if adj > 0.05 else "normal")
        cp = r.get("close_pool_change_2021_2025_pct")
        ax.text(1.34, i, "—" if pd.isna(cp) else f"{cp:+.0f}%", transform=tr, va="center", ha="left", fontsize=7.8,
                color=INK if not pd.isna(cp) else MUTED)
        top = r.get("top1_source")
        lab = "—" if pd.isna(top) else f"{FLOOR_NAMES.get(top, top)} (P {r.top1_P:.0f})"
        ax.text(1.53, i, lab, transform=tr, va="center", ha="left", fontsize=7.8, color=INK2)
    for xx, head in ((1.03, "Jobs"), (1.17, "BLS adj."), (1.34, "Close pool\n2021–25"), (1.53, "Nearest eligible successor")):
        ax.text(xx, -1.2, head, transform=ax.get_yaxis_transform(), fontsize=8.3, color=INK, fontweight="bold", va="bottom")
    ax.set_yticks(range(n))
    ax.set_yticklabels(s.name, fontsize=8.3, color=INK)
    for lab, mt in zip(ax.get_yticklabels(), s.maintenance_target):
        if mt:
            lab.set_fontweight("bold")
    ax.set_ylim(n - 0.4, -1.6); ax.set_xscale("log"); ax.set_xlim(0.04, 300)
    ax.set_xticks([0.06, 1, 10, 100]); ax.set_xticklabels(["none", "1", "10", "100"]); ax.minorticks_off()
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Close internal successors per job in the position (jobs in eligible roles with P ≤ 25, log scale)")
    ax.text(1.12, -1.2, "bench = position size", fontsize=7.6, color=INK2, va="bottom")
    titles(fig, "Succession bench for every floor position: deep for maintenance, absent for most entry roles",
           "NAICS 3363, 33 floor occupations with ≥ 1,000 jobs (OEWS May 2025) · successor = lower-paid role with the same or a "
           "lower Job Zone and Skills P ≤ 25 · bold = maintenance targets\nBLS adj. = BLS's share adjustment vs. the −12.9% "
           "industry baseline · close pool 2021–25 = observed OEWS change of the close successor roles · point estimates, exploratory")
    p = OUT / "fig6_floor_bench.png"; fig.savefig(p, dpi=200); plt.close(fig); return p


def fig_jobzone() -> Path | None:
    """Figure S1 (Technical Documentation) — BLS adjustment vs O*NET Job Zone for every NEM 336300 line item (DL-34)."""
    occ_p, sum_p = PR / "bls_adjustment_by_occupation_job_zone.csv", PR / "bls_adjustment_by_job_zone.csv"
    if not (occ_p.exists() and sum_p.exists()):
        return None
    occ = pd.read_csv(occ_p).dropna(subset=["job_zone"])
    sm = pd.read_csv(sum_p).set_index("job_zone")
    zones = list(sm.index)
    fig, ax = plt.subplots(figsize=(10.4, 6.2))
    fig.subplots_adjust(left=0.09, right=0.97, top=0.81, bottom=0.17)
    sign = lambda v, nd=0: f"{v:+.{nd}f}".replace("-", "\u2212")
    rng = np.random.default_rng(7)                                   # fixed jitter so the figure is reproducible
    xi = {z: i for i, z in enumerate(zones)}
    x = occ.job_zone.map(xi) + rng.uniform(-0.22, 0.22, len(occ))
    size = 12 + 160 * np.sqrt(occ.emp_2025_k / occ.emp_2025_k.max())
    ax.scatter(x, occ.bls_adjustment_pct, s=size, color=MUTED, alpha=0.45, lw=0, zorder=2)
    for z in zones:
        r = sm.loc[z]
        ax.plot([xi[z] - 0.32, xi[z] + 0.32], [r.mean_adjustment_pct] * 2, color=BLUE, lw=2.4, zorder=4)
        ax.text(xi[z] + 0.36, r.mean_adjustment_pct, f"{sign(r.mean_adjustment_pct, 1)}%", va="center", fontsize=8.5,
                color=BLUE, fontweight="bold")
    ax.axhline(0, color=INK2, lw=0.8, zorder=1)
    marks = {"49-9041": (0.25, 3.5), "49-9043": (0.25, -3.0), "51-9161": (-0.15, -4.2), "51-9162": (0.2, 3.2)}
    for code, (dx, dy) in marks.items():
        r = occ[occ.code == code]
        if r.empty:
            continue
        r = r.iloc[0]
        xx = xi[r.job_zone] + float(x[r.name] - occ.job_zone.map(xi)[r.name])
        ax.scatter([xx], [r.bls_adjustment_pct], s=60, color=BLUE, zorder=5)
        ax.annotate(f"{LABELS.get(code, r.title)} ({sign(r.bls_adjustment_pct)}%)", (xx, r.bls_adjustment_pct),
                    (xx + dx, r.bls_adjustment_pct + dy), fontsize=8.5, color=INK,
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax.set_xticks(range(len(zones)))
    prep = {2: "little to some", 3: "medium", 4: "considerable", 5: "extensive"}
    ax.set_xticklabels([f"Job Zone {'1–2' if z == 2 else z}: {prep.get(z, '')}\n{int(sm.loc[z].n)} occupations · "
                        f"{sm.loc[z].emp_2025_k:.0f}k jobs\nraised {sm.loc[z].share_up_pct:.0f}% · cut "
                        f"{sm.loc[z].share_down_pct:.0f}%" for z in zones], fontsize=8.6)
    ax.set_xlim(-0.6, len(zones) - 0.3); ax.set_ylim(-23, 27)
    ax.set_ylabel("BLS adjustment vs. the −12.9% industry baseline (%)")
    handles = [Line2D([], [], color=BLUE, lw=2.4, label="Mean of occupations in the zone"),
               Line2D([], [], marker="o", ls="", color=MUTED, alpha=0.6, ms=8, label="One occupation (size = 2025 jobs)")]
    ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=8.5)
    rho = float(sm.spearman_rho.iloc[0]); n = int(sm.n_with_job_zone.iloc[0]); tot = int(sm.n_line_items.iloc[0])
    titles(fig, "BLS raises jobs that need more preparation and cuts jobs that need less",
           f"Motor vehicle parts (NAICS 3363), BLS National Employment Matrix 2025–35 · {n} of {tot} occupations with an "
           f"O*NET Job Zone · Spearman ρ = {rho:.2f}\nAdjustments are BLS's projections, not observed change · "
           "O*NET 31.0 merges Job Zones 1 and 2")
    p = OUT / "figS1_adjustment_by_job_zone.png"; fig.savefig(p, dpi=200); plt.close(fig); return p


def main() -> int:
    OUT.mkdir(exist_ok=True)
    for fn in (fig_trend, fig_track, fig_automation, fig_mix, fig_flows, fig_floor, fig_jobzone):
        p = fn()
        if p is not None:
            print("wrote", p.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
