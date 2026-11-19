# North Carolina 2022 vs 2026 U.S. Senate Race: ΔG Method

**Version 1, built Nov 19 2026 12:02 CST.**

> **\*2026 figures are UNOFFICIAL.** The NC State Board of Elections (SBOE) results site labels the Nov 3, 2026 statewide results "UNOFFICIAL" (statewide page last updated November 19, 2026 11:19 am ET (10:19 am CST), snapshot taken 11:52 am CST Nov 19 2026); the state canvass has not been completed. 95 of 100 county pages are marked OFFICIAL (county canvass done); 5 are still unofficial (Forsyth, Robeson, Watauga, Alexander, Anson). 2022 figures are SBOE OFFICIAL/certified results.
>
> **Race: U.S. Senate, not governor.** North Carolina elects its governor in presidential years (2020, 2024), so there was no governor race in 2022 or 2026. The top statewide race in both years was U.S. Senate (2022: Cheri Beasley (D) vs. Ted Budd (R); 2026: Roy Cooper (D) vs. Michael Whatley (R)), and it is used here in place of governor. Votes are votes for the Democratic Senate candidate, not a count of registered Democrats who voted. Registration is the SBOE voter_stats file for each election date (all parties: DEM, REP, UNA, LIB, GRE). These pages measure a pattern; they make no claim about intent, fraud or cause.

Method developed by Morissa Benson (CD3 Vice Chair, Nebraska GOP). It began with her [Cedar County Audit](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit) on the [Nebraska Election Analysis wiki](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki), the origin of the ΔG method and the reverse step used here. This wiki applies the same arithmetic, unchanged, to all 100 North Carolina counties, using **U.S. Senate** in place of governor (see the box above). Data: NC State Board of Elections (SBOE) election-results files (2022 official; 2026 unofficial) and SBOE voter-registration statistics for each election date; population from the Census Bureau. Compiled 19 Nov 2026.

## Contents

Start with the Cedar County audit in Nebraska. That is where the method began. The North Carolina pages then build up from one county (Wake) to the ten largest counties, to all 100 counties, and to the formula.

1. [Cedar County Audit](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit) (Nebraska wiki): where the method started
2. [Bottom-Up Reverse Math](Reverse-Math): Wake → the ten largest counties → all 100 counties, then solved backward for implied extra votes
3. [Locked North Carolina Formula](Locked-North-Carolina-Formula): the equation, a blank fill-in template, and the North Carolina constant (computed from NC data only)
4. [Floor and Ceiling Counties](Floor-and-Ceiling): the counties at the top and bottom, the Texas-style over-ballot check, regional constants and counties narrowed out
5. [Graphs](Graphs): slope chart, ΔG by population, stacked bars, share-vs-gain bars, residual bars, scatter, constant fit, over-ballot check

## Statewide at a glance

| Measure | 2022 (official) | 2026\* (unofficial) | Change |
|---|---|---|---|
| Democratic registration (election-date SBOE voter_stats) | 2,504,085 | 2,347,537 | −156,548 (−6.3%) |
| Total registration | 7,422,396 | 7,902,361 | +479,965 |
| Democratic U.S. Senate votes | 1,784,049 | 2,480,636\* | +696,587\* (+39.0%) |
| Republican U.S. Senate votes | 1,905,786 | 1,648,858\* | −256,928\* |
| Total ballots cast | 3,790,202 | 4,242,644\* | +452,442\* (+11.9%) |
| Democratic share of ballots (S) | 47.07% | 58.47%\* | +11.40 pts\* |
| Democratic registration share (R) | 33.74% | 29.71% | −4.03 pts |
| G = S − R | +13.33 | +28.76\* | ΔG +15.43\* |

## County results in brief

- **ΔG rose in all 100 counties.** Median ΔG is +15.28\*, with a range from +8.91\* (Orange) to +21.44\* (Robeson). 81 of 100 counties are within 3 points of the median.
- **Democratic registration share fell in all 100 counties.** Registered Democrats fell in 97 counties; Johnston, Brunswick, Harnett gained registered Democrats (non-loss counties, raw numbers only).
- **Residual after the registration-loss step** (ΔG minus the registration-share decline), 97 loss counties: median +10.03\*, positive in all 97, range +4.55\* to +14.75\*.
- **Solved backward (hypothesis):** the residuals add up to 427,569\* implied extra votes across the 97 loss counties (457,666\* on the pooled numbers for those counties). These are the votes a hypothesis of added or switched votes would have to account for, not votes shown to be improper. See [Bottom-Up Reverse Math](Reverse-Math).
- **North Carolina constant (NC data only):** ΔG = 11.83 + 0.633 × registration-share drop (all 100 counties, R² 0.41). With 7 counties narrowed out: ΔG = 11.71 + 0.648 × drop (93 counties, R² 0.47). Regional constants do **not** beat one statewide constant at the 5% level (prosperity zones p = 0.11; Mountains / Piedmont / Coastal Plain p = 0.08). See [Locked North Carolina Formula](Locked-North-Carolina-Formula).
- **Ceiling and floor:** the five highest ΔG are Robeson, Nash, Washington, Scotland, Edgecombe; the floor (most Republican baseline, lowest 2022 Democratic registration share) is Mitchell, Avery, Yadkin, Currituck, Davie. The lowest ΔG is Orange (+8.91\*). See [Floor and Ceiling Counties](Floor-and-Ceiling).
- **Texas-style over-ballot check:** counties where Democratic + Republican Senate votes exceed total ballots cast: **2022: 0; 2026\*: 0.** The highest ratio is 98.34% (Warren, 2022) and 98.26% (Durham, 2026\*). No county's total Senate votes (all candidates) exceed ballots cast in either year.

## Verification

Every county and every figure was checked in **two independent passes** that re-parse the raw SBOE files from scratch (separate scripts, separate parsers, no shared intermediate data). Pass 1: 4,700 county-figure checks (100 counties × 47 fields), 42 statewide/summary checks and 21 wiki checks, 0 mismatches. Pass 2: 4,400 county-figure checks, 28 statewide/summary checks and 1,000 wiki table figures (100 county rows × 10), 0 mismatches. Cross-source: the 2022 Senate counts match the SBOE precinct results file (results_pct) in all 100 counties; for 2026 they match in 99, and Halifax differs because Halifax updated its results on Nov 16, after the Nov 13 results_pct file was posted (this wiki uses the newer figures). Scripts and logs are in the [repository](https://github.com/mbenson8989/North-Carolina-Election-Analysis).

## Read this before using the numbers

- **This is a Senate race, not a governor race.** Candidate effects differ: 2026 featured a former two-term governor (Cooper) in an open seat. Do not compare these figures directly with governor-race figures from other states without that caveat.
- **The swing was large and close to uniform.** Every county moved toward the Democratic candidate. The ceiling counties are the top of one continuous spread, not a separate group.
- **A residual is not evidence of altered votes.** Candidate choice, crossover voting by Republicans and unaffiliated voters (unaffiliated is now North Carolina's largest registration group: 3,171,545 in 2026), turnout differences, and registration-list maintenance all move these numbers. The arithmetic cannot separate them.
- **2026 is unofficial.** Every 2026 figure is marked \* and will be re-run after the State Board's canvass.

---
**Related:** [Bottom-Up Reverse Math](Reverse-Math) · [Locked North Carolina Formula](Locked-North-Carolina-Formula) · [Floor and Ceiling Counties](Floor-and-Ceiling) · [Graphs](Graphs) · [Cedar County Audit (Nebraska)](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit)
