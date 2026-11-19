"""Verify every figure in the county PDF against the verified county data (pdftotext extraction)."""
import subprocess, os, re, sys
import pandas as pd
H = os.path.dirname(os.path.abspath(__file__))
PDF = f"{H}/../pdf/North_Carolina_100_County_Democratic_Registration_and_Vote_Change.pdf"
df = pd.read_csv(f"{H}/../data/nc_senate_2022_2026_by_population.csv")
txt = subprocess.run(["pdftotext", "-layout", PDF, "-"], capture_output=True, text=True).stdout
names = sorted(df.county.tolist() + ["Statewide total"], key=len, reverse=True)
t1, t2 = {}, {}
for line in txt.splitlines():
    s = line.strip()
    for nm in names:
        if s.startswith(nm + " "):
            toks = s[len(nm):].split()
            (t1 if len(toks) == 13 else t2 if len(toks) == 7 else {}).setdefault(nm, toks)
            break
num = lambda t: float(t.replace(",", "").replace("%", "").replace("+", ""))
tot = {k: df[k].sum() for k in ("regdem22", "regdem26", "dem22", "dem26", "ballots22", "ballots26", "regtot22", "regtot26")}
rows = [(r.county, r) for _, r in df.iterrows()] + [("Statewide total", pd.Series(tot))]
checked = bad = 0; probs = []
def ck(nm, label, got, exp, tol):
    global checked, bad; checked += 1
    if abs(num(got) - exp) > tol: bad += 1; probs.append((nm, label, got, exp))
for nm, r in rows:
    a = t1.get(nm); b = t2.get(nm)
    if a is None or b is None: bad += 1; probs.append((nm, "row missing", a, b)); continue
    R22 = r.regdem22 / r.regtot22 * 100; R26 = r.regdem26 / r.regtot26 * 100; S22 = r.dem22 / r.ballots22 * 100; S26 = r.dem26 / r.ballots26 * 100
    exp1 = [R26, r.regdem22, r.regdem26, r.regdem26 - r.regdem22, (r.regdem26 / r.regdem22 - 1) * 100, r.dem22, r.dem26, r.dem26 - r.dem22, (r.dem26 / r.dem22 - 1) * 100,
            r.ballots22, r.ballots26, r.ballots26 - r.ballots22, (r.ballots26 / r.ballots22 - 1) * 100]
    tol1 = [0.05, 0, 0, 0, 0.05, 0, 0, 0, 0.05, 0, 0, 0, 0.05]
    for j, (g, e, tl) in enumerate(zip(a, exp1, tol1)): ck(nm, f"t1c{j+2}", g, e, tl + 1e-9)
    exp2 = [S22, S26, S26 - S22, R22, r.regtot22, R26, r.regtot26]; tol2 = [0.05, 0.05, 0.005, 0.05, 0, 0.05, 0]
    for j, (g, e, tl) in enumerate(zip(b, exp2, tol2)): ck(nm, f"t2c{j+2}", g, e, tl + 1e-9)
# county sums equal statewide row (as printed)
sums = 0
for j in (1, 2, 3, 5, 6, 7, 9, 10, 11):
    sums += 1
    if sum(num(t1[c][j]) for c in df.county) != num(t1["Statewide total"][j]): bad += 1; probs.append(("SUM", j))
for j in (4, 6):
    sums += 1
    if sum(num(t2[c][j]) for c in df.county) != num(t2["Statewide total"][j]): bad += 1; probs.append(("SUM2", j))
# order check: sorted by 2026 Dem reg share descending
order = [nm for nm in re.findall(r"^\s*([A-Z][A-Za-z ]+?)\s+\d", txt, re.M) if nm in set(df.county)]
exp_order = df.sort_values(["R26", "county"], ascending=[False, True]).county.tolist()
ord_ok = order[:100] == exp_order and order[100:200] == exp_order
print(f"PDF: rows found table1 {len(t1)} table2 {len(t2)} (100 counties + statewide each); figures checked {checked}; county-sum checks {sums}; mismatches {bad}; sort order ok {ord_ok}")
for p in probs[:20]: print("  MISMATCH", p)
print("Statewide row t1:", " | ".join(t1.get("Statewide total", []))); print("Statewide row t2:", " | ".join(t2.get("Statewide total", [])))
sys.exit(0 if bad == 0 and ord_ok else 1)
