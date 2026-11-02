"""
================================================================================
 Manufacturing Talent Supply Chain II-A
 Where Each Floor Job's Successors Come From — full pipeline
 U.S. motor vehicle parts manufacturing, NAICS 3363 (exploratory / descriptive)
================================================================================

 Runs every step in order, stops at the first failure, and writes the complete
 console output to results_log.txt.

 DATA REQUIRED (all free, no login) — see docs/DATA_DOWNLOAD_GUIDE.md
   data/raw/onet/  knowledge.csv, essential_skills.csv, transferable_skills.csv,
                   job_zones.csv, job_zone_reference.csv,
                   software_skills.csv, task_statements.csv      (O*NET 31.0, CSV)
   data/raw/oews/  oesm25in4.zip                                 (OEWS May 2025, by industry)
   data/raw/oews_history/  oesm21in4.zip … oesm24in4.zip, oesm14in4.zip  (OEWS May 2021–2024, May 2014)
   data/raw/ep/    occupation.xlsx, education.xlsx, nem-onet-to-soc-crosswalk.xlsx,
                   National_Employment_Matrix_IND_336300.csv, industry.xlsx   (BLS EP 2025–35)
   data/raw/ep_archive/  2008-18.zip … 2014-24.zip               (BLS projections archive)
   data/raw/ces/, data/raw/ces_2008/   CEU3133630001 monthly exports (BLS CES)
   data/raw/soc/   soc_2010_to_2018_crosswalk.xlsx
   data/raw/cps/basic/   jan20pub.zip … (CPS basic monthly); data/raw/census_codes/

 Occupation definitions shared with II-B are read from config/project.yaml.
 II-A is not pre-registered; every analysis is logged in outputs/analysis_log.md
 (DL entries copied from II-B, then AL-1 …).

 Usage:   python run_pipeline.py            # full run (bootstraps B = 200 / 1,000)
          python run_pipeline.py --quick    # every bootstrap with 50 draws (smoke test only; output audit skipped)
================================================================================
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG = ROOT / "results_log.txt"

STEPS = [
    ("DATA CHECK — files present, SHA-256 manifest", ["scripts/check_downloads.py"]),
    ("O*NET INGEST — schema, row counts, duplicates", ["-m", "src.ingest_onet"]),
    ("OEWS NAICS 336300 — ingest and occupation re-validation", ["-m", "src.ingest_oews"]),
    ("BLS EP 2025–35 — tables and O*NET-SOC crosswalk check", ["-m", "src.ingest_ep"]),
    ("BLS PROJECTIONS INSIDE NAICS 3363 — factors, NEM two-stage reading, industry output, adjustment by Job Zone, automation share of adjustments (DL-14, 23, 28, 29, 34, 39)", ["-m", "src.mix"]),
    ("OBSERVED TREND — CES employment, NAICS 3363 (DL-26)", ["-m", "src.trend"]),
    ("OBSERVED MIX — OEWS May 2021–2025 inside NAICS 3363 (DL-29)", ["-m", "src.history"]),
    ("SKILL SHIFT — inside the maintenance family: levels, software, tasks (DL-30)", ["-m", "src.skill_shift"]),
    ("FLOOR SUCCESSION MAP — every floor position with ≥ 1,000 jobs; bootstrap, rule variants, cross-part links (DL-31–33)", ["-m", "src.floor_map"]),
    ("PROJECTION TRACK RECORD — archived BLS projections for NAICS 3363 vs CES and OEWS (DL-38, 40, 41)", ["-m", "src.track_record"]),
    ("CPS AGE PROFILE AND FLOWS — floor occupations in manufacturing (DL-44)", ["-m", "src.cps_flows"]),
    ("FIGURES", ["scripts/make_figures.py"]),
    ("OUTPUT AUDIT — cross-path checks of every derived output (E1–E17)", ["-m", "src.output_audit"]),
]


def banner(text: str) -> str:
    line = "=" * 78
    return f"\n{line}\n  {text}\n{line}\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the full pipeline and write results_log.txt")
    ap.add_argument("--quick", action="store_true", help="bootstraps with 50 draws (not for reporting)")
    args = ap.parse_args()
    out = [banner("MANUFACTURING TALENT SUPPLY CHAIN II-A — WHERE EACH FLOOR JOB'S SUCCESSORS COME FROM — FULL PIPELINE"),
           f"Started (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n"
           "Industry: NAICS 336300 Motor Vehicle Parts Manufacturing (national); CPS: manufacturing as a whole\n"
           "Inputs: O*NET 31.0 · OEWS May 2014, 2021–2025 · BLS Employment Projections 2025–35 and archive · CES · CPS 2020–2026\n"]
    ok = True
    for title, cmd in STEPS:
        if args.quick and cmd[-1] in ("src.floor_map", "src.cps_flows"):
            cmd = cmd + ["--draws", "50"]
            title += "  [QUICK: 50 draws — not for reporting]"
        if args.quick and cmd[-1] == "src.output_audit":
            continue
        t0 = time.time()
        res = subprocess.run([sys.executable, *cmd], cwd=ROOT, capture_output=True, text=True)
        out.append(banner(title))
        out.append(res.stdout)
        if res.stderr.strip():
            out.append("[stderr]\n" + res.stderr)
        out.append(f"-> exit {res.returncode} ({time.time() - t0:.1f} s)\n")
        print(f"[{'OK' if res.returncode == 0 else 'FAIL'}] {title} ({time.time() - t0:.1f} s)")
        if res.returncode != 0:
            ok = False
            break
    out.append(banner("PIPELINE " + ("COMPLETED" if ok else "STOPPED — see the failing step above")))
    LOG.write_text("".join(out), encoding="utf-8")
    print(f"Log written to {LOG.name}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
