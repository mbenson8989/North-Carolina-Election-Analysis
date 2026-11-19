"""Constants, regional test, narrowing, floor/ceiling, over-ballot. Reads build-pass CSV; writes data/summary.json."""
import json, os
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
D = os.path.join(os.path.dirname(__file__), "..", "data")
df = pd.read_csv(f"{D}/nc_senate_2022_2026_by_population.csv")
S = json.load(open(f"{D}/summary_base.json"))
df["drop"] = df["R22"] - df["R26"]          # registration-share decline, points
n = len(df)

def fit(formula, data):
    m = smf.ols(formula, data=data).fit()
    return m

# 1. NC reverse-factoring constant: dG = c + k * drop   (same form as the South Dakota constant)
rev = fit("dG ~ drop", df)
infl = rev.get_influence(); cooks = infl.cooks_distance[0]
df["cooks_rev"] = cooks
S["rev"] = dict(k=rev.params["drop"], k_se=rev.bse["drop"], c=rev.params["Intercept"], c_se=rev.bse["Intercept"],
               r2=rev.rsquared, rmse=float(np.sqrt(rev.mse_resid)), n=n,
               k_ci=list(rev.conf_int().loc["drop"]), c_ci=list(rev.conf_int().loc["Intercept"]))
# 2. forward surplus fit G = m*(R/100) + b each year (equal weight) and ballots-weighted
for y in ("22", "26"):
    d2 = df.assign(Rf=df[f"R{y}"] / 100, G=df[f"G{y}"])
    f = fit("G ~ Rf", d2)
    w = smf.wls("G ~ Rf", data=d2, weights=d2[f"ballots{y}"]).fit()
    resid = f.resid.abs()
    S[f"fwd{y}"] = dict(m=f.params["Rf"], m_se=f.bse["Rf"], b=f.params["Intercept"], r2=f.rsquared,
                       rse=float(np.sqrt(f.mse_resid)), m_w=w.params["Rf"], b_w=w.params["Intercept"],
                       within1=float((resid <= 1).mean()), within2=float((resid <= 2).mean()), within3=float((resid <= 3).mean()))
# change fit: dG on 2022 R
chg = fit("dG ~ Rf", df.assign(Rf=df["R22"] / 100))
S["chg"] = dict(m=chg.params["Rf"], b=chg.params["Intercept"], r2=chg.rsquared)
# 3. regional constants: zone-specific intercepts with common slope
regz = fit("dG ~ drop + C(zone)", df)
regb = fit("dG ~ drop + C(region)", df)
S["regional_zone_F_p"] = float(anova_lm(rev, regz)["Pr(>F)"][1])
S["regional_broad_F_p"] = float(anova_lm(rev, regb)["Pr(>F)"][1])
S["rmse_single"] = float(np.sqrt(rev.mse_resid)); S["rmse_zone"] = float(np.sqrt(regz.mse_resid)); S["rmse_broad"] = float(np.sqrt(regb.mse_resid))
zc = {}
for z, g in df.groupby("zone"):
    fz = fit("dG ~ drop", g) if len(g) >= 5 else None
    zc[z] = dict(n=len(g), c=fz.params["Intercept"], k=fz.params["drop"], r2=fz.rsquared,
                 mean_dG=g.dG.mean(), median_residual=g.residual.median(), mean_fit_resid=float(rev.resid[g.index].mean()))
S["zone_constants"] = zc
bc = {}
for z, g in df.groupby("region"):
    fz = fit("dG ~ drop", g)
    bc[z] = dict(n=len(g), c=fz.params["Intercept"], k=fz.params["drop"], r2=fz.rsquared, mean_dG=g.dG.mean(),
                 mean_fit_resid=float(rev.resid[g.index].mean()))
S["broad_constants"] = bc
# 4. narrowing: Cook's distance > 4/n in the reverse fit, plus non-loss counties (raw numbers only)
thr = 4 / n
infl_c = df.loc[df.cooks_rev > thr, ["county", "cooks_rev", "dG", "drop"]].sort_values("cooks_rev", ascending=False)
nonloss = df.loc[df.regloss == 0, "county"].tolist()
S["cooks_threshold"] = thr
S["influential"] = infl_c.to_dict("records")
S["nonloss"] = nonloss
narrow = set(infl_c.county) | set(nonloss)
dn = df[~df.county.isin(narrow)]
nr = fit("dG ~ drop", dn)
S["rev_narrow"] = dict(k=nr.params["drop"], k_se=nr.bse["drop"], c=nr.params["Intercept"], c_se=nr.bse["Intercept"],
                      r2=nr.rsquared, rmse=float(np.sqrt(nr.mse_resid)), n=len(dn))
regzn = fit("dG ~ drop + C(zone)", dn)
S["regional_zone_F_p_narrow"] = float(anova_lm(nr, regzn)["Pr(>F)"][1])
S["rmse_zone_narrow"] = float(np.sqrt(regzn.mse_resid))
# 5. floor / ceiling
S["ceiling"] = df.nlargest(5, "dG")[["county", "dG"]].to_dict("records")
S["floor_dG"] = df.nsmallest(5, "dG")[["county", "dG"]].to_dict("records")
S["floor_baseline"] = df.nsmallest(5, "R22")[["county", "R22", "dG"]].to_dict("records")
S["floor_baseline_S"] = df.nsmallest(5, "S22")[["county", "S22"]].to_dict("records")
S["baseline_ceiling"] = df.nlargest(5, "R22")[["county", "R22", "dG"]].to_dict("records")
S["dG_median"] = df.dG.median(); S["dG_min"] = df.dG.min(); S["dG_max"] = df.dG.max()
S["dG_pos"] = int((df.dG > 0).sum())
S["resid_median"] = df.residual.median(); S["resid_min"] = df.residual.min(); S["resid_max"] = df.residual.max()
S["resid_pos"] = int((df.residual > 0).sum()); S["n_loss"] = int(df.regloss.sum())
S["implied_sum"] = float(df.implied_votes.sum())
S["implied_pooled_loss"] = float(df.loc[df.regloss == 1, "dem26"].sum() - df.loc[df.regloss == 1, "dem22"].sum() / df.loc[df.regloss == 1, "ballots22"].sum() * df.loc[df.regloss == 1, "ballots26"].sum())
S["dem_votes_fell"] = df.loc[df.dem26 < df.dem22, "county"].tolist()
S["ballots_fell"] = df.loc[df.ballots26 < df.ballots22, "county"].tolist()
S["G_neg22"] = int((df.G22 < 0).sum()); S["G_neg26"] = int((df.G26 < 0).sum())
S["G_flip"] = int(((df.G22 < 0) & (df.G26 >= 0)).sum())
S["within3_median"] = int(((df.dG - df.dG.median()).abs() <= 3).sum())
S["dR_neg"] = int((df.dR < 0).sum())
for y in ("22", "26"):
    S[f"max_dr_ratio{y}"] = df.loc[df[f"dr_over_ballots{y}"].idxmax(), ["county", f"dr_over_ballots{y}"]].to_dict()
    S[f"senover_count{y}"] = int(df[f"senover{y}"].sum())
    S[f"max_sen_ratio{y}"] = float((df[f"sentot{y}"] / df[f"ballots{y}"] * 100).max())
json.dump(S, open(f"{D}/summary.json", "w"), indent=1, default=float)
df.to_csv(f"{D}/nc_senate_2022_2026_by_population.csv", index=False, float_format="%.10f")
print(json.dumps({k: v for k, v in S.items() if k not in ("zone_constants",)}, indent=1, default=float))
print(json.dumps(S["zone_constants"], indent=1, default=float))
