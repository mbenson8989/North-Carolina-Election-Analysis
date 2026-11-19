# North-Carolina-Election-Analysis
North Carolina 22-26, U.S. Senate, ΔG method from the Cedar County (Nebraska) audit, Residual Math, Locked North Carolina Formula

North Carolina, 2022 vs 2026, all 100 counties. Same method as Morissa Benson's
[Nebraska Election Analysis wiki](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki), which began with the
[Cedar County Audit](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit).
The write-up is on this repo's **Wiki** tab (Home, Reverse-Math, Locked-North-Carolina-Formula, Floor-and-Ceiling, Graphs).

**Race: U.S. Senate, not governor.** North Carolina elects its governor in presidential years, so there was no governor race in 2022 or 2026.
The top statewide race both years was U.S. Senate (2022 Beasley–Budd; 2026 Cooper–Whatley), used here in place of governor.

**2026 figures are unofficial** (NC State Board of Elections results site, statewide results labeled UNOFFICIAL on Nov 19 2026; state canvass pending).
These files measure a pattern; they make no claim about intent, fraud or cause. "Implied extra votes" are what a
hypothesis would have to account for, not votes shown to be improper.

## Formula (ballots denominator)
- S = Democratic Senate votes ÷ total ballots cast × 100
- R = Democratic registered ÷ total registered (all parties, SBOE voter_stats for the election date) × 100
- G = S − R; ΔG = G 2026 − G 2022
- Residual = ΔG − (R 2022 − R 2026) = S 2026 − S 2022 (loss counties only)
- Implied extra votes = residual × ballots 2026 ÷ 100 = D 2026 − (S 2022 ÷ 100) × ballots 2026
- NC constant (NC data only): ΔG = c + k × (R 2022 − R 2026), OLS over the 100 counties

## Files
- `charts/*.png`: the charts embedded in the wiki
- `data/nc_senate_2022_2026_by_population.csv`: every county input and result, largest to smallest population (Census Vintage 2025)
- `data/summary.json`: statewide results, constants, regional tests, floor/ceiling, over-ballot check
- `scripts/run_all.sh` runs `build_data.py` → `analysis.py` → `charts.py` → `build_wiki.py` → `verify_pass1.py` + `verify_pass2.py`
- `VERIFY_LOG.txt`: output of the two independent verification passes (each re-parses the raw SBOE files from scratch)
- `wiki/`: the wiki pages as generated
- `raw/`: the SBOE and Census source files (see `SOURCES.md`)

## Reproduce
```
pip install pandas numpy statsmodels matplotlib
bash scripts/run_all.sh
```
