# North Carolina County PDF Information

> **\*2026 figures are UNOFFICIAL.** The NC State Board of Elections (SBOE) results site labels the Nov 3, 2026 statewide results "UNOFFICIAL" (statewide page last updated November 19, 2026 11:19 am ET (10:19 am CST), snapshot taken 11:52 am CST Nov 19 2026); the state canvass has not been completed. 95 of 100 county pages are marked OFFICIAL (county canvass done); 5 are still unofficial (Forsyth, Robeson, Watauga, Alexander, Anson). 2022 figures are SBOE OFFICIAL/certified results.
>
> **Race: U.S. Senate, not governor.** North Carolina elects its governor in presidential years (2020, 2024), so there was no governor race in 2022 or 2026. The top statewide race in both years was U.S. Senate (2022: Cheri Beasley (D) vs. Ted Budd (R); 2026: Roy Cooper (D) vs. Michael Whatley (R)), and it is used here in place of governor. Votes are votes for the Democratic Senate candidate, not a count of registered Democrats who voted. Registration is the SBOE voter_stats file for each election date (all parties: DEM, REP, UNA, LIB, GRE). These pages measure a pattern; they make no claim about intent, fraud or cause.

This 4-page PDF covers all 100 North Carolina counties, 2022 vs 2026\*, U.S. Senate race (substituted for governor). It is modeled on Nebraska's [93-County Summary PDF](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/93-County-PDF-Information): same column order, same two tables, statewide totals row at the bottom of each table.

**[Download the North Carolina 100-County PDF](https://raw.githubusercontent.com/mbenson8989/North-Carolina-Election-Analysis/main/pdf/North_Carolina_100_County_Democratic_Registration_and_Vote_Change.pdf)** · [View it on GitHub](https://github.com/mbenson8989/North-Carolina-Election-Analysis/blob/main/pdf/North_Carolina_100_County_Democratic_Registration_and_Vote_Change.pdf)

## Sort order

Counties are sorted by **2026 Democratic share of registration** (Democratic registered voters ÷ all registered voters, SBOE voter_stats for 11/03/2026), highest first. Hertford is first (56.9%). The last row of each table is the statewide total. Rows shaded blue are counties where Democratic registration rose (Johnston, Brunswick, Harnett); no county's Democratic Senate votes fell.

## Table 1 columns (pages 1–2)

| Column | Meaning |
|---|---|
| County | County name |
| Dem Reg Share 2026 % | Democratic registered voters ÷ all registered voters, 11/03/2026 |
| Dem Reg 2022 / Dem Reg 2026 | Registered Democrats, SBOE voter_stats for 11/08/2022 and 11/03/2026 |
| Reg Change # / Reg Change % | 2026 minus 2022, and that change as a percent of 2022 |
| Dem Senate Votes 2022 / 2026\* | Votes for the Democratic U.S. Senate candidate (Beasley 2022; Cooper 2026\*) |
| Vote Change # / Vote Change % | 2026\* minus 2022, and that change as a percent of 2022 |
| Total Ballots 2022 / 2026\* | Total ballots cast in the county (SBOE results site) |
| Ballot Change # / Ballot Change % | 2026\* minus 2022, and that change as a percent of 2022 |

## Table 2 columns (pages 3–4)

| Column | Meaning |
|---|---|
| Dem Share of Ballots 2022 % / 2026\* % | Democratic Senate votes ÷ total ballots cast |
| Change (pts) | 2026\* share minus 2022 share, percentage points (from unrounded shares) |
| Dem Share of Registration 2022 % / 2026 % | Democratic registered voters ÷ all registered voters |
| Total Registered 2022 / 2026 | All registered voters, all parties (DEM, REP, UNA, LIB, GRE) |

Percentages are rounded to one decimal place and point changes to two.

## Statewide totals row

| Dem Reg Share 2026 | Dem Reg 2022 | Dem Reg 2026 | Reg Change | Dem Senate Votes 2022 | 2026\* | Vote Change | Total Ballots 2022 | 2026\* | Ballot Change |
|---|---|---|---|---|---|---|---|---|---|
| 29.7% | 2,504,085 | 2,347,537 | −156,548 (−6.3%) | 1,784,049 | 2,480,636\* | +696,587\* (+39.0%) | 3,790,202 | 4,242,644\* | +452,442\* (+11.9%) |

## Verification

Before publishing, every cell in the PDF was checked against the **raw SBOE files** by an independent script (`scripts/verify_pdf_raw.py`). It re-parses the raw results-site files and voter_stats files from scratch (not the summary tables), recomputes each value with exact arithmetic, rounds it to the precision shown in the PDF, and compares it with the text extracted from the PDF: **2,020 cells checked (100 counties + statewide total, both tables), 2,020 matched, 0 mismatches**, and the row order matches the 2026 registration-share sort. A second script (`scripts/verify_pdf.py`) checked the same 2,020 figures against the verified county data plus 11 county-sum checks against the statewide row: 0 mismatches.

## Sources

NC State Board of Elections: results-site county data for 11/08/2022 (OFFICIAL) and 11/03/2026 (UNOFFICIAL\*), and voter_stats registration files for each election date, all downloaded 19 Nov 2026. Full list in [SOURCES.md](https://github.com/mbenson8989/North-Carolina-Election-Analysis/blob/main/SOURCES.md).

---
**Related:** [Home](Home) · [Bottom-Up Reverse Math](Reverse-Math) · [Locked North Carolina Formula](Locked-North-Carolina-Formula) · [Floor and Ceiling Counties](Floor-and-Ceiling) · [Graphs](Graphs) · [Cedar County Audit (Nebraska)](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit)
