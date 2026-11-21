"""Share version of the locked formula, recomputed from the RAW SBOE files (reuses only the raw parser
pattern of verify_pdf_raw.py; no CSV/summary inputs).  S = m x (D/100) + b, where
S = Democratic surplus G = Dem Senate votes / ballots x 100 - Dem registration share (points), and
D = Democratic registration share (points), same election year (sister-state definition: Kansas/Texas/Michigan).
Ordinary least squares, each county weighted equally."""
import re, os, csv, json
from fractions import Fraction as Fr
H = os.path.dirname(os.path.abspath(__file__)); RAW = f"{H}/../raw"
V = {}
for y, d in (("22", "20221108"), ("26", "20261103")):
    for obj in re.findall(r"\{[^{}]*\}", open(f"{RAW}/enr_{d}/county.txt").read()):
        g = dict(re.findall(r'"(\w+)":"([^"]*)"', obj))
        if g["cid"] == "0": continue
        e = V.setdefault(g["cnm"].strip().title().replace("Mcdowell", "McDowell"), {})
        e["B" + y] = int(g["bct"]); dem = 0
        for o in re.findall(r"\{[^{}]*\}", open(f"{RAW}/enr_{d}/results_{g['cid']}.txt").read()):
            h = dict(re.findall(r'"(\w+)":"([^"]*)"', o))
            if h["cnm"] == "US SENATE (VOTE FOR 1)" and h["pty"] == "DEM": dem += int(h["vct"])
        e["D" + y] = dem
    with open(f"{RAW}/voter_stats_{d}.txt", newline="") as f:
        for r in csv.reader(f, delimiter="\t"):
            if r[0] == "county_desc": continue
            e = V[r[0].strip().title().replace("Mcdowell", "McDowell")]
            n = int(r[10]); e["T" + y] = e.get("T" + y, 0) + n
            if r[5].strip() == "DEM": e["RD" + y] = e.get("RD" + y, 0) + n
assert len(V) == 100
for e in V.values():
    for y in ("22", "26"):
        e["Dsh" + y] = Fr(100 * e["RD" + y], e["T" + y]); e["S" + y] = Fr(100 * e["D" + y], e["B" + y]) - e["Dsh" + y]
def ols(pts):
    n = len(pts); xs = [x / 100 for x, _ in pts]; ys = [s for _, s in pts]
    mx = sum(xs) / n; my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs); sxy = sum((x - mx) * (s - my) for x, s in zip(xs, ys))
    m = sxy / sxx; b = my - m * mx; res = [s - (m * x + b) for x, s in zip(xs, ys)]
    sse = sum(r * r for r in res); sst = sum((s - my) ** 2 for s in ys)
    return dict(n=n, m=float(m), b=float(b), r2=float(1 - sse / sst), mae=float(sum(abs(r) for r in res) / n),
                rse=float((sse / (n - 2))) ** 0.5, m_se=float(sse / (n - 2) / sxx) ** 0.5), res
NARROW = {"Nash", "Orange", "Warren", "Cabarrus", "Johnston", "Brunswick", "Harnett"}
out = {}; names = sorted(V)
for key, sel, yrs in (("y2022", names, ["22"]), ("y2026", names, ["26"]), ("pooled", names, ["22", "26"]),
                      ("y2026_narrow93", [c for c in names if c not in NARROW], ["26"]),
                      ("y2022_narrow93", [c for c in names if c not in NARROW], ["22"])):
    pts = [(V[c]["Dsh" + y], V[c]["S" + y]) for y in yrs for c in sel]; lab = [(c, y) for y in yrs for c in sel]
    f, res = ols(pts)
    order = sorted(zip(lab, res), key=lambda t: -abs(t[1]))
    f["max_res"] = [dict(county=c, year="20" + y, res=float(r)) for (c, y), r in order[:5]]
    f["top_pos"] = [dict(county=c, res=float(r)) for (c, y), r in sorted(zip(lab, res), key=lambda t: -t[1])[:3]]
    f["top_neg"] = [dict(county=c, res=float(r)) for (c, y), r in sorted(zip(lab, res), key=lambda t: t[1])[:3]]
    f["within3"] = sum(abs(r) <= 3 for r in res) / len(res)
    out[key] = f
w = V["Wake"]; f = out["y2026"]
out["wake"] = dict(D26=float(w["Dsh26"]), S26=float(w["S26"]), fit=f["m"] * float(w["Dsh26"]) / 100 + f["b"])
out["wake"]["res"] = out["wake"]["S26"] - out["wake"]["fit"]
out["county"] = {c: dict(D22=float(V[c]["Dsh22"]), S22=float(V[c]["S22"]), D26=float(V[c]["Dsh26"]), S26=float(V[c]["S26"])) for c in names}
json.dump(out, open(f"{H}/../data/share_fit.json", "w"), indent=1)
for k in ("y2022", "y2026", "pooled", "y2026_narrow93", "y2022_narrow93"):
    f = out[k]; print(k, f"n={f['n']} m={f['m']:.4f} (SE {f['m_se']:.2f}) b={f['b']:.4f} R2={f['r2']:.4f} MAE={f['mae']:.4f} RSE={f['rse']:.4f} within3={f['within3']:.2f}", "max:", [(x['county'], x['year'], round(x['res'], 2)) for x in f['max_res'][:3]])
print("wake", out["wake"])
