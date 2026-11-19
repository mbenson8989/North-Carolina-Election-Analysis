import json, os
import pandas as pd
H = os.path.dirname(os.path.abspath(__file__)); D = f"{H}/../data"; W = f"{H}/../wiki"
df = pd.read_csv(f"{D}/nc_senate_2022_2026_by_population.csv"); S = json.load(open(f"{D}/summary.json"))
RAWURL = "https://raw.githubusercontent.com/mbenson8989/North-Carolina-Election-Analysis/main/charts/"
CEDAR = "https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit"
NEWIKI = "https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki"
BUILT = "Nov 19 2026 " + os.environ.get("BUILT_TIME", "")
n = lambda v: f"{int(round(v)):,}"
sg = lambda v, d=2: ("+" if v >= 0 else "−") + f"{abs(v):.{d}f}"
sn = lambda v: ("+" if v >= 0 else "−") + f"{abs(int(round(v))):,}"
pc = lambda v, d=2: f"{v:.{d}f}%"
row = lambda c: df[df.county == c].iloc[0]
unoff = S["unofficial_counties26"]
BANNER = (f"> **\\*2026 figures are UNOFFICIAL.** The NC State Board of Elections (SBOE) results site labels the Nov 3, 2026 statewide results "
          f"\"UNOFFICIAL\" (statewide page last updated {S['enr_updated26']} ET (10:19 am CST), snapshot taken 11:52 am CST Nov 19 2026); the state canvass has not been completed. "
          f"{S['county_official26']} of 100 county pages are marked OFFICIAL (county canvass done); {len(unoff)} are still unofficial ({', '.join(unoff)}). "
          f"2022 figures are SBOE OFFICIAL/certified results.\n>\n"
          f"> **Race: U.S. Senate, not governor.** North Carolina elects its governor in presidential years (2020, 2024), so there was no governor race in 2022 or 2026. "
          f"The top statewide race in both years was U.S. Senate (2022: Cheri Beasley (D) vs. Ted Budd (R); 2026: Roy Cooper (D) vs. Michael Whatley (R)), and it is used here in place of governor. "
          f"Votes are votes for the Democratic Senate candidate, not a count of registered Democrats who voted. Registration is the SBOE voter_stats file for each election date (all parties: DEM, REP, UNA, LIB, GRE). "
          f"These pages measure a pattern; they make no claim about intent, fraud or cause.")
def rel(*pages):
    names = {"Home": "Home", "Reverse-Math": "Bottom-Up Reverse Math", "Locked-North-Carolina-Formula": "Locked North Carolina Formula",
             "Floor-and-Ceiling": "Floor and Ceiling Counties", "Graphs": "Graphs"}
    return "\n---\n**Related:** " + " · ".join(f"[{names[p]}]({p})" for p in pages) + f" · [Cedar County Audit (Nebraska)]({CEDAR})\n"
img = lambda f, alt, cap: f"![{alt}]({RAWURL}{f})\n\n*{cap}*\n"
ceil = [c["county"] for c in S["ceiling"]]; floor = [c["county"] for c in S["floor_baseline"]]
fdg = S["floor_dG"]; narrow_inf = [c["county"] for c in S["influential"]]
nonloss = S["nonloss"]
pages = {}
# ---------------- HOME
w = row("Wake")
pages["Home"] = f"""# North Carolina 2022 vs 2026 U.S. Senate Race: ΔG Method

**Version 1, built {BUILT} CST.**

{BANNER}

Method developed by Morissa Benson (CD3 Vice Chair, Nebraska GOP). It began with her [Cedar County Audit]({CEDAR}) on the [Nebraska Election Analysis wiki]({NEWIKI}), the origin of the ΔG method and the reverse step used here. This wiki applies the same arithmetic, unchanged, to all 100 North Carolina counties, using **U.S. Senate** in place of governor (see the box above). Data: NC State Board of Elections (SBOE) election-results files (2022 official; 2026 unofficial) and SBOE voter-registration statistics for each election date; population from the Census Bureau. Compiled 19 Nov 2026.

## Pages

Start with the Cedar County audit in Nebraska. That is where the method began. The North Carolina pages then build up from one county (Wake) to the ten largest counties, to all 100 counties, and to the formula.

1. [Cedar County Audit]({CEDAR}) (Nebraska wiki): where the method started
2. [Bottom-Up Reverse Math](Reverse-Math): Wake → the ten largest counties → all 100 counties, then solved backward for implied extra votes
3. [Locked North Carolina Formula](Locked-North-Carolina-Formula): the equation, a blank fill-in template, and the North Carolina constant (computed from NC data only)
4. [Floor and Ceiling Counties](Floor-and-Ceiling): the counties at the top and bottom, the Texas-style over-ballot check, regional constants and counties narrowed out
5. [Graphs](Graphs): slope chart, ΔG by population, stacked bars, share-vs-gain bars, residual bars, scatter, constant fit, over-ballot check

## Statewide at a glance

| Measure | 2022 (official) | 2026\\* (unofficial) | Change |
|---|---|---|---|
| Democratic registration (election-date SBOE voter_stats) | {n(S['regdem22'])} | {n(S['regdem26'])} | {sn(S['regdem26']-S['regdem22'])} ({sg((S['regdem26']/S['regdem22']-1)*100,1)}%) |
| Total registration | {n(S['regtot22'])} | {n(S['regtot26'])} | {sn(S['regtot26']-S['regtot22'])} |
| Democratic U.S. Senate votes | {n(S['dem22'])} | {n(S['dem26'])}\\* | {sn(S['dem26']-S['dem22'])}\\* ({sg((S['dem26']/S['dem22']-1)*100,1)}%) |
| Republican U.S. Senate votes | {n(S['rep22'])} | {n(S['rep26'])}\\* | {sn(S['rep26']-S['rep22'])}\\* |
| Total ballots cast | {n(S['ballots22'])} | {n(S['ballots26'])}\\* | {sn(S['ballots26']-S['ballots22'])}\\* ({sg((S['ballots26']/S['ballots22']-1)*100,1)}%) |
| Democratic share of ballots (S) | {pc(S['S22'])} | {pc(S['S26'])}\\* | {sg(S['S26']-S['S22'])} pts\\* |
| Democratic registration share (R) | {pc(S['R22'])} | {pc(S['R26'])} | {sg(S['R26']-S['R22'])} pts |
| G = S − R | {sg(S['G22'])} | {sg(S['G26'])}\\* | ΔG {sg(S['dG'])}\\* |

## County results in brief

- **ΔG rose in all {S['dG_pos']} counties.** Median ΔG is {sg(S['dG_median'])}\\*, with a range from {sg(S['dG_min'])}\\* ({fdg[0]['county']}) to {sg(S['dG_max'])}\\* ({ceil[0]}). {S['within3_median']} of 100 counties are within 3 points of the median.
- **Democratic registration share fell in all {S['dR_neg']} counties.** Registered Democrats fell in {S['n_loss']} counties; {', '.join(nonloss)} gained registered Democrats (non-loss counties, raw numbers only).
- **Residual after the registration-loss step** (ΔG minus the registration-share decline), {S['n_loss']} loss counties: median {sg(S['resid_median'])}\\*, positive in all {S['resid_pos']}, range {sg(S['resid_min'])}\\* to {sg(S['resid_max'])}\\*.
- **Solved backward (hypothesis):** the residuals add up to {n(S['implied_sum'])}\\* implied extra votes across the {S['n_loss']} loss counties ({n(S['implied_pooled_loss'])}\\* on the pooled numbers for those counties). These are the votes a hypothesis of added or switched votes would have to account for, not votes shown to be improper. See [Bottom-Up Reverse Math](Reverse-Math).
- **North Carolina constant (NC data only):** ΔG = {S['rev']['c']:.2f} + {S['rev']['k']:.3f} × registration-share drop (all 100 counties, R² {S['rev']['r2']:.2f}). With 7 counties narrowed out: ΔG = {S['rev_narrow']['c']:.2f} + {S['rev_narrow']['k']:.3f} × drop ({S['rev_narrow']['n']} counties, R² {S['rev_narrow']['r2']:.2f}). Regional constants do **not** beat one statewide constant at the 5% level (prosperity zones p = {S['regional_zone_F_p']:.2f}; Mountains / Piedmont / Coastal Plain p = {S['regional_broad_F_p']:.2f}). See [Locked North Carolina Formula](Locked-North-Carolina-Formula).
- **Ceiling and floor:** the five highest ΔG are {', '.join(ceil)}; the floor (most Republican baseline, lowest 2022 Democratic registration share) is {', '.join(floor)}. The lowest ΔG is {fdg[0]['county']} ({sg(fdg[0]['dG'])}\\*). See [Floor and Ceiling Counties](Floor-and-Ceiling).
- **Texas-style over-ballot check:** counties where Democratic + Republican Senate votes exceed total ballots cast: **2022: {S['overballot_count22']}; 2026\\*: {S['overballot_count26']}.** The highest ratio is {S['max_dr_ratio22']['dr_over_ballots22']:.2f}% ({S['max_dr_ratio22']['county']}, 2022) and {S['max_dr_ratio26']['dr_over_ballots26']:.2f}% ({S['max_dr_ratio26']['county']}, 2026\\*). No county's total Senate votes (all candidates) exceed ballots cast in either year.

## Verification

Every county and every figure was checked in **two independent passes** that re-parse the raw SBOE files from scratch (separate scripts, separate parsers, no shared intermediate data). Pass 1: {{VER1}}. Pass 2: {{VER2}}. Cross-source: the 2022 Senate counts match the SBOE precinct results file (results_pct) in all 100 counties; for 2026 they match in 99, and Halifax differs because Halifax updated its results on Nov 16, after the Nov 13 results_pct file was posted (this wiki uses the newer figures). Scripts and logs are in the [repository](https://github.com/mbenson8989/North-Carolina-Election-Analysis).

## Read this before using the numbers

- **This is a Senate race, not a governor race.** Candidate effects differ: 2026 featured a former two-term governor (Cooper) in an open seat. Do not compare these figures directly with governor-race figures from other states without that caveat.
- **The swing was large and close to uniform.** Every county moved toward the Democratic candidate. The ceiling counties are the top of one continuous spread, not a separate group.
- **A residual is not evidence of altered votes.** Candidate choice, crossover voting by Republicans and unaffiliated voters (unaffiliated is now North Carolina's largest registration group: {n(S['reguna26'])} in 2026), turnout differences, and registration-list maintenance all move these numbers. The arithmetic cannot separate them.
- **2026 is unofficial.** Every 2026 figure is marked \\* and will be re-run after the State Board's canvass.
{rel("Reverse-Math", "Locked-North-Carolina-Formula", "Floor-and-Ceiling", "Graphs")}"""
# ---------------- REVERSE MATH
top10 = df.head(10)
def tblrow(r):
    res = sg(r.residual) if r.regloss else "non-loss"
    iv = sn(r.implied_votes) if r.regloss else "n/a"
    return (f"| {r.county} | {n(r.pop2025)} | {n(r.regdem22)} → {n(r.regdem26)} | {n(r.dem22)} → {n(r.dem26)} | {n(r.ballots22)} → {n(r.ballots26)} | "
            f"{pc(r.S22)} → {pc(r.S26)} | {pc(r.R22)} → {pc(r.R26)} | {sg(r.dG)} | {res} | {iv} |")
HDR = "| County | Population | Dem reg 2022 → 2026 | Dem Senate votes 2022 → 2026\\* | Ballots 2022 → 2026\\* | S 2022 → 2026\\* | R 2022 → 2026 | ΔG\\* | Residual\\* | Implied extra votes\\* |\n|---|---|---|---|---|---|---|---|---|---|"
t10 = top10
def pooled(g):
    S22 = g.dem22.sum() / g.ballots22.sum() * 100; S26 = g.dem26.sum() / g.ballots26.sum() * 100
    R22 = g.regdem22.sum() / g.regtot22.sum() * 100; R26 = g.regdem26.sum() / g.regtot26.sum() * 100
    return S22, S26, R22, R26
grp = []
for name, g in (("Ten largest counties", df.head(10)), ("Other 90 counties", df.iloc[10:]), ("All 100 counties", df)):
    S22, S26, R22, R26 = pooled(g); gl = g[g.regloss == 1]
    grp.append(f"| {name} | {len(g)} | {pc(S22)} → {pc(S26)}\\* | {pc(R22)} → {pc(R26)} | {sg(S26-S22)} | {sg(R26-R22)} | {sg((S26-R26)-(S22-R22))} | {sg(g.dG.mean())} ({sg(g.dG.min())} to {sg(g.dG.max())}) | {sn(gl.implied_votes.sum())} ({len(gl)} loss counties) |")
pages["Reverse-Math"] = f"""# Bottom-Up Reverse Math

{BANNER}

The same arithmetic at three levels, from one county up to the whole state. Total-ballots denominator (SBOE "ballots cast" per county), U.S. Senate race.

## Step 1: Wake County

| Step | Value |
|---|---|
| Democratic vote share (S) | {pc(w.S22)} (2022) → {pc(w.S26)}\\* (2026): **{sg(w.dS)} points\\*** |
| Democratic registration share (R) | {pc(w.R22)} → {pc(w.R26)}: **{sg(w.dR)} points** |
| ΔG = vote-share growth − registration-share change | {w.dS:.2f} − ({sg(w.dR)}) = **{sg(w.dG)} points\\*** |
| Reverse step: ΔG − registration-share loss | {w.dG:.2f} − {-w.dR:.2f} = **{w.residual:.2f}** (the residual) |
| Solved backward: implied extra votes | {n(w.dem26)}\\* − {w.S22:.4f}% × {n(w.ballots26)}\\* = **about {sn(w.implied_votes)}\\*** |
| Registration-scaled gap (Nebraska "gap in votes" line, comparison only) | {n(w.dem26)}\\* − {n(w.dem22)} × ({n(w.regdem26)} ÷ {n(w.regdem22)}) = **about {sn(w.regscaled_gap)}\\*** |

## Step 2: the ten largest counties

Largest to smallest population (Census Vintage 2025).

{HDR}
{chr(10).join(tblrow(r) for _, r in t10.iterrows())}

ΔG is positive in all ten ({sg(t10.dG.min())} to {sg(t10.dG.max())}). Johnston is a non-loss county (registered Democrats rose), so it gets raw numbers only. Cabarrus lost a single registered Democrat ({n(row('Cabarrus').regdem22)} → {n(row('Cabarrus').regdem26)}), so by the rule it runs the residual step.

## Step 3: all 100 counties

| Group | Counties | Pooled S\\* | Pooled R | Vote-share growth\\* | Reg-share change | Pooled ΔG\\* | County mean ΔG\\* (range) | Implied extra votes\\* |
|---|---|---|---|---|---|---|---|---|
{chr(10).join(grp)}

ΔG is positive in all 100 counties; Democratic registration share fell in all 100. {S['n_loss']} counties lost registered Democrats and run the residual step; {', '.join(nonloss)} did not.

### All 100 counties, largest to smallest

{HDR}
{chr(10).join(tblrow(r) for _, r in df.iterrows())}

> **Hypothesis label.** Turning the residual into "implied extra votes" (residual × 2026 ballots ÷ 100) and calling them injected or offset votes is a hypothesis the arithmetic cannot test. The same number reflects turnout changes, crossover voting, candidate effects and any other cause. Candidate votes are not turnout.

{img("NC_Wake_residual_steps.png", "Wake residual steps", f"Wake reverse math: ΔG {sg(w.dG)}\\* = {w.dS:.2f}-point vote-share gain\\* + {-w.dR:.2f}-point registration-share loss.")}
{rel("Home", "Locked-North-Carolina-Formula", "Floor-and-Ceiling", "Graphs")}"""
# ---------------- FORMULA
zc = S["zone_constants"]; bc = S["broad_constants"]
zrows = "\n".join(f"| {z} | {v['n']} | {v['c']:+.2f} | {v['k']:.3f} | {v['r2']:.2f} | {sg(v['mean_dG'])} | {sg(v['mean_fit_resid'])} |" for z, v in sorted(zc.items(), key=lambda kv: -kv[1]['mean_fit_resid']))
brows = "\n".join(f"| {z} | {v['n']} | {v['c']:+.2f} | {v['k']:.3f} | {v['r2']:.2f} | {sg(v['mean_dG'])} | {sg(v['mean_fit_resid'])} |" for z, v in bc.items())
f22, f26 = S["fwd22"], S["fwd26"]
pages["Locked-North-Carolina-Formula"] = f"""# Locked North Carolina Formula

{BANNER}

## The equation

- **S** (Democratic vote share) = Democratic U.S. Senate votes ÷ total ballots cast (SBOE county "ballots cast") × 100
- **R** (Democratic registration share) = Democratic registered voters ÷ total registered voters (all parties, SBOE voter_stats for the election date) × 100
- **G** = S − R
- **ΔG** = G(2026) − G(2022) = (S2026 − S2022) − (R2026 − R2022)
- **Reverse step (registration-loss subtraction):** residual = ΔG − (R2022 − R2026) = S2026 − S2022, the vote-share growth left after subtracting the expected loss from the registration-share decline
- **Solved backward, implied extra (injected/offset) votes:** residual × ballots2026 ÷ 100 = D2026 − (S2022 ÷ 100) × ballots2026
- **Registration-scaled gap** (the Nebraska wiki's "gap in votes" line, for comparison only): D2026 − D2022 × (RegDem2026 ÷ RegDem2022)

**Race.** U.S. Senate in both years, substituted for governor because North Carolina had no governor race in 2022 or 2026.

**Denominator.** Total ballots cast as reported by SBOE for each county (2022 official; 2026\\* unofficial). Total Senate votes (all candidates incl. write-ins) were {n(S['sentot22'])} of {n(S['ballots22'])} ballots in 2022 and {n(S['sentot26'])}\\* of {n(S['ballots26'])}\\* in 2026.

## Blank template

| Line | Item | 2022 | 2026* |
|---|---|---|---|
| 1 | Democratic U.S. Senate votes | ______ | ______ |
| 2 | Total ballots cast (SBOE county figure) | ______ | ______ |
| 3 | S = line 1 ÷ line 2 × 100 | ______ | ______ |
| 4 | Democratic registered voters (SBOE voter_stats, election date) | ______ | ______ |
| 5 | Total registered voters, all parties (same file) | ______ | ______ |
| 6 | R = line 4 ÷ line 5 × 100 | ______ | ______ |
| 7 | G = line 3 − line 6 | ______ | ______ |
| 8 | ΔG = G 2026 − G 2022 | | ______ |
| 9 | Registration-share change = R 2026 − R 2022 | | ______ |
| 10 | Did Democratic registration fall? (line 4: 2026 < 2022) | | Yes / No |
| 11 | If yes: residual = line 8 − \\|line 9\\| | | ______ |
| 12 | Implied extra votes = line 1 (2026) − line 3 (2022) ÷ 100 × line 2 (2026) | | ______ |
| 13 | Registration-scaled gap = line 1 (2026) − line 1 (2022) × (line 4 2026 ÷ line 4 2022) | | ______ |

## Rules for using this formula

1. **If a county lost Democratic registration, run the residual step.** Subtract the registration-share loss from ΔG (line 11) and solve backward for implied extra votes (line 12). In North Carolina, {S['n_loss']} of 100 counties lost registered Democrats. The exceptions are {', '.join(f"{c} ({n(row(c).regdem22)} → {n(row(c).regdem26)})" for c in nonloss)}, the **non-loss counties**: report their raw numbers. Their registration *share* still fell, because total registration grew faster.
2. **The starting point is different in every state. Don't assume Nebraska's numbers carry over.** North Carolina's statewide ΔG was {sg(S['dG'])}\\* and its county median {sg(S['dG_median'])}\\*. Compare North Carolina counties with North Carolina's own range, not with another state's.
3. **Always pull out the ceiling and floor counties.** In North Carolina the ceiling county is {ceil[0]} ({sg(S['ceiling'][0]['dG'])}\\*) and the lowest ΔG is {fdg[0]['county']} ({sg(fdg[0]['dG'])}\\*). No North Carolina county has a negative ΔG. See [Floor and Ceiling Counties](Floor-and-Ceiling).

**Terms used in this wiki** (full definitions on [Floor and Ceiling Counties](Floor-and-Ceiling#terminology)):
- **Ceiling counties**: the five largest ΔG ({', '.join(ceil)}).
- **Floor counties**: the most Republican baseline, the five lowest 2022 Democratic registration shares ({', '.join(floor)}).
- **Non-loss counties**: no Democratic registration loss ({', '.join(nonloss)}). Raw numbers only.

## Worked example: Wake

| Line | Item | 2022 | 2026* |
|---|---|---|---|
| 1 | Democratic U.S. Senate votes | {n(w.dem22)} | {n(w.dem26)}* |
| 2 | Total ballots cast | {n(w.ballots22)} | {n(w.ballots26)}* |
| 3 | S | {w.S22:.2f} | {w.S26:.2f}* |
| 4 | Democratic registered | {n(w.regdem22)} | {n(w.regdem26)} |
| 5 | Total registered | {n(w.regtot22)} | {n(w.regtot26)} |
| 6 | R | {w.R22:.2f} | {w.R26:.2f} |
| 7 | G | {sg(w.G22)} | {sg(w.G26)}* |
| 8 | ΔG | | {sg(w.dG)}* |
| 9 | Registration-share change | | {sg(w.dR)} |
| 10 | Registration fell? | | Yes |
| 11 | Residual | | {w.residual:.2f}* |
| 12 | Implied extra votes | | {sn(w.implied_votes)}* |
| 13 | Registration-scaled gap | | {sn(w.regscaled_gap)}* |

## The North Carolina reverse-factoring constant (NC data only)

Recomputed from North Carolina's own 100 counties; no other state's constant is used. Ordinary least squares, each county weighted equally, ΔG against the registration-share drop (R2022 − R2026, points), the same form as the South Dakota constant:

| Fit | Counties | Constant c (SE) | Slope k (SE) | R² | Residual SD (pts) |
|---|---|---|---|---|---|
| **All counties** | {S['rev']['n']} | **{S['rev']['c']:+.2f}** ({S['rev']['c_se']:.2f}) | **{S['rev']['k']:.3f}** ({S['rev']['k_se']:.3f}) | {S['rev']['r2']:.2f} | {S['rev']['rmse']:.2f} |
| Narrowed (7 counties out, see below) | {S['rev_narrow']['n']} | {S['rev_narrow']['c']:+.2f} ({S['rev_narrow']['c_se']:.2f}) | {S['rev_narrow']['k']:.3f} ({S['rev_narrow']['k_se']:.3f}) | {S['rev_narrow']['r2']:.2f} | {S['rev_narrow']['rmse']:.2f} |

**Locked North Carolina formula: ΔG ≈ {S['rev']['c']:.2f} + {S['rev']['k']:.3f} × (registration-share drop)\\*.** 95% CI for c: {S['rev']['c_ci'][0]:.2f} to {S['rev']['c_ci'][1]:.2f}; for k: {S['rev']['k_ci'][0]:.3f} to {S['rev']['k_ci'][1]:.3f}. Read it this way: a county with no registration-share drop would be expected to show a ΔG of about {S['rev']['c']:.1f} points; each point of registration-share drop adds about {S['rev']['k']:.2f} points. The intercept is the statewide swing in Democratic vote share that registration change does not explain. Because k is below 1, ΔG grows less than one-for-one with registration loss.

### Forward surplus fit (for comparison with the other state wikis)

G = m × (R ÷ 100) + b, each year, all 100 counties, equal weight.

| Year | m (SE) | b | R² | Residual SE | Within ±1 / ±2 / ±3 pts | m, b weighted by ballots |
|---|---|---|---|---|---|---|
| 2022 | {f22['m']:.1f} ({f22['m_se']:.1f}) | {f22['b']:+.2f} | {f22['r2']:.2f} | {f22['rse']:.2f} | {f22['within1']:.0%} / {f22['within2']:.0%} / {f22['within3']:.0%} | {f22['m_w']:+.1f}, {f22['b_w']:+.2f} |
| 2026\\* | {f26['m']:.1f} ({f26['m_se']:.1f}) | {f26['b']:+.2f} | {f26['r2']:.2f} | {f26['rse']:.2f} | {f26['within1']:.0%} / {f26['within2']:.0%} / {f26['within3']:.0%} | {f26['m_w']:+.1f}, {f26['b_w']:+.2f} |

The forward fit is weak in North Carolina (registration share explains {f22['r2']:.0%} of county differences in G in 2022 and {f26['r2']:.0%} in 2026\\*), and the slope changes sign when weighted by ballots, so m is not a stable constant here. The change fit ΔG = m × (R2022 ÷ 100) + b gives m = {S['chg']['m']:.2f}, b = {S['chg']['b']:+.2f} (R² {S['chg']['r2']:.2f}).

### Regional constants

Same ΔG-on-drop fit, run within each NC Commerce Prosperity Zone and within a three-region roll-up (Mountains = Western + Northwest zones; Piedmont = Southwest + Piedmont-Triad + North Central; Coastal Plain = Sandhills + Northeast + Southeast). "Mean deviation" is the zone's average distance above (+) or below (−) the single statewide line.

| Prosperity Zone | Counties | c | k | R² | Mean ΔG\\* | Mean deviation from statewide line |
|---|---|---|---|---|---|---|
{zrows}

| Broad region | Counties | c | k | R² | Mean ΔG\\* | Mean deviation from statewide line |
|---|---|---|---|---|---|---|
{brows}

**Result:** regional intercepts do not significantly improve on one statewide constant. Zone intercepts: RMSE {S['rmse_zone']:.2f} vs {S['rmse_single']:.2f}, F-test p = {S['regional_zone_F_p']:.2f} (narrowed set: p = {S['regional_zone_F_p_narrow']:.2f}). Broad regions: RMSE {S['rmse_broad']:.2f}, p = {S['regional_broad_F_p']:.2f}. The Southwest (Charlotte metro) and Piedmont-Triad zones sit about +1.0 and +0.7 points above the line; the Northeast and Southeast sit about −0.9 and −0.6 below. These are leanings, not separate constants. Within-zone slopes vary widely (k from {min(v['k'] for v in zc.values()):.2f} to {max(v['k'] for v in zc.values()):.2f}) on 10 to 17 counties each, so they are not stable enough to lock.

### Counties narrowed out of the fit

| County | Reason |
|---|---|
{chr(10).join(f"| {c['county']} | High influence on the statewide fit (Cook's distance {c['cooks_rev']:.3f}, above 4/n = {S['cooks_threshold']:.2f}); ΔG {sg(c['dG'])}\\*, registration-share drop {c['drop']:.2f} |" for c in S['influential'])}
{chr(10).join(f"| {c} | Non-loss county (gained registered Democrats): raw numbers only, no residual step |" for c in nonloss if c not in narrow_inf)}

Johnston is both influential and non-loss. Narrowing these 7 counties moves the constant only slightly (c {S['rev']['c']:.2f} → {S['rev_narrow']['c']:.2f}, k {S['rev']['k']:.3f} → {S['rev_narrow']['k']:.3f}); they do not drive the result. Orange (Chapel Hill, the lowest ΔG) and Nash (second-highest ΔG) are the two ends that pull hardest.

{img("NC_Constant_DeltaG_vs_Registration_Drop.png", "NC constant fit", "ΔG\\* against registration-share drop, colored by prosperity zone; narrowed counties circled.")}
{rel("Home", "Reverse-Math", "Floor-and-Ceiling", "Graphs")}"""
# ---------------- FLOOR AND CEILING
fc = df[df.county.isin(ceil + floor)].copy()
def fcrow(r):
    g = "Ceiling" if r.county in ceil else "Floor"
    return (f"| {r.county} | {g} | {n(r.pop2025)} | {sg(r.G22)} | {sg(r.G26)} | {sg(r.dG)} | {r.R22:.1f}% → {r.R26:.1f}% | {n(r.regdem22)} → {n(r.regdem26)} ({sg((r.regdem26/r.regdem22-1)*100,1)}%) | "
            f"{n(r.dem22)} → {n(r.dem26)} | {sn(r.implied_votes) if r.regloss else 'n/a'} |")
cz = df[df.county.isin(ceil)]
obrows = "\n".join(f"| {r.county} | {r.dr_over_ballots22:.2f}% | {r.dr_over_ballots26:.2f}% |" for _, r in df.nlargest(5, "dr_over_ballots26").iterrows())
pages["Floor-and-Ceiling"] = f"""# Floor and Ceiling Counties

{BANNER}

## How to read floor and ceiling counties

Look for the pattern at both ends. The ceiling counties are the ones with the highest ΔG; in North Carolina those are {', '.join(ceil)}. The floor counties are the most Republican baseline counties, where there were the fewest Democrats to move.

- **The floor** by ΔG is the single county with the lowest ΔG in the state. In North Carolina that's {fdg[0]['county']}, at {sg(fdg[0]['dG'])}\\*. No North Carolina county has a negative ΔG, so the floor is the smallest rise, not a decline.
- **The ceiling** is the single county with the highest ΔG in the state. In North Carolina that's {ceil[0]}, at {sg(S['ceiling'][0]['dG'])}\\*.

Every state has its own floor and ceiling. Those two extremes set the range the rest of that state's counties fall within.

## Terminology

- **Ceiling counties** are residual counties with the largest positive ΔG: they lost registered Democrats and moved most. {', '.join(f"{c['county']} {sg(c['dG'])}\\*" for c in S['ceiling'])}.
- **Floor counties** are the most Republican baseline: the five lowest 2022 Democratic registration shares. {', '.join(f"{c['county']} {c['R22']:.1f}% (ΔG {sg(c['dG'])}\\*)" for c in S['floor_baseline'])}. By 2022 Democratic vote share instead, the five lowest are {', '.join(f"{c['county']} ({c['S22']:.1f}%)" for c in S['floor_baseline_S'])}. Read by ΔG, the five lowest are {', '.join(f"{c['county']} ({sg(c['dG'])}\\*)" for c in fdg)}; Avery is on both the baseline and ΔG floor lists.
- **Baseline ceiling** (most Democratic registration in 2022): {', '.join(f"{c['county']} {c['R22']:.1f}%" for c in S['baseline_ceiling'])}. Edgecombe is also a ΔG ceiling county.
- **Non-loss counties** had no Democratic registration loss. Raw numbers only, no residual step:
{chr(10).join(f"  - {c}: registered Democrats {n(row(c).regdem22)} → {n(row(c).regdem26)}; Democratic Senate votes {n(row(c).dem22)} → {n(row(c).dem26)}\\*." for c in nonloss)}
- **Registration fell and votes fell too:** {"none in North Carolina. Democratic Senate votes rose in all 100 counties." if not S['dem_votes_fell'] else ', '.join(S['dem_votes_fell'])}
- **Ballots fell, Democratic votes rose** ({len(S['ballots_fell'])} counties): {', '.join(S['ballots_fell'])}. These are flagged for how their votes moved, not because their ΔG is unusual.

## Ceiling and floor detail

Largest to smallest population.

| County | Group | Population | G 2022 | G 2026\\* | ΔG\\* | Dem reg share 2022 → 2026 | Dem reg 2022 → 2026 | Dem Senate votes 2022 → 2026\\* | Implied extra votes\\* |
|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(fcrow(r) for _, r in fc.iterrows())}

**Ceiling profile.**
- **Starting G:** {int((cz.G22 < 0).sum())} of 5 ceiling counties began 2022 with a negative G (Democratic vote share behind registration share) and turned positive in 2026. Statewide, {S['G_flip']} counties flipped from negative to positive; the number of counties with a negative G in 2026 is {S['G_neg26']}.
- **Registration decline:** Democratic registration fell in 5 of 5, by {sg((cz.regdem26/cz.regdem22-1).max()*100,1)}% to {sg((cz.regdem26/cz.regdem22-1).min()*100,1)}%; registration-share drops of {(-cz.dR).min():.2f} to {(-cz.dR).max():.2f} points; their drops rank {', '.join(str(int(x)) for x in sorted(df['drop'].rank(ascending=False)[cz.index]))} of 100 statewide (1 = largest).
- **Region:** all five are in the eastern Coastal Plain / Sandhills or the Nash–Edgecombe corridor (zones: {', '.join(sorted(set(cz.zone)))}). Robeson's 2026 county results were still unofficial at snapshot time.

**Floor profile.** The five floor counties are in the mountains and northwest Piedmont (Mitchell, Avery, Yadkin, Davie) plus Currituck on the northeast coast. All five rose, and {int((df[df.county.isin(floor)].dG < S['dG_median']).sum())} of 5 rose less than the statewide median ΔG ({sg(S['dG_median'])}\\*).

Statewide, ΔG rose in {S['dG_pos']} of 100 counties (median about {sg(S['dG_median'],1)}).

## Texas-style over-ballot check

Any county where Democratic + Republican U.S. Senate votes exceed total ballots cast.

| Year | Counties checked | Counties where D + R > ballots | Highest (D + R) ÷ ballots | Counties where all Senate votes > ballots |
|---|---|---|---|---|
| 2022 (official) | 100 | **{S['overballot_count22']}** | {S['max_dr_ratio22']['dr_over_ballots22']:.2f}% ({S['max_dr_ratio22']['county']}) | {S['senover_count22']} (highest {S['max_sen_ratio22']:.2f}%) |
| 2026\\* (unofficial) | 100 | **{S['overballot_count26']}** | {S['max_dr_ratio26']['dr_over_ballots26']:.2f}% ({S['max_dr_ratio26']['county']}) | {S['senover_count26']} (highest {S['max_sen_ratio26']:.2f}%) |

**No over-ballot anomalies in either year.** Highest five in 2026\\*:

| County | (D + R) ÷ ballots 2022 | 2026\\* |
|---|---|---|
{obrows}

## Regional constants and counties narrowed out

Regional constants do not significantly beat one statewide constant (prosperity zones p = {S['regional_zone_F_p']:.2f}; broad regions p = {S['regional_broad_F_p']:.2f}). Seven counties were narrowed out of the constant fit: {', '.join(narrow_inf)} (high influence, Cook's distance above 4/n) and {', '.join(c for c in nonloss if c not in narrow_inf)} (non-loss). Full tables on [Locked North Carolina Formula](Locked-North-Carolina-Formula#regional-constants).

{img("NC_Ceiling_and_Floor_DeltaG_by_Population.png", "Ceiling and floor counties", "Ceiling (orange) and floor (blue, most Republican baseline) counties in population order, with the state median ΔG.")}
{img("NC_DeltaG_by_Population.png", "Delta-G by population, ceiling and floor marked", "All 100 counties, ΔG in population order. Orange: ceiling (5 largest ΔG). Blue: floor (5 lowest 2022 Democratic registration share). Dashed red line: state median.")}
{rel("Home", "Reverse-Math", "Locked-North-Carolina-Formula", "Graphs")}"""
# ---------------- GRAPHS
pages["Graphs"] = f"""# Graphs

{BANNER}

## 1. County slope chart

{img("NC_Slope_G2022_to_G2026.png", "County slope chart, G 2022 to G 2026", f"Each line is one county, G 2022 to G 2026\\*. G rose in {S['dG_pos']} of 100 counties. Ceiling counties orange, floor counties blue, labeled with ΔG.")}
## 2. Stacked bars: vote-share gain and registration-share loss

{img("NC_Stacked_Share_Reg_Loss_by_Population.png", "Vote-share gain above the line, registration-share loss below", "2022 Democratic share of ballots plus the 2026\\* gain (above the line) and the registration-share change (below the line), all 100 counties in population order.")}
## 3. ΔG by population and ΔG scatter

{img("NC_DeltaG_by_Population.png", "Delta-G for all 100 counties in population order", f"All 100 counties in population order. Lowest ΔG: {fdg[0]['county']} ({sg(fdg[0]['dG'])}\\*). Ceiling: {ceil[0]} ({sg(S['ceiling'][0]['dG'])}\\*).")}
{img("NC_DeltaG_vs_Population_Scatter.png", "Delta-G versus population", f"ΔG\\* against population (log scale), 100 counties (r with log population = {S['r_logpop_dG']:.2f}). Treat as a pattern, not a conclusion.")}
## 4. Vote-share gain bars sorted by 2022 Democratic share

{img("NC_Senate_2022_Dem_share_vs_gain_bar_chart.png", "2022 Democratic share and 2026 gain, sorted by 2022 share", "All 100 counties sorted by 2022 Democratic share of ballots. Blue is the 2022 share; orange is the 2022 to 2026 gain\\*.")}
## 5. Residual after the registration-loss step

{img("NC_Residual_Bars_by_Population.png", "Residual bars by population", f"Residual\\* = ΔG − registration-share drop for the {S['n_loss']} loss counties, population order; non-loss counties ({', '.join(nonloss)}) shown as zero and labeled.")}
## 6. Ceiling and floor counties

{img("NC_Ceiling_and_Floor_DeltaG_by_Population.png", "Ceiling and floor counties", "Ceiling: " + ", ".join(f"{c['county']} {sg(c['dG'])}\\*" for c in S['ceiling']) + ". Floor (most Republican baseline): " + ", ".join(f"{c['county']} {sg(c['dG'])}\\*" for c in S['floor_baseline']) + ".")}
## 7. North Carolina constant

{img("NC_Constant_DeltaG_vs_Registration_Drop.png", "NC constant fit", f"ΔG\\* against registration-share drop: ΔG = {S['rev']['c']:.2f} + {S['rev']['k']:.3f} × drop (all 100) and {S['rev_narrow']['c']:.2f} + {S['rev_narrow']['k']:.3f} × drop (narrowed {S['rev_narrow']['n']}). Colors are prosperity zones.")}
## 8. Texas-style over-ballot check

{img("NC_Over_Ballot_Check_Dem_plus_Rep_vs_Ballots.png", "Over-ballot check", f"(Democratic + Republican Senate votes) ÷ ballots cast, every county, 2022 and 2026\\*. No county reaches 100% (2022: {S['overballot_count22']}, 2026\\*: {S['overballot_count26']}).")}
## 9. Wake County

{img("NC_Wake_residual_steps.png", "Wake residual steps", f"Wake reverse math: ΔG {sg(w.dG)}\\* = {w.dS:.2f}-point vote-share gain\\* + {-w.dR:.2f}-point registration-share loss.")}
{rel("Home", "Reverse-Math", "Floor-and-Ceiling", "Locked-North-Carolina-Formula")}"""
ver = json.load(open(f"{D}/verify_summary.json")) if os.path.exists(f"{D}/verify_summary.json") else {"p1": "PENDING", "p2": "PENDING"}
for k, v in pages.items():
    v = v.replace("{VER1}", ver["p1"]).replace("{VER2}", ver["p2"])
    open(f"{W}/{k}.md", "w").write(v)
print("wiki pages:", list(pages))
