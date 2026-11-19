"""VERIFICATION PASS 1 - independent re-parse of raw NCSBE ENR JSON, voter_stats and Census files
with the Python standard library only (no pandas, no build-pass code or intermediates).
Checks every county and every figure in data/nc_senate_2022_2026_by_population.csv and data/summary.json."""
import json, csv, os, sys
H = os.path.dirname(os.path.abspath(__file__)); RAW = f"{H}/../raw"; DATA = f"{H}/../data"
sys.path.insert(0, H); from zones import COUNTY_ZONE
TOL = 1e-5
ind = {}
def put(c, k, v): ind.setdefault(c, {})[k] = v
for y, d in (("22", "20221108"), ("26", "20261103")):
    for c in json.load(open(f"{RAW}/enr_{d}/county.txt")):
        if c["cid"] == "0": continue
        nm = c["cnm"].upper().strip()
        put(nm, "ballots" + y, int(c["bct"])); put(nm, "enr_regtotal" + y, int(c["rtl"]))
        put(nm, "county_official" + y, 0 if "UNOFFICIAL" in c["tle"] else 1)
        recs = [r for r in json.load(open(f"{RAW}/enr_{d}/results_{c['cid']}.txt")) if "US SENATE" in r["cnm"] and "STATE" not in r["cnm"]]
        dem = sum(int(r["vct"]) for r in recs if r["pty"] == "DEM"); rep = sum(int(r["vct"]) for r in recs if r["pty"] == "REP")
        tot = sum(int(r["vct"]) for r in recs)
        put(nm, "dem" + y, dem); put(nm, "rep" + y, rep); put(nm, "oth" + y, tot - dem - rep); put(nm, "sentot" + y, tot)
    with open(f"{RAW}/voter_stats_{d}.txt") as f:
        hdr = f.readline().rstrip("\n").split("\t"); ic, ip, it = hdr.index("county_desc"), hdr.index("party_cd"), hdr.index("total_voters")
        acc = {}
        for line in f:
            p = line.rstrip("\n").split("\t"); key = (p[ic].upper().strip(), p[ip].strip())
            acc[key] = acc.get(key, 0) + int(p[it])
    for (nm, party), v in acc.items():
        e = ind[nm]
        e["regtot" + y] = e.get("regtot" + y, 0) + v
        k = {"DEM": "regdem", "REP": "regrep", "UNA": "reguna"}.get(party, "regoth") + y
        e[k] = e.get(k, 0) + v
with open(f"{RAW}/co-est2025-alldata.csv", encoding="latin-1") as f:
    for r in csv.DictReader(f):
        if r["STATE"] == "37" and r["COUNTY"] != "000":
            ind[r["CTYNAME"][:-7].upper()]["pop2025"] = int(r["POPESTIMATE2025"])
assert len(ind) == 100
for nm, e in ind.items():
    e["zone"] = COUNTY_ZONE[nm]
    for y in ("22", "26"):
        e["S" + y] = 100 * e["dem" + y] / e["ballots" + y]; e["Srep" + y] = 100 * e["rep" + y] / e["ballots" + y]
        e["R" + y] = 100 * e["regdem" + y] / e["regtot" + y]; e["G" + y] = e["S" + y] - e["R" + y]
        e["dr_over_ballots" + y] = 100 * (e["dem" + y] + e["rep" + y]) / e["ballots" + y]
        e["overballot" + y] = int(e["dem" + y] + e["rep" + y] > e["ballots" + y]); e["senover" + y] = int(e["sentot" + y] > e["ballots" + y])
    e["dS"] = e["S26"] - e["S22"]; e["dR"] = e["R26"] - e["R22"]; e["dG"] = e["G26"] - e["G22"]
    e["regloss"] = int(e["regdem26"] < e["regdem22"])
    e["residual"] = (e["dG"] - (e["R22"] - e["R26"])) if e["regloss"] else None
    e["implied_votes"] = (e["dem26"] - e["S22"] / 100 * e["ballots26"]) if e["regloss"] else None
    e["regscaled_gap"] = e["dem26"] - e["dem22"] * e["regdem26"] / e["regdem22"]
checked = mism = 0; problems = []
rows = list(csv.DictReader(open(f"{DATA}/nc_senate_2022_2026_by_population.csv")))
assert len(rows) == 100, len(rows)
pops = [int(r["pop2025"]) for r in rows]
sorted_ok = pops == sorted(pops, reverse=True)
fields = [k for k in ind["WAKE"] if k in rows[0]]
for r in rows:
    e = ind[r["county"].upper()]
    for k in fields:
        checked += 1; a, b = r[k], e[k]
        if b is None: ok = a == ""
        elif isinstance(b, str): ok = a == b
        else: ok = a != "" and abs(float(a) - b) <= (0 if isinstance(b, int) else TOL)
        if not ok: mism += 1; problems.append((r["county"], k, a, b))
# statewide / summary checks
S = json.load(open(f"{DATA}/summary.json")); sc = sm = 0
def chk(name, got, exp, tol=1e-6):
    global sc, sm; sc += 1
    if (abs(got - exp) > tol) if isinstance(exp, (int, float)) else got != exp: sm += 1; problems.append(("STATE", name, got, exp))
for y, d in (("22", "20221108"), ("26", "20261103")):
    for k in ("dem", "rep", "oth", "sentot", "ballots", "regdem", "regrep", "reguna", "regtot"):
        chk(k + y, S[k + y], sum(e[k + y] for e in ind.values()))
    st = [c for c in json.load(open(f"{RAW}/enr_{d}/county.txt")) if c["cid"] == "0"][0]
    chk("enr_state_ballots" + y, S["ballots" + y], int(st["bct"]))
    st_sen = [r for r in json.load(open(f"{RAW}/enr_{d}/results_0.txt")) if r["cnm"].startswith("US SENATE")]
    chk("enr_state_dem" + y, S["dem" + y], sum(int(r["vct"]) for r in st_sen if r["pty"] == "DEM"))
    chk("enr_state_rep" + y, S["rep" + y], sum(int(r["vct"]) for r in st_sen if r["pty"] == "REP"))
    chk("enr_state_sentot" + y, S["sentot" + y], sum(int(r["vct"]) for r in st_sen))
    chk("S" + y, S["S" + y], 100 * S["dem" + y] / S["ballots" + y]); chk("R" + y, S["R" + y], 100 * S["regdem" + y] / S["regtot" + y])
    chk("overballot_count" + y, S["overballot_count" + y], sum(e["overballot" + y] for e in ind.values()))
    chk("senover_count" + y, S["senover_count" + y], sum(e["senover" + y] for e in ind.values()))
by = sorted(ind.items(), key=lambda kv: -kv[1]["dG"])
chk("ceiling", [c["county"].upper() for c in S["ceiling"]], [k for k, _ in by[:5]])
chk("floor_dG", [c["county"].upper() for c in S["floor_dG"]], [k for k, _ in by[::-1][:5]])
chk("floor_baseline", [c["county"].upper() for c in S["floor_baseline"]], [k for k, _ in sorted(ind.items(), key=lambda kv: kv[1]["R22"])[:5]])
chk("nonloss", sorted(c.upper() for c in S["nonloss"]), sorted(k for k, e in ind.items() if not e["regloss"]))
chk("implied_sum", S["implied_sum"], sum(e["implied_votes"] for e in ind.values() if e["implied_votes"] is not None), 1e-3)
chk("unofficial_counties26", sorted(c.upper() for c in S["unofficial_counties26"]), sorted(k for k, e in ind.items() if not e["county_official26"]))
# least squares constant, closed form
xs = [e["R22"] - e["R26"] for e in ind.values()]; ys = [e["dG"] for e in ind.values()]
mx, my = sum(xs) / 100, sum(ys) / 100
k = sum((x - mx) * (yv - my) for x, yv in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
chk("rev.k", S["rev"]["k"], k, 1e-9); chk("rev.c", S["rev"]["c"], my - k * mx, 1e-9)

# wiki checks (pass 1): statewide table on Home, constant on the formula page, ceiling/floor table rows
wdir = f"{H}/../wiki"; wc = wm = 0
if os.path.isdir(wdir):
    home = open(f"{wdir}/Home.md").read(); form = open(f"{wdir}/Locked-North-Carolina-Formula.md").read(); fc = open(f"{wdir}/Floor-and-Ceiling.md").read()
    tot = {k: sum(e[k] for e in ind.values()) for k in ("regdem22","regdem26","regtot22","regtot26","dem22","dem26","rep22","rep26","ballots22","ballots26")}
    for kk, v in tot.items():
        wc += 1
        if f"{v:,}" not in home: wm += 1; problems.append(("WIKI-Home", kk, v))
    for kk, v in (("S22", 100*tot["dem22"]/tot["ballots22"]), ("S26", 100*tot["dem26"]/tot["ballots26"]), ("R22", 100*tot["regdem22"]/tot["regtot22"]), ("R26", 100*tot["regdem26"]/tot["regtot26"])):
        wc += 1
        if f"{v:.2f}%" not in home: wm += 1; problems.append(("WIKI-Home", kk, v))
    wc += 1
    if f"ΔG = {my - k*mx:.2f} + {k:.3f} × registration-share drop" not in home: wm += 1; problems.append(("WIKI-Home", "constant"))
    wc += 1
    if f"ΔG ≈ {my - k*mx:.2f} + {k:.3f} × (registration-share drop)" not in form: wm += 1; problems.append(("WIKI-Formula", "constant"))
    for c, _ in by[:5]:
        e = ind[c]; wc += 1
        if f"| {c.title()} | Ceiling | {e['pop2025']:,} |" not in fc or f"{e['dem22']:,} → {e['dem26']:,}" not in fc: wm += 1; problems.append(("WIKI-FC", c))
    print(f"PASS 1: wiki checks {wc}; mismatches {wm}")
    sm += wm
print(f"PASS 1: counties {len(rows)}; fields per county {len(fields)}; county-figure checks {checked}; mismatches {mism}")
print(f"PASS 1: statewide/summary checks {sc}; mismatches {sm}; population sort largest-first: {sorted_ok}")
for p in problems[:50]: print("  MISMATCH", p)
sys.exit(0 if (mism == 0 and sm == 0 and sorted_ok) else 1)
