"""Independent cell-by-cell check of the county PDF against the RAW SBOE files.
Re-parses raw ENR results JSON (county.txt + results_N.txt) and raw voter_stats files from scratch
(no pandas, no build-pass CSV/summary), recomputes every displayed value with exact rational arithmetic,
formats it at the PDF's displayed precision (round half up), and compares to pdftotext output string-for-string."""
import re, os, sys, csv, subprocess
from fractions import Fraction as Fr
from decimal import Decimal, ROUND_HALF_UP
H = os.path.dirname(os.path.abspath(__file__)); RAW = f"{H}/../raw"
PDF = f"{H}/../pdf/North_Carolina_100_County_Democratic_Registration_and_Vote_Change.pdf"
V = {}
for y, d in (("22", "20221108"), ("26", "20261103")):
    ctext = open(f"{RAW}/enr_{d}/county.txt").read()
    for obj in re.findall(r"\{[^{}]*\}", ctext):
        g = dict(re.findall(r'"(\w+)":"([^"]*)"', obj))
        if g["cid"] == "0": continue
        e = V.setdefault(g["cnm"].strip().title().replace("Mcdowell", "McDowell"), {})
        e["B" + y] = int(g["bct"])
        dem = 0
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
V["Statewide total"] = {k: sum(e[k] for e in V.values()) for k in ("B22", "B26", "D22", "D26", "T22", "T26", "RD22", "RD26")}
def r(x, dp):  # exact rational -> half-up decimal string
    q = Decimal(1).scaleb(-dp)
    return str((Decimal(x.numerator) / Decimal(x.denominator)).quantize(q, rounding=ROUND_HALF_UP)) if isinstance(x, Fr) else str(Decimal(x).quantize(q, rounding=ROUND_HALF_UP))
def pct(x, dp=1): return r(x, dp) + "%"
def spct(x, dp=1):
    s = r(x, dp); return ("+" if Decimal(s) > 0 else "") + s + "%"
def ints(n): return f"{n:,}"
def sint(n): return ("+" if n > 0 else "") + f"{n:,}"
def spts(x):
    s = r(x, 2); return ("+" if Decimal(s) > 0 else "") + s
EXP1 = {}; EXP2 = {}
for c, e in V.items():
    R26 = Fr(e["RD26"] * 100, e["T26"]); R22 = Fr(e["RD22"] * 100, e["T22"]); S22 = Fr(e["D22"] * 100, e["B22"]); S26 = Fr(e["D26"] * 100, e["B26"])
    EXP1[c] = [pct(R26), ints(e["RD22"]), ints(e["RD26"]), sint(e["RD26"] - e["RD22"]), spct(Fr(e["RD26"] - e["RD22"], e["RD22"]) * 100),
               ints(e["D22"]), ints(e["D26"]), sint(e["D26"] - e["D22"]), spct(Fr(e["D26"] - e["D22"], e["D22"]) * 100),
               ints(e["B22"]), ints(e["B26"]), sint(e["B26"] - e["B22"]), spct(Fr(e["B26"] - e["B22"], e["B22"]) * 100)]
    EXP2[c] = [pct(S22), pct(S26), spts(S26 - S22), pct(R22), ints(e["T22"]), pct(R26), ints(e["T26"])]
    e["R26"] = R26
COLS1 = ["Dem Reg Share 2026 %", "Dem Reg 2022", "Dem Reg 2026", "Reg Change #", "Reg Change %", "Dem Senate Votes 2022", "Dem Senate Votes 2026*", "Vote Change #",
         "Vote Change %", "Total Ballots 2022", "Total Ballots 2026*", "Ballot Change #", "Ballot Change %"]
COLS2 = ["Dem Share of Ballots 2022 %", "Dem Share of Ballots 2026* %", "Change (pts)", "Dem Share of Registration 2022 %", "Total Registered 2022",
         "Dem Share of Registration 2026 %", "Total Registered 2026"]
txt = subprocess.run(["pdftotext", "-layout", PDF, "-"], capture_output=True, text=True).stdout
names = sorted(V, key=len, reverse=True); P1, P2, order = {}, {}, []
for line in txt.splitlines():
    s = line.strip()
    for nm in names:
        if s.startswith(nm + " ") and re.match(r"[-+\d]", s[len(nm):].strip() or "x"):
            toks = s[len(nm):].split()
            if len(toks) == 13 and nm not in P1: P1[nm] = toks; order.append(nm)
            elif len(toks) == 7 and nm not in P2: P2[nm] = toks; order.append(nm)
            else: print("UNPARSED/DUPLICATE ROW:", nm, toks)
            break
cells = match = 0; mism = []
for nm in V:
    for tbl, P, EXP, COLS in (("Table 1", P1, EXP1, COLS1), ("Table 2", P2, EXP2, COLS2)):
        got = P.get(nm)
        for j, col in enumerate(COLS):
            cells += 1; g = got[j] if got and j < len(got) else "MISSING"
            if g == EXP[nm][j]: match += 1
            else: mism.append((tbl, nm, col, g, EXP[nm][j]))
exp_order = sorted([c for c in V if c != "Statewide total"], key=lambda c: (-V[c]["R26"], c)) + ["Statewide total"]
order_ok = order == exp_order + exp_order
print(f"RAW-vs-PDF: cells checked {cells}; matched {match}; mismatches {len(mism)}; rows table1 {len(P1)}, table2 {len(P2)}; sort order (2026 Dem reg share desc) matches raw: {order_ok}")
for m in mism: print("  MISMATCH", m)
sys.exit(0 if not mism and order_ok else 1)
