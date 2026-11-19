# Sources

All election and registration data come from the North Carolina State Board of Elections (SBOE) public file server and results site. Downloaded Nov 19 2026, 11:50–11:52 am CST.

| Data | File(s) in `raw/` | Origin | Status |
|---|---|---|---|
| 2022 U.S. Senate votes and ballots cast by county (primary) | `enr_20221108/county.txt`, `results_0.txt` … `results_100.txt` | SBOE results site JSON, https://er.ncsbe.gov/enr/20221108/data/ | OFFICIAL (all 100 counties and statewide) |
| 2026 U.S. Senate votes and ballots cast by county (primary) | `enr_20261103/county.txt`, `results_0.txt` … `results_100.txt` | SBOE results site JSON, https://er.ncsbe.gov/enr/20261103/data/ (statewide page last updated Nov 19 2026 11:19 am ET) | **UNOFFICIAL** statewide; 95 of 100 county pages OFFICIAL; Forsyth, Robeson, Watauga, Alexander, Anson unofficial |
| 2022 precinct results (cross-check) | `results_pct_20221108.zip` | https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/results_pct_20221108.zip | Official |
| 2026 precinct results (cross-check) | `results_pct_20261103.zip` | https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2026_11_03/results_pct_20261103.zip (posted Nov 13 2026) | Unofficial; Halifax later updated (Nov 16) |
| 2022 precinct-sort results (informational cross-check, not committed: 272 MB) | `AllCounties.txt` | https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/results_precinct_sort/AllCounties.txt | Absentee/early votes re-sorted to home precincts; does not reproduce canvass totals |
| Registration by county and party, election date | `voter_stats_20221108.zip`, `voter_stats_20261103.zip` | https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/voter_stats_20221108.zip, https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2026_11_03/voter_stats_20261103.zip | SBOE registration statistics for the election date (2022 file updated 01/01/2023; 2026 file 11/03/2026) |
| Population | `co-est2025-alldata.csv` | U.S. Census Bureau Vintage 2025 county estimates, https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv (POPESTIMATE2025) | Official |
| Regions | `scripts/zones.py` | NC Commerce Prosperity Zones, https://www.commerce.nc.gov/about-us/nc-prosperity-zones | Official zone lists; Mountains / Piedmont / Coastal Plain roll-up is this analysis's own |

SHA-256 of key raw files:
```
2024bf67243ef173f54e625c3bace4c8b6f80947fa7d67df26796c2c85d3e9f1  results_pct_20221108.zip
4fcc5999bbafe8f6e3e350632fa9f7f6009e10b00e14df2d4f86d095cc90fc8c  results_pct_20261103.zip
61e98e61cb9cd3f529c82fbfdd7ac17f7267a68475f25024331a90d25e969346  voter_stats_20221108.zip
2de662d51cfb46084b4e02b47f527d164934439c3a20eb905baceb1aac70dbb0  voter_stats_20261103.zip
4f5a499d851e2cb48fd7a5405e5a9235453a8a66933657aacd10df0e264f35d5  co-est2025-alldata.csv
400b1f83a16d63517e3fb19f81fe0e49c1bcfdad2350e6381959561ac8d5d007  enr_20221108/county.txt
fb2883b1892a674bf8093a8ad0c1978ef0c2f52d7d147f97c044585643e274a9  enr_20261103/county.txt
6cd10a38d8fed79c3db657fbbcb86c4c253470ad9fd80e7472a67b1a8a11600e  enr_20261103/results_0.txt
```
