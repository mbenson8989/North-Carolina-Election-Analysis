"""Build pass: NC U.S. Senate 2022 vs 2026, all 100 counties, from raw NCSBE files.
Sources (all under raw/): ENR JSON snapshots enr_YYYYMMDD/{county.txt,results_N.txt},
voter_stats_YYYYMMDD.txt (registration as of election day), Census co-est2025-alldata.csv."""
import json, csv, os, collections
import pandas as pd
from zones import COUNTY_ZONE, BROAD
RAW = os.path.join(os.path.dirname(__file__), "..", "raw")
OUT = os.path.join(os.path.dirname(__file__), "..", "data")
YEARS = {"22": "20221108", "26": "20261103"}

def enr(d):
    cty = json.load(open(f"{RAW}/enr_{d}/county.txt"))
    meta = {c["cid"]: c for c in cty}
    rows = {}
    for cid in range(1, 101):
        m = meta[str(cid)]
        name = m["cnm"].strip().upper()
        dem = rep = oth = 0; ncand = 0
        for x in json.load(open(f"{RAW}/enr_{d}/results_{cid}.txt")):
            if not x["cnm"].startswith("US SENATE"):
                continue
            v = int(x["vct"]); ncand += 1
            if x["pty"] == "DEM": dem += v
            elif x["pty"] == "REP": rep += v
            else: oth += v
        assert ncand >= 4, (d, name)
        rows[name] = dict(dem=dem, rep=rep, oth=oth, sentot=dem + rep + oth, ballots=int(m["bct"]),
                          enr_regtotal=int(m["rtl"]), county_official=int(m["tle"].split()[1] == "OFFICIAL"))
    return rows, meta["0"]

def reg(d):
    c = collections.defaultdict(collections.Counter)
    with open(f"{RAW}/voter_stats_{d}.txt") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            c[r["county_desc"].strip().upper()][r["party_cd"].strip()] += int(r["total_voters"])
    return c

def pop():
    p = {}
    for r in csv.DictReader(open(f"{RAW}/co-est2025-alldata.csv", encoding="latin-1")):
        if r["STATE"] == "37" and r["COUNTY"] != "000":
            p[r["CTYNAME"].replace(" County", "").upper()] = int(r["POPESTIMATE2025"])
    return p

P = pop()
recs = {c: {"county": c.title().replace("Mcdowell", "McDowell"), "pop2025": P[c], "zone": COUNTY_ZONE[c],
            "region": BROAD[COUNTY_ZONE[c]]} for c in P}
assert len(recs) == 100
state = {}
for y, d in YEARS.items():
    rows, st = enr(d); state[y] = st
    R = reg(d)
    assert set(rows) == set(recs) == set(R), (y, set(rows) ^ set(recs))
    for c in recs:
        for k, v in rows[c].items():
            recs[c][f"{k}{y}"] = v
        rc = R[c]
        recs[c][f"regdem{y}"] = rc["DEM"]; recs[c][f"regrep{y}"] = rc["REP"]; recs[c][f"reguna{y}"] = rc["UNA"]
        recs[c][f"regoth{y}"] = sum(v for k, v in rc.items() if k not in ("DEM", "REP", "UNA"))
        recs[c][f"regtot{y}"] = sum(rc.values())

df = pd.DataFrame(recs.values())
for y in YEARS:
    df[f"S{y}"] = df[f"dem{y}"] / df[f"ballots{y}"] * 100
    df[f"Srep{y}"] = df[f"rep{y}"] / df[f"ballots{y}"] * 100
    df[f"R{y}"] = df[f"regdem{y}"] / df[f"regtot{y}"] * 100
    df[f"G{y}"] = df[f"S{y}"] - df[f"R{y}"]
    df[f"dr_over_ballots{y}"] = (df[f"dem{y}"] + df[f"rep{y}"]) / df[f"ballots{y}"] * 100
    df[f"overballot{y}"] = ((df[f"dem{y}"] + df[f"rep{y}"]) > df[f"ballots{y}"]).astype(int)
    df[f"senover{y}"] = (df[f"sentot{y}"] > df[f"ballots{y}"]).astype(int)
df["dS"] = df["S26"] - df["S22"]
df["dR"] = df["R26"] - df["R22"]
df["dG"] = df["G26"] - df["G22"]
df["regloss"] = (df["regdem26"] < df["regdem22"]).astype(int)
# Residual after subtracting the expected loss from the registration-share decline (= S26 - S22);
# only for counties that lost registered Democrats (Locked formula rule 1).
df["residual"] = (df["dG"] - (df["R22"] - df["R26"])).where(df["regloss"] == 1)
# Solved backward: implied extra (injected/offset) votes = residual x ballots 2026 = D26 - S22/100 x B26
df["implied_votes"] = (df["dem26"] - df["S22"] / 100 * df["ballots26"]).where(df["regloss"] == 1)
df["regscaled_gap"] = df["dem26"] - df["dem22"] * (df["regdem26"] / df["regdem22"])
df = df.sort_values("pop2025", ascending=False).reset_index(drop=True)
df["pop_rank"] = df.index + 1
df.to_csv(f"{OUT}/nc_senate_2022_2026_by_population.csv", index=False, float_format="%.10f")

S = {}
for y in YEARS:
    S[f"dem{y}"] = int(df[f"dem{y}"].sum()); S[f"rep{y}"] = int(df[f"rep{y}"].sum()); S[f"oth{y}"] = int(df[f"oth{y}"].sum())
    S[f"sentot{y}"] = int(df[f"sentot{y}"].sum()); S[f"ballots{y}"] = int(df[f"ballots{y}"].sum())
    S[f"regdem{y}"] = int(df[f"regdem{y}"].sum()); S[f"regrep{y}"] = int(df[f"regrep{y}"].sum())
    S[f"reguna{y}"] = int(df[f"reguna{y}"].sum()); S[f"regtot{y}"] = int(df[f"regtot{y}"].sum())
    S[f"S{y}"] = S[f"dem{y}"] / S[f"ballots{y}"] * 100; S[f"R{y}"] = S[f"regdem{y}"] / S[f"regtot{y}"] * 100
    S[f"G{y}"] = S[f"S{y}"] - S[f"R{y}"]
    S[f"enr_state_ballots{y}"] = int(state[y]["bct"]); S[f"enr_state_title{y}"] = state[y]["tle"]
    S[f"enr_updated{y}"] = state[y]["imp"]
    S[f"overballot_count{y}"] = int(df[f"overballot{y}"].sum())
S["dG"] = S["G26"] - S["G22"]
S["county_official26"] = int(df["county_official26"].sum())
S["unofficial_counties26"] = df.loc[df.county_official26 == 0, "county"].tolist()
json.dump(S, open(f"{OUT}/summary_base.json", "w"), indent=1)
print(json.dumps(S, indent=1))
