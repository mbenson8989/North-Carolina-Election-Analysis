import json, os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); D = f"{H}/../data"; O = f"{H}/../charts"
df = pd.read_csv(f"{D}/nc_senate_2022_2026_by_population.csv"); S = json.load(open(f"{D}/summary.json"))
ceil = [c["county"] for c in S["ceiling"]]; floor = [c["county"] for c in S["floor_baseline"]]; floordg = S["floor_dG"][0]["county"]
narrow = set(c["county"] for c in S["influential"]) | set(S["nonloss"])
NOTE = "U.S. Senate (NC had no governor race in 2022 or 2026). *2026 unofficial (NCSBE ENR, state canvass pending). Source: NC State Board of Elections."
plt.rcParams.update({"font.size": 9})
def save(fig, name):
    fig.text(0.01, 0.005, NOTE, fontsize=7, color="#555"); fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(f"{O}/{name}", dpi=130); plt.close(fig)
col = lambda c: "#e67e22" if c in ceil else ("#2c7fb8" if c in floor else "#bbbbbb")
# 1 slope
fig, ax = plt.subplots(figsize=(8, 9))
labs_ = []
for _, r in df.iterrows():
    c = col(r.county); lw = 2 if c != "#bbbbbb" else 0.6
    ax.plot([0, 1], [r.G22, r.G26], color=c, lw=lw, alpha=0.9 if lw > 1 else 0.6)
    if lw > 1: labs_.append([r.G26, f"{r.county} ({r.dG:+.2f}*)", c])
labs_.sort(key=lambda t: t[0])
for i in range(1, len(labs_)):
    labs_[i][0] = max(labs_[i][0], labs_[i - 1][0] + 1.1)
for yv, t, c in labs_: ax.text(1.02, yv, t, va="center", fontsize=7, color=c)
ax.axhline(0, color="k", lw=0.6); ax.set_xticks([0, 1]); ax.set_xticklabels(["G 2022", "G 2026*"]); ax.set_xlim(-0.1, 1.45)
ax.set_ylabel("G = Dem share of ballots − Dem registration share (pts)")
ax.set_title(f"North Carolina U.S. Senate: county G, 2022 → 2026* (G rose in {S['dG_pos']} of 100)\nOrange: ceiling (5 largest ΔG). Blue: floor (5 lowest 2022 Dem registration share)")
save(fig, "NC_Slope_G2022_to_G2026.png")
# 2 dG by population
fig, ax = plt.subplots(figsize=(14, 5.5))
ax.bar(range(100), df.dG, color=[col(c) for c in df.county])
ax.axhline(S["dG_median"], color="r", ls="--", lw=1, label=f"median ΔG {S['dG_median']:+.2f}*")
ax.set_xticks(range(100)); ax.set_xticklabels(df.county, rotation=90, fontsize=6); ax.set_ylabel("ΔG* (pts)")
ax.set_title(f"ΔG* for all 100 NC counties, largest population (left) to smallest. Ceiling: {ceil[0]} ({S['ceiling'][0]['dG']:+.2f}*). Lowest ΔG: {floordg} ({S['floor_dG'][0]['dG']:+.2f}*)")
ax.legend(); save(fig, "NC_DeltaG_by_Population.png")
# 3 stacked share + reg loss by population
fig, ax = plt.subplots(figsize=(14, 6))
x = np.arange(100)
ax.bar(x, df.S22, color="#2c7fb8", label="2022 Dem share of ballots")
ax.bar(x, df.dS, bottom=df.S22, color="#e67e22", label="2022→2026* gain in Dem share")
ax.bar(x, df.dR, color="#7f7f7f", label="Dem registration-share change (below line)")
ax.axhline(0, color="k", lw=0.6); ax.set_xticks(x); ax.set_xticklabels(df.county, rotation=90, fontsize=6); ax.set_ylabel("points")
ax.set_title("Democratic vote-share gain (stacked above) and registration-share loss (below the line), population order"); ax.legend(fontsize=8)
save(fig, "NC_Stacked_Share_Reg_Loss_by_Population.png")
# 4 sorted by 2022 share
d4 = df.sort_values("S22").reset_index(drop=True)
fig, ax = plt.subplots(figsize=(14, 6))
ax.bar(x, d4.S22, color="#2c7fb8", label="2022 Dem share of ballots"); ax.bar(x, d4.dS, bottom=d4.S22, color="#e67e22", label="gain to 2026*")
ax.set_xticks(x); ax.set_xticklabels(d4.county, rotation=90, fontsize=6); ax.set_ylabel("% of ballots cast")
ax.set_title("All 100 counties sorted by 2022 Democratic share of ballots; orange is the 2022→2026* gain"); ax.legend(fontsize=8)
save(fig, "NC_Senate_2022_Dem_share_vs_gain_bar_chart.png")
# 5 scatter dG vs population
r = np.corrcoef(np.log10(df.pop2025), df.dG)[0, 1]; S["r_logpop_dG"] = r
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.scatter(df.pop2025, df.dG, c=[col(c) for c in df.county], s=22, edgecolor="k", lw=0.3); ax.set_xscale("log")
for _, rr in df[df.county.isin(ceil + floor + [floordg])].iterrows(): ax.annotate(rr.county, (rr.pop2025, rr.dG), fontsize=7, xytext=(3, 3), textcoords="offset points")
ax.set_xlabel("2025 population (Census Vintage 2025, log scale)"); ax.set_ylabel("ΔG* (pts)")
ax.set_title(f"ΔG* vs population, 100 NC counties (r with log population = {r:.2f})"); save(fig, "NC_DeltaG_vs_Population_Scatter.png")
# 6 ceiling and floor
d6 = df[df.county.isin(ceil + floor)]
fig, ax = plt.subplots(figsize=(9, 4.8))
b = ax.bar(d6.county, d6.dG, color=[col(c) for c in d6.county])
for rect, v in zip(b, d6.dG): ax.text(rect.get_x() + rect.get_width() / 2, v + 0.2, f"{v:+.2f}*", ha="center", fontsize=8)
ax.axhline(S["dG_median"], color="r", ls="--", lw=1, label=f"state median {S['dG_median']:+.2f}*"); ax.legend(fontsize=8)
ax.set_ylabel("ΔG* (pts)"); ax.set_title("Ceiling (orange) and floor (blue, most Republican baseline) counties, population order")
save(fig, "NC_Ceiling_and_Floor_DeltaG_by_Population.png")
# 7 residual bars
fig, ax = plt.subplots(figsize=(14, 5.5))
res = df.residual.fillna(0)
ax.bar(x, res, color=["#bbbbbb" if l == 0 else col(c) if col(c) != "#bbbbbb" else "#6a51a3" for c, l in zip(df.county, df.regloss)])
for i, (c, l) in enumerate(zip(df.county, df.regloss)):
    if l == 0: ax.text(i, 0.2, "non-loss", rotation=90, fontsize=6, ha="center")
ax.set_xticks(x); ax.set_xticklabels(df.county, rotation=90, fontsize=6); ax.set_ylabel("residual* (pts) = ΔG − registration-share drop")
ax.set_title(f"Residual after the registration-loss step, {S['n_loss']} loss counties, population order (median {S['resid_median']:+.2f}*)")
save(fig, "NC_Residual_Bars_by_Population.png")
# 8 over-ballot check
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(x, df.dr_over_ballots22, "o", ms=3, label="2022", color="#2c7fb8"); ax.plot(x, df.dr_over_ballots26, "s", ms=3, label="2026*", color="#e67e22")
ax.axhline(100, color="r", lw=1, label="100% = Dem + Rep equals ballots cast"); ax.set_ylim(90, 101)
ax.set_xticks(x); ax.set_xticklabels(df.county, rotation=90, fontsize=6); ax.set_ylabel("(Dem + Rep Senate votes) ÷ ballots cast, %")
ax.set_title(f"Texas-style over-ballot check: counties above 100%: 2022 = {S['overballot_count22']}, 2026* = {S['overballot_count26']}"); ax.legend(fontsize=8)
save(fig, "NC_Over_Ballot_Check_Dem_plus_Rep_vs_Ballots.png")
# 9 constant fit
zcol = dict(zip(sorted(df.zone.unique()), plt.cm.tab10.colors))
fig, ax = plt.subplots(figsize=(9, 6))
for z, g in df.groupby("zone"): ax.scatter(g["drop"], g.dG, color=zcol[z], s=22, label=z, edgecolor="k", lw=0.3)
nn = df[df.county.isin(narrow)]
ax.scatter(nn["drop"], nn.dG, facecolor="none", edgecolor="r", s=90, lw=1.2, label="narrowed out")
for _, rr in nn.iterrows(): ax.annotate(rr.county, (rr["drop"], rr.dG), fontsize=7, xytext=(4, -8), textcoords="offset points")
xx = np.linspace(df["drop"].min() - 0.3, df["drop"].max() + 0.3, 10)
ax.plot(xx, S["rev"]["c"] + S["rev"]["k"] * xx, "k-", label=f"all 100: ΔG = {S['rev']['c']:.2f} + {S['rev']['k']:.3f} × drop")
ax.plot(xx, S["rev_narrow"]["c"] + S["rev_narrow"]["k"] * xx, "k--", label=f"narrowed {S['rev_narrow']['n']}: ΔG = {S['rev_narrow']['c']:.2f} + {S['rev_narrow']['k']:.3f} × drop")
ax.set_xlabel("Democratic registration-share drop, R2022 − R2026 (pts)"); ax.set_ylabel("ΔG* (pts)")
ax.set_title("North Carolina reverse-factoring constant: ΔG* against registration-share drop"); ax.legend(fontsize=7, ncol=2)
save(fig, "NC_Constant_DeltaG_vs_Registration_Drop.png")
# 10 Wake residual steps
w = df[df.county == "Wake"].iloc[0]
fig, ax = plt.subplots(figsize=(8, 4.8))
vals = [w.dS, -w.dR, w.dG, w.residual]; labs = ["Vote-share growth*\nS26 − S22", "Registration-share\nloss R22 − R26", "ΔG*", "Residual*\nΔG − reg-share loss"]
b = ax.bar(labs, vals, color=["#e67e22", "#7f7f7f", "#2c7fb8", "#6a51a3"])
for rect, v in zip(b, vals): ax.text(rect.get_x() + rect.get_width() / 2, v + 0.2, f"{v:+.2f}", ha="center")
ax.set_ylabel("points"); ax.set_title(f"Wake County reverse math: ΔG {w.dG:+.2f}* = {w.dS:.2f}-pt vote-share gain* + {-w.dR:.2f}-pt registration-share loss")
save(fig, "NC_Wake_residual_steps.png")
json.dump(S, open(f"{D}/summary.json", "w"), indent=1, default=float)
print("charts ok", sorted(os.listdir(O)))

# share version S = m*(D/100)+b, from share_fit.json (raw-file recompute)
SF = json.load(open(f"{D}/share_fit.json"))
fig, ax = plt.subplots(figsize=(11, 6.5))
for y, col, mk in (("22", "#1f4e9c", "o"), ("26", "#d9822b", "^")):
    f = SF[f"y20{y}"]; xs = [v[f"D{y}"] for v in SF["county"].values()]; ys = [v[f"S{y}"] for v in SF["county"].values()]
    ax.scatter(xs, ys, s=18, c=col, marker=mk, alpha=.75, label=f"20{y}{'*' if y == '26' else ''} counties")
    xx = np.linspace(min(xs), max(xs), 50)
    ax.plot(xx, f["m"] * xx / 100 + f["b"], c=col, lw=2, label=f"20{y}{'*' if y == '26' else ''}: S = {f['m']:.2f} × (D/100) + {f['b']:.2f}  (R² {f['r2']:.2f}, mean |resid| {f['mae']:.2f})")
for c in ("Orange", "Durham", "Wake"):
    v = SF["county"][c]; ax.annotate(c, (v["D26"], v["S26"]), fontsize=8, xytext=(4, 2), textcoords="offset points")
ax.set_xlabel("D = Democratic registration share (%)"); ax.set_ylabel("S = Dem share of ballots − Dem registration share (pts)")
ax.set_title("North Carolina share version, all 100 counties, U.S. Senate (2026* unofficial)"); ax.legend(fontsize=8)
save(fig, "NC_Share_Version_S_vs_D.png")
