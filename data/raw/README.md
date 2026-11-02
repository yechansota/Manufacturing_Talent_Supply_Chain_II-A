# data/raw — immutable downloads (II-A)

Follow `docs/DATA_DOWNLOAD_GUIDE.md`. Never edit files here; re-download instead. Nothing in this folder is committed
except this README, `MANIFEST.csv` and the `.gitkeep` placeholders.

`python scripts/check_downloads.py` checks the files named in `config/project.yaml` and regenerates `MANIFEST.csv`
(path, bytes, SHA-256 of every file in this folder). The output audit compares several inputs with their SHA-256 in
`MANIFEST.csv`.

**Core inputs** (checked by `scripts/check_downloads.py`; the run stops if one is missing):

| Folder | Expected contents | Used by |
|---|---|---|
| `onet/` | `knowledge.csv`, `essential_skills.csv`, `transferable_skills.csv` (O*NET 31.0, CSV) | floor succession map, skill shift |
| `oews/` | `oesm25in4.zip` (OEWS May 2025 national industry-specific; leave zipped) | every layer that uses NAICS 336300 jobs and wages |
| `ep/` | `occupation.xlsx`, `education.xlsx`, `nem-onet-to-soc-crosswalk.xlsx` (BLS EP 2025–35) | BLS factors, crosswalk check, Job Zone mapping |

**Further inputs** (most steps print `[skip]` when their file is absent; the floor map needs `job_zones.csv`):

| Folder | File | Used by | Log |
|---|---|---|---|
| `onet/` | `job_zones.csv` | successor rule (Job Zone), adjustment by Job Zone | DL-31, DL-34 |
| `onet/` | `job_zone_reference.csv` | reference only (Job Zone descriptions; not read by the code) | — |
| `onet/` | `software_skills.csv`, `task_statements.csv` | skill content inside maintenance | DL-30 |
| `ep/` | `National_Employment_Matrix_IND_336300.csv` | projections inside NAICS 336300 | DL-23, DL-28 |
| `ep/` | `industry.xlsx` | industry employment and real output | DL-29 |
| `ces/` | BLS CES export for series CEU3133630001 (2016 onward) | observed industry employment | DL-26 |
| `ces_2008/` | BLS CES export for series CEU3133630001 (2008 onward) | projection track record | DL-38 |
| `ep_archive/` | `2008-18.zip`, `2010-20.zip`, `2012-22.zip`, `2014-24.zip` (BLS projections archive) | projection track record | DL-38 |
| `oews_history/` | `oesm21in4.zip` … `oesm24in4.zip`; `oesm14in4.zip` (leave zipped) | observed mix 2021–2025; 2014–24 occupation comparison | DL-29, DL-38 |
| `soc/` | `soc_2010_to_2018_crosswalk.xlsx` | 2014–24 occupation comparison | DL-38 |
| `cps/basic/` | `jan20pub.zip` … (CPS basic monthly public-use files, January 2020 onward) | age profile and flows | DL-44 (data as in DL-37) |
| `cps/docs/` | record layouts (2020, 2025) and the Census note on linking | reference only | DL-37 |
| `census_codes/` | 2018 Census occupation code list; 2017 and 2022 Census industry code lists (with crosswalks) | CPS code groups | DL-40 |
