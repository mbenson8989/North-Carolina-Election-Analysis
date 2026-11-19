"""VERIFICATION PASS 2 - a second, independent re-parse of the raw NCSBE files from scratch.
Different parsers from pass 1: regular expressions over the raw ENR text (no json module), awk over voter_stats,
manual line split of the Census file; recomputes every figure with decimal arithmetic and compares to the
published CSV and summary.json. Also cross-checks the Senate vote counts against two other SBOE renderings
(results_pct zip files; 2022 results_precinct_sort AllCounties.txt)."""
import re, os, sys, subprocess, json
from decimal import Decimal as Dm, getcontext
getcontext().prec = 40
H = os.path.dirname(os.path.abspath(__file__)); RAW = f"{H}/../raw"; DATA = f"{H}/../data"
OBJ = re.compile(r"\{[^{}]*\}")
def fld(o, k):
    m = re.search(r'"%s":"([^"]*)"' % k, o); return m.group(1)
V = {}
for y, d in (("22", "20221108"), ("26", "20261103")):
    txt = open(f"{RAW}/enr_{d}/county.txt").read()
    for o in OBJ.findall(txt):
        cid = int(fld(o, "cid"))
        if cid == 0: continue
        nm = fld(o, "cnm").strip().upper(); e = V.setdefault(nm, {})
        e["ballots" + y] = int(fld(o, "bct")); e["official" + y] = int(not fld(o, "tle").split(" ")[1].startswith("UN"))
        res = open(f"{RAW}/enr_{d}/results_{cid}.txt").read()
        dem = rep = tot = 0
        for r in OBJ.findall(res):
            if not re.match(r"US SENATE \(VOTE FOR 1\)$", fld(r, "cnm")): continue
            v = int(fld(r, "vct")); tot += v; p = fld(r, "pty")
            dem += v if p == "DEM" else 0; rep += v if p == "REP" else 0
        e["dem" + y], e["rep" + y], e["sentot" + y] = dem, rep, tot
    awk = r"""BEGIN{FS="\t"} NR>1{c=toupper($1); gsub(/^ +| +$/,"",c); p=$6; gsub(/ /,"",p); if(p!="DEM"&&p!="REP"&&p!="UNA")p="OTH"; s[c"|"p]+=$11; t[c]+=$11} END{for(k in s)print k"|"s[k]; for(k in t)print k"|TOT|"t[k]}"""
    out = subprocess.run(["awk", awk, f"{RAW}/voter_stats_{d}.txt"], capture_output=True, text=True, check=True).stdout
    for line in out.splitlines():
        c, p, v = line.split("|"); V[c][f"reg{p.lower()}{y}"] = int(v)
for line in open(f"{RAW}/co-est2025-alldata.csv", encoding="latin-1").read().splitlines()[1:]:
    p = line.split(",")
    if p[3] == "37" and p[4] != "000": V[p[6].replace(" County", "").upper()]["pop"] = int(p[13])
assert len(V) == 100
# published data
lines = open(f"{DATA}/nc_senate_2022_2026_by_population.csv").read().splitlines()
hdr = lines[0].split(","); pub = [dict(zip(hdr, l.split(","))) for l in lines[1:]]
checked = mism = 0; probs = []
def cmp(cty, k, exp, tol=Dm("0.000001")):
    global checked, mism; checked += 1
    got = pub_row.get(k, "")
    if exp is None: ok = got == ""
    else: ok = got != "" and abs(Dm(got) - Dm(exp)) <= tol
    if not ok: mism += 1; probs.append((cty, k, got, exp))
H100 = Dm(100)
for pub_row in pub:
    c = pub_row["county"].upper(); e = V[c]
    cmp(c, "pop2025", e["pop"], 0)
    for y in ("22", "26"):
        D_, R_, T_, B_ = e["dem" + y], e["rep" + y], e["sentot" + y], e["ballots" + y]
        for k, v in (("dem", D_), ("rep", R_), ("oth", T_ - D_ - R_), ("sentot", T_), ("ballots", B_), ("regdem", e["regdem" + y]),
                     ("regrep", e["regrep" + y]), ("reguna", e["reguna" + y]), ("regoth", e["regoth" + y]), ("regtot", e["regtot" + y]),
                     ("county_official", e["official" + y]), ("overballot", int(D_ + R_ > B_)), ("senover", int(T_ > B_))):
            cmp(c, k + y, v, 0)
        S = Dm(D_) / B_ * H100; Rr = Dm(e["regdem" + y]) / e["regtot" + y] * H100
        e["S" + y], e["R" + y] = S, Rr
        cmp(c, "S" + y, S); cmp(c, "R" + y, Rr); cmp(c, "G" + y, S - Rr); cmp(c, "Srep" + y, Dm(R_) / B_ * H100)
        cmp(c, "dr_over_ballots" + y, Dm(D_ + R_) / B_ * H100)
    dG = (e["S26"] - e["R26"]) - (e["S22"] - e["R22"]); e["dG"] = dG
    cmp(c, "dS", e["S26"] - e["S22"]); cmp(c, "dR", e["R26"] - e["R22"]); cmp(c, "dG", dG)
    loss = e["regdem26"] < e["regdem22"]; e["loss"] = loss
    cmp(c, "regloss", int(loss), 0)
    cmp(c, "residual", (dG - (e["R22"] - e["R26"])) if loss else None)
    iv = (Dm(e["dem26"]) - e["S22"] / H100 * e["ballots26"]) if loss else None; e["iv"] = iv
    cmp(c, "implied_votes", iv, Dm("0.0001"))
    cmp(c, "regscaled_gap", Dm(e["dem26"]) - Dm(e["dem22"]) * e["regdem26"] / e["regdem22"], Dm("0.0001"))
# summary
Sm = json.load(open(f"{DATA}/summary.json")); sc = sm = 0
def sch(name, got, exp, tol=1e-6):
    global sc, sm; sc += 1
    bad = (abs(float(got) - float(exp)) > tol) if not isinstance(exp, (list, str)) else got != exp
    if bad: sm += 1; probs.append(("STATE", name, got, exp))
for y in ("22", "26"):
    for k in ("dem", "rep", "sentot", "ballots", "regdem", "regrep", "reguna", "regtot"):
        sch(k + y, Sm[k + y], sum(e[k + y] for e in V.values()))
    sch("S" + y, Sm["S" + y], Dm(Sm["dem" + y]) / Sm["ballots" + y] * 100)
    sch("G" + y, Sm["G" + y], Dm(Sm["dem" + y]) / Sm["ballots" + y] * 100 - Dm(Sm["regdem" + y]) / Sm["regtot" + y] * 100)
    sch("overballot_count" + y, Sm["overballot_count" + y], sum(1 for e in V.values() if e["dem" + y] + e["rep" + y] > e["ballots" + y]))
rk = sorted(V, key=lambda c: V[c]["dG"])
sch("ceiling", [x["county"].upper() for x in Sm["ceiling"]], rk[::-1][:5]); sch("floor_dG", [x["county"].upper() for x in Sm["floor_dG"]], rk[:5])
sch("floor_baseline", [x["county"].upper() for x in Sm["floor_baseline"]], sorted(V, key=lambda c: V[c]["R22"])[:5])
sch("dG_median", Sm["dG_median"], sorted(V[c]["dG"] for c in V)[49:51][0] / 2 + sorted(V[c]["dG"] for c in V)[49:51][1] / 2, 1e-5)
sch("implied_sum", Sm["implied_sum"], sum(e["iv"] for e in V.values() if e["iv"] is not None), 1e-3)
sch("n_loss", Sm["n_loss"], sum(1 for e in V.values() if e["loss"]))
print(f"PASS 2: counties {len(pub)}; county-figure checks {checked}; mismatches {mism}")
print(f"PASS 2: statewide/summary checks {sc}; mismatches {sm}")
for p in probs[:50]: print("  MISMATCH", p)

# wiki check: every county row of the all-100 table on Reverse-Math, rebuilt from this pass's own numbers
wk = f"{H}/../wiki/Reverse-Math.md"; wchecked = wmism = 0
if os.path.exists(wk):
    txt = open(wk).read().split("### All 100 counties")[1]
    def fm(v, d=2): return ("+" if v >= 0 else "\u2212") + f"{abs(v):.{d}f}"
    def fi(v): return f"{int(v):,}"
    for c, e in V.items():
        tit = c.title().replace("Mcdowell", "McDowell")
        q = lambda v: v.quantize(Dm("0.01"))
        res = fm(float(q(e["dG"] - (e["R22"] - e["R26"])))) if e["loss"] else "non-loss"
        ivs = (("+" if e["iv"] >= 0 else "\u2212") + f"{abs(int(e['iv'].quantize(Dm('1')))):,}") if e["loss"] else "n/a"
        exp = (f"| {tit} | {fi(e['pop'])} | {fi(e['regdem22'])} \u2192 {fi(e['regdem26'])} | {fi(e['dem22'])} \u2192 {fi(e['dem26'])} | "
               f"{fi(e['ballots22'])} \u2192 {fi(e['ballots26'])} | {float(q(e['S22'])):.2f}% \u2192 {float(q(e['S26'])):.2f}% | "
               f"{float(q(e['R22'])):.2f}% \u2192 {float(q(e['R26'])):.2f}% | {fm(float(q(e['dG'])))} | {res} | {ivs} |")
        wchecked += 1
        if exp not in txt: wmism += 1; probs.append(("WIKI", c, exp))
    print(f"PASS 2: wiki Reverse-Math all-county rows checked {wchecked} (10 figures each); mismatches {wmism}")
    for p_ in probs[-5:]:
        if p_[0] == "WIKI": print("  MISMATCH", p_)
mism += wmism
# cross-source (other SBOE renderings of the same results)
xs = {}
for y, f in (("22", "results_pct_20221108.txt"), ("26", "results_pct_20261103.txt")):
    agg = {}
    with open(f"{RAW}/{f}") as fh:
        fh.readline()
        for line in fh:
            p = line.split("\t")
            if p[5] != "US SENATE": continue
            key = (p[0].upper(), p[7].strip()); agg[key] = agg.get(key, 0) + int(p[13])
    diffs = []
    for c, e in V.items():
        dd, rr, tt = agg.get((c, "DEM"), 0), agg.get((c, "REP"), 0), sum(v for (cc, _), v in agg.items() if cc == c)
        for k, a, b in (("dem", dd, e["dem" + y]), ("rep", rr, e["rep" + y]), ("sentot", tt, e["sentot" + y])):
            if a != b: diffs.append((c, k + y, a, b))
    xs["results_pct" + y] = diffs
    print(f"CROSS-SOURCE results_pct 20{y}: 300 county vote checks; differences {len(diffs)} {diffs}")
agg = {}
if not os.path.exists(f"{RAW}/AllCounties.txt"):
    print("CROSS-SOURCE 2022 AllCounties: skipped (file not present; download from https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/results_precinct_sort/AllCounties.txt)"); sys.exit(0 if mism == 0 and sm == 0 else 1)
with open(f"{RAW}/AllCounties.txt") as fh:
    fh.readline()
    for line in fh:
        p = line.split("\t")
        if p[6] != "US SENATE" or p[3] not in ("STD", "WRI"): continue
        key = (p[1].upper(), p[13].strip().upper()); agg[key] = agg.get(key, 0) + int(p[18])
d2 = [(c, k, a, b) for c, e in V.items() for k, a, b in (("dem22", agg.get((c, "DEM"), 0), e["dem22"]), ("rep22", agg.get((c, "REP"), 0), e["rep22"]),
      ("sentot22", sum(v for (cc, _), v in agg.items() if cc == c), e["sentot22"])) if a != b]
sd = sum(v for (c, p), v in agg.items() if p == "DEM"); sr = sum(v for (c, p), v in agg.items() if p == "REP")
print(f"CROSS-SOURCE 2022 results_precinct_sort AllCounties (informational; absentee/early votes re-sorted to home precincts, not the canvass): "
      f"300 county vote checks; differences {len(d2)}; statewide DEM {sd:,} vs canvass {sum(e['dem22'] for e in V.values()):,}, REP {sr:,} vs {sum(e['rep22'] for e in V.values()):,}")
sys.exit(0 if mism == 0 and sm == 0 else 1)
