#!/usr/bin/env bash
# Rebuild everything from the raw SBOE files and run both independent verification passes.
set -euo pipefail
cd "$(dirname "$0")"
R=../raw
for z in results_pct_20221108 results_pct_20261103 voter_stats_20221108 voter_stats_20261103; do
  [ -f $R/$z.txt ] || unzip -o -q $R/$z.zip -d $R; done
python3 build_data.py > /dev/null
python3 analysis.py > /dev/null
python3 share_fit.py > /dev/null
python3 charts.py > /dev/null
python3 build_pdf.py > /dev/null
python3 verify_pdf_raw.py
python3 verify_pdf.py > /dev/null
python3 build_wiki.py > /dev/null
python3 verify_pass1.py > /tmp/p1.txt; python3 verify_pass2.py > /tmp/p2.txt
python3 - <<'PY'
import json, re
p1 = open("/tmp/p1.txt").read(); p2 = open("/tmp/p2.txt").read()
g = lambda pat, s: re.search(pat, s).group(1)
v1 = (f"{int(g(r'county-figure checks (\d+)', p1)):,} county-figure checks (100 counties × {g(r'fields per county (\d+)', p1)} fields), "
      f"{g(r'statewide/summary checks (\d+)', p1)} statewide/summary checks and {g(r'wiki checks (\d+)', p1)} wiki checks, "
      f"{int(g(r'county-figure checks \d+; mismatches (\d+)', p1)) + int(g(r'summary checks \d+; mismatches (\d+)', p1))} mismatches")
v2 = (f"{int(g(r'county-figure checks (\d+)', p2)):,} county-figure checks, {g(r'statewide/summary checks (\d+)', p2)} statewide/summary checks "
      f"and {int(g(r'rows checked (\d+)', p2))*10:,} wiki table figures ({g(r'rows checked (\d+)', p2)} county rows × 10), "
      f"{int(g(r'county-figure checks \d+; mismatches (\d+)', p2)) + int(g(r'summary checks \d+; mismatches (\d+)', p2)) + int(g(r'rows checked \d+ \(10 figures each\); mismatches (\d+)', p2))} mismatches")
json.dump({"p1": v1, "p2": v2}, open("../data/verify_summary.json", "w"), indent=1)
PY
python3 build_wiki.py > /dev/null
{ echo "NC U.S. Senate 2022 vs 2026 - verification log, run $(date '+%Y-%m-%d %H:%M %Z')"; echo; echo "== VERIFICATION PASS 1 (scripts/verify_pass1.py)";
  python3 verify_pass1.py; echo "exit $?"; echo; echo "== VERIFICATION PASS 2 (scripts/verify_pass2.py)"; python3 verify_pass2.py; echo "exit $?"; } > ../VERIFY_LOG.txt
cat ../VERIFY_LOG.txt
