# Data Download Guide (II-A)

Every input is a free public file; no login is needed. This guide lists each file, where to get it, the exact name and
folder it must have, and how to check it. Allow about an hour: the 80 CPS monthly zips are about 800 MB in total.

> II-A shares its occupation definitions and core files with II-B (*From the Production Line to Maintenance*). If you
> already downloaded II-B's files, copy the shared ones (marked **shared**) instead of downloading them again.

---

## 0. Folder layout

Put the files in these folders inside the repository. Folder names are lower case, exactly as shown.

```
data/raw/
├── onet/          knowledge.csv, essential_skills.csv, transferable_skills.csv,
│                  job_zones.csv, job_zone_reference.csv, software_skills.csv, task_statements.csv
├── oews/          oesm25in4.zip
├── oews_history/  oesm21in4.zip, oesm22in4.zip, oesm23in4.zip, oesm24in4.zip, oesm14in4.zip
├── ep/            occupation.xlsx, education.xlsx, nem-onet-to-soc-crosswalk.xlsx,
│                  National_Employment_Matrix_IND_336300.csv, industry.xlsx
├── ep_archive/    2008-18.zip, 2010-20.zip, 2012-22.zip, 2014-24.zip
├── ces/           one BLS export of series CEU3133630001 from 2016
├── ces_2008/      one BLS export of series CEU3133630001 from 2008
├── soc/           soc_2010_to_2018_crosswalk.xlsx
├── cps/basic/     jan20pub.zip … sep26pub.zip  (80 files)
├── cps/docs/      record layouts and the Census note on linking (reference only)
└── census_codes/  2018-occupation-code-list-and-crosswalk.xlsx,
                   2017-industry-code-list-with-crosswalk.xlsx,
                   2022-Census-Industry-Code-List-with-Crosswalk.xlsx
```

## Rules

1. **Use the exact file names above.** Browsers sometimes add ` (1)` or `_1` to a name (for example
   `knowledge_1.csv`); delete only the added part.
2. **Do not save a CSV or XLSX after opening it in Excel.** Excel can change codes, dates and encoding. If you saved one
   by mistake, delete it and download it again.
3. **Leave every `.zip` file zipped.** The code reads the zips directly (OEWS, EP archive, CPS).
4. **Do not substitute another release.** The code checks the release of the core files and stops on a mismatch.

---

## 1. O*NET 31.0 — 7 files → `data/raw/onet/`

O*NET rates every occupation's skills and knowledge. Click each link; the file downloads directly.

| File | Content | Link |
|---|---|---|
| `knowledge.csv` **shared** | Knowledge (33 elements) | https://www.onetcenter.org/dl_files/database/db_31_0_csv/knowledge.csv |
| `essential_skills.csv` **shared** | Essential skills (10 elements) | https://www.onetcenter.org/dl_files/database/db_31_0_csv/essential_skills.csv |
| `transferable_skills.csv` **shared** | Transferable skills (25 elements) | https://www.onetcenter.org/dl_files/database/db_31_0_csv/transferable_skills.csv |
| `software_skills.csv` | Software used in each occupation | https://www.onetcenter.org/dl_files/database/db_31_0_csv/software_skills.csv |
| `task_statements.csv` | Task statements | https://www.onetcenter.org/dl_files/database/db_31_0_csv/task_statements.csv |

`job_zones.csv` **shared** (Job Zone of each occupation; the floor map needs it) and `job_zone_reference.csv` (Job Zone
descriptions; reference only) come in the full release zip:
https://www.onetcenter.org/dl_files/database/db_31_0_csv.zip — unzip it and copy only these two files.

**If a link shows text on screen instead of downloading:** press `Ctrl + S` (`Cmd + S` on a Mac), choose "All files",
check the name ends in `.csv`, and save.

**If the 31.0 links no longer work:** get release **31.0** from the archived releases page
(https://www.onetcenter.org/db_releases.html). Do not use another release.

**Check:** rows excluding the header — knowledge 60,060; essential_skills 18,200; transferable_skills 45,500 (checked by
the code); software_skills 31,821 and task_statements 18,838 in the files used here.

---

## 2. OEWS, NAICS 336300 — 6 zip files

**May 2025 → `data/raw/oews/`** **shared**

| File | Link |
|---|---|
| `oesm25in4.zip` | https://www.bls.gov/oes/special-requests/oesm25in4.zip |

**May 2021–2024 and May 2014 → `data/raw/oews_history/`**

| File | Link | Used for |
|---|---|---|
| `oesm21in4.zip` | https://www.bls.gov/oes/special-requests/oesm21in4.zip | observed mix 2021–2025 |
| `oesm22in4.zip` | https://www.bls.gov/oes/special-requests/oesm22in4.zip | observed mix 2021–2025 |
| `oesm23in4.zip` | https://www.bls.gov/oes/special-requests/oesm23in4.zip | observed mix 2021–2025 |
| `oesm24in4.zip` | https://www.bls.gov/oes/special-requests/oesm24in4.zip | observed mix 2021–2025; 2014–24 occupation comparison |
| `oesm14in4.zip` | https://www.bls.gov/oes/special-requests/oesm14in4.zip | 2014–24 occupation comparison |

These are the "National industry-specific and by ownership" files on https://www.bls.gov/oes/tables.htm. Each zip holds
every industry; the code keeps NAICS 336300. BLS does not encourage comparing OEWS estimates over time
([OEWS FAQ](https://www.bls.gov/oes/oes_ques.htm)); the README reads the changes as observed differences.

**Check:** `oesm25in4.zip` must contain `oesm25in4/nat4d_M2025_dl.xlsx`; the NAICS 336300 total must be 538,980 jobs
(checked by the code).

---

## 3. BLS Employment Projections → `data/raw/ep/`

| File | Where to get it |
|---|---|
| `occupation.xlsx` **shared** | https://www.bls.gov/emp/tables.htm → "Occupations" → **All occupational tables in a single file (XLSX)** |
| `education.xlsx` **shared** | same page → "Education and Training" → **All education tables in a single file (XLSX)** |
| `nem-onet-to-soc-crosswalk.xlsx` **shared** | https://www.bls.gov/emp/data/occupational-data.htm → **O*NET-SOC to National Employment Matrix/Occupational Outlook Handbook Crosswalk (XLSX)** |
| `industry.xlsx` | https://www.bls.gov/emp/tables.htm → "Industries" → **All industry tables in a single file (XLSX)** (direct: https://www.bls.gov/emp/industry-employment/industry.xlsx) |
| `National_Employment_Matrix_IND_336300.csv` **shared** | see below |

**National Employment Matrix for NAICS 336300:**
1. Open https://data.bls.gov/projections/nationalMatrix?queryParams=336300&ioType=i
2. Use the export button above the table and choose **CSV**.
3. Check the name is `National_Employment_Matrix_IND_336300.csv`. Codes appear as `="00-0000"`; leave them as they are.

**Check:** the Table 1.10 sheet title of `occupation.xlsx` contains "2025–35"; the crosswalk shows "As of 08/27/2026";
Table 2.11 of `industry.xlsx` says "2025 and projected 2035" (all checked by the code). The first row of the matrix CSV is
`Total, all occupations`.

---

## 4. BLS projections archive → `data/raw/ep_archive/`

Used for the track record of past BLS projections for auto parts. Source page:
https://www.bls.gov/emp/data/projections-archive.htm

| File | Link |
|---|---|
| `2008-18.zip` | https://www.bls.gov/emp/projections-archive/2008-18.zip |
| `2010-20.zip` | https://www.bls.gov/emp/projections-archive/2010-20.zip |
| `2012-22.zip` | https://www.bls.gov/emp/projections-archive/2012-22.zip |
| `2014-24.zip` | https://www.bls.gov/emp/projections-archive/2014-24.zip |

Keep the names and do not unzip. The code reads the industry–occupation matrix inside each zip.

---

## 5. BLS Current Employment Statistics, series CEU3133630001 — 2 exports

All employees in motor vehicle parts manufacturing (NAICS 3363), not seasonally adjusted, thousands.

1. Open https://data.bls.gov/timeseries/CEU3133630001
2. Set the years and download the table as **XLSX**:
   - from **2016** to the latest year → put the file in `data/raw/ces/` **shared** (industry trend);
   - from **2008** to the latest year → put the file in `data/raw/ces_2008/` (track record).
3. Keep the file name BLS gives (for example `SeriesReport-….xlsx`). Put only one file in each folder.

**Check:** the top of each file shows `Series Id: CEU3133630001` and `Not Seasonally Adjusted`. BLS revises CES
estimates in the following months and at each annual benchmark
([BLS, CES benchmark article](https://www.bls.gov/web/empsit/cesbmart.htm)), so a later download can differ.

---

## 6. SOC 2010 → 2018 crosswalk → `data/raw/soc/`

| File | Link |
|---|---|
| `soc_2010_to_2018_crosswalk.xlsx` | https://www.bls.gov/soc/2018/soc_2010_to_2018_crosswalk.xlsx (page: https://www.bls.gov/soc/2018/crosswalks.htm) |

Used to match 2014–24 projection codes (2010 SOC) with OEWS May 2024 codes (2018 SOC).

---

## 7. CPS basic monthly public-use files → `data/raw/cps/` **shared**

Used for the age profile and monthly flows of floor occupations (manufacturing as a whole).

**Data (`cps/basic/`):** every month from January 2020 to the latest month, in the DOS/Windows `.zip` format.
- Yearly pages: https://www.census.gov/data/datasets/time-series/demo/cps/cps-basic.html → choose the year.
- File address pattern: `https://www2.census.gov/programs-surveys/cps/datasets/<YEAR>/basic/<mon><yy>pub.zip`, for
  example https://www2.census.gov/programs-surveys/cps/datasets/2020/basic/jan20pub.zip
- Names: three-letter month in lower case + two-digit year + `pub.zip` (`jan20pub.zip` … `sep26pub.zip`).
- **October 2025 does not exist:** "CPS data were not collected for October 2025 due to the lapse in appropriations",
  and there is no public-use file for that month
  ([BLS](https://www.bls.gov/cps/methods/2025-federal-government-shutdown-impact-cps.htm)). January 2020 – September
  2026 therefore gives 80 files.
- Do not unzip. Each zip holds one fixed-width `.dat` file of 1,000-character records.

**Documentation (`cps/docs/`, reference only; the code does not read it):**

| Saved here as | Official file | Link |
|---|---|---|
| `Basic_CPS_Record_Layout_starting_2020.txt` | `2020_Basic_CPS_Public_Use_Record_Layout_plus_IO_Code_list.txt` | https://www2.census.gov/programs-surveys/cps/datasets/2020/basic/2020_Basic_CPS_Public_Use_Record_Layout_plus_IO_Code_list.txt |
| `Basic_CPS_Record_Layout_starting_2025.txt` | `2025_Basic_CPS_Public_Use_Record_Layout_plus_IO_Code_list.txt` | https://www2.census.gov/programs-surveys/cps/datasets/2025/basic/2025_Basic_CPS_Public_Use_Record_Layout_plus_IO_Code_list.txt |
| `How_To_Link_CPS_Public_Use_Files.pdf` | same | https://www2.census.gov/programs-surveys/cps/methodology/How_To_Link_CPS_Public_Use_Files.pdf |

The field positions the code uses are identical in the 2020 and 2025 layouts.

---

## 8. Census industry and occupation code lists → `data/raw/census_codes/` **shared**

Source page: https://www.census.gov/topics/employment/industry-occupation/guidance/code-lists.html

| File | Link |
|---|---|
| `2018-occupation-code-list-and-crosswalk.xlsx` | https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/2018-occupation-code-list-and-crosswalk.xlsx |
| `2017-industry-code-list-with-crosswalk.xlsx` | https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/2017-industry-code-list-with-crosswalk.xlsx |
| `2022-Census-Industry-Code-List-with-Crosswalk.xlsx` | https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/2022-Census-Industry-Code-List-with-Crosswalk.xlsx |

They map CPS occupation and industry codes to SOC and NAICS. The code checks that the maintenance and machinist codes map
to the expected SOC codes and that industry 3570 is in manufacturing.

---

## 9. Versions used in this repository

| Input | Version |
|---|---|
| O*NET | release 31.0 |
| OEWS | May 2014, May 2021–2025 (national industry-specific) |
| BLS Employment Projections | 2025–35; crosswalk "As of 08/27/2026"; archive vintages 2008–18 … 2014–24 |
| CES CEU3133630001 | exports of 2026-10-19 (2016 onward) and 2026-10-27 (2008 onward), as stamped in the BLS file names |
| CPS basic monthly | January 2020 – September 2026 (80 files) |
| Census code lists | 2018 occupation; 2017 and 2022 industry |

`data/raw/MANIFEST.csv` records the SHA-256 of every file used. Compare yours with it to see whether a file differs.

## 10. Check the files

From the repository root:

```bash
python scripts/check_downloads.py      # PASS / MISSING for the core files; writes data/raw/MANIFEST.csv (SHA-256)
python run_pipeline.py                 # every layer; a layer whose file is missing prints [skip]
```

`check_downloads.py` stops the run if a core file is missing (O*NET Knowledge and Skills, OEWS May 2025, the three EP
workbooks). The floor map also needs `job_zones.csv`; the other layers print `[skip]` when their file is absent.

## Common problems

| Symptom | Fix |
|---|---|
| A link shows numbers and text on screen | save with `Ctrl/Cmd + S` (section 1) |
| A BLS page is slow or refuses the connection | try again a few minutes later or in another browser |
| A name changed to `knowledge (1).csv` / `knowledge_1.csv` | delete the added part |
| A file was saved after opening it in Excel | delete it and download it again |
| `record length is not 1000` for a CPS file | the download is damaged; download that month again |
| CES numbers differ from the README | BLS revised them; the README used the exports listed in section 9 |
