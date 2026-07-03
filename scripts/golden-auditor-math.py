#!/usr/bin/env python3
"""Golden math check for the auditor scoring frameworks — Python 3 stdlib only.

The auditor *scores* are computed by an LLM reading the runbook, but the
arithmetic those scores depend on is fully deterministic and therefore testable.
This guards the two regression classes that have actually bitten this repo:

  1. A weight table column that no longer sums to 100% (or the CITE weights that
     no longer sum to 1.0) — a silent scoring bug.
  2. A worked example whose stated raw_overall no longer matches the weighted
     arithmetic of its own inputs — i.e. someone edited the numbers wrong, or a
     release-bump corrupted them.

Run: python3 scripts/golden-auditor-math.py   (exit 0 = pass, 1 = fail)
Wired into CI alongside validate-skill.sh.
"""
from __future__ import annotations

import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(ROOT, "references", "core-eeat-benchmark.md")
CITE = os.path.join(ROOT, "references", "cite-domain-rating.md")
C3 = os.path.join(ROOT, "references", "c3-benchmark.md")
ROAS = os.path.join(ROOT, "references", "roas-benchmark.md")
SEND = os.path.join(ROOT, "references", "send-benchmark.md")
CQA = os.path.join(ROOT, "optimize", "content-quality-auditor", "SKILL.md")
DAA = os.path.join(ROOT, "monitor", "domain-authority-auditor", "SKILL.md")

fails = []
def check(cond, msg):
    print(("  ok  " if cond else "FAIL  ") + msg)
    if not cond:
        fails.append(msg)


def parse_core_weight_table(path):
    """Return {content_type: {dim: weight_fraction}} from the §Content-Type Weight Table."""
    text = open(path, encoding="utf-8").read()
    lines = text.splitlines()
    # find the header row that names the content types
    hdr_i = next((i for i, l in enumerate(lines)
                  if l.startswith("| Dim ") and "Product Review" in l), None)
    if hdr_i is None:
        return {}
    cols = [c.strip() for c in lines[hdr_i].strip("|").split("|")][1:]  # drop 'Dim'
    table = {c: {} for c in cols}
    for l in lines[hdr_i + 2:]:                # skip the |---| separator
        if not l.startswith("|"):
            break
        cells = [c.strip() for c in l.strip("|").split("|")]
        dim = cells[0]
        for c, val in zip(cols, cells[1:]):
            m = re.match(r"(\d+)%", val)
            if m:
                table[c][dim] = int(m.group(1)) / 100.0
    return table


def weighted(dims, weights):
    return math.floor(sum(dims[d] * weights[d] for d in dims))


print("== CORE-EEAT weight table: every content-type column sums to 100% ==")
core = parse_core_weight_table(CORE)
check(len(core) == 9, "parsed 9 content-type columns (got %d)" % len(core))
for ctype, w in core.items():
    total = round(sum(w.values()) * 100)
    check(total == 100 and len(w) == 8, "%s: 8 dims summing to 100%% (got %d dims, %d%%)" % (ctype, len(w), total))

print("== CORE-EEAT worked examples recompute to their stated raw_overall ==")
# Example 1 — Product Review (from content-quality-auditor §2)
ex1 = {"C": 75, "O": 77, "R": 80, "E": 75, "Exp": 78, "Ept": 77, "A": 77, "T": 85}
if "Product Review" in core:
    check(weighted(ex1, core["Product Review"]) == 78,
          "CORE ex1 (Product Review) weighted == 78 (got %d)" % weighted(ex1, core["Product Review"]))
# Example 2 — FAQ Page
ex2 = {"C": 55, "O": 75, "R": 88, "E": 80, "Exp": 80, "Ept": 75, "A": 82, "T": 85}
if "FAQ Page" in core:
    check(weighted(ex2, core["FAQ Page"]) == 73,
          "CORE ex2 (FAQ Page) weighted == 73 (got %d)" % weighted(ex2, core["FAQ Page"]))

print("== CITE default weights sum to 1.0 and worked examples recompute ==")
cite_text = open(CITE, encoding="utf-8").read()
m = re.search(r"C\s*×\s*([\d.]+)\s*\+\s*I\s*×\s*([\d.]+)\s*\+\s*T\s*×\s*([\d.]+)\s*\+\s*E\s*×\s*([\d.]+)", cite_text)
check(m is not None, "found CITE default-weight formula")
if m:
    wC, wI, wT, wE = (float(x) for x in m.groups())
    check(abs((wC + wI + wT + wE) - 1.0) < 1e-9, "CITE weights sum to 1.0 (got %.2f)" % (wC + wI + wT + wE))
    cw = {"C": wC, "I": wI, "T": wT, "E": wE}
    c1 = weighted({"C": 80, "I": 70, "T": 85, "E": 75}, cw)
    check(c1 == 78, "CITE ex1 (C80 I70 T85 E75) weighted == 78 (got %d)" % c1)
    c2 = weighted({"C": 55, "I": 70, "T": 58, "E": 72}, cw)
    check(c2 == 62, "CITE ex2 (C55 I70 T58 E72) weighted == 62 (got %d)" % c2)

print("== the worked-example INPUTS and stated results still appear in the auditor bodies ==")
cqa, daa = open(CQA, encoding="utf-8").read(), open(DAA, encoding="utf-8").read()
# Input-vector presence closes the false-pass gap: if a SKILL example's dimension
# numbers drift away from what this test recomputes, the test must notice.
check("C=75 O=77 R=80 E=75 Exp=78 Ept=77 A=77 T=85" in cqa, "CORE ex1 input vector present in content-quality-auditor")
check("C=55 O=75 R=88 E=80 Exp=80 Ept=75 A=82 T=85" in cqa, "CORE ex2 input vector present in content-quality-auditor")
check("C=80 I=70 T=85 E=75" in daa, "CITE ex1 input vector present in domain-authority-auditor")
check("C=55 I=70 T=58 E=72" in daa, "CITE ex2 input vector present in domain-authority-auditor")
check("raw_overall = 78" in cqa and "raw_overall = 73" in cqa, "CORE stated results 78 & 73 present in content-quality-auditor")
check("raw_overall = 78" in daa and "raw_overall = 62" in daa, "CITE stated results 78 & 62 present in domain-authority-auditor")
# guard against the old framework-crossed defect re-appearing
check("624 / 8" not in daa and "O=77" not in daa, "no CORE-EEAT 8-dim arithmetic leaked into the CITE auditor")

print("== C3 CVI geometric-mean rollup recomputes; veto/cap boundary locked ==")
c3_text = open(C3, encoding="utf-8").read()
check(re.search(r"CVI\s*=\s*\(\s*ACE_avg.*ROI\s*\)\s*\^\s*\(1/3\)", c3_text) is not None,
      "found C3 CVI geometric-mean formula")

def cvi(a, r, o):
    # geometric mean of the three scope averages, floor-rounded (repo floor convention)
    return math.floor((a * r * o) ** (1.0 / 3.0))

check(cvi(90, 80, 70) == 79, "C3 no-veto CVI (ACE90 ART80 ROI70) == 79 (got %d)" % cvi(90, 80, 70))
check(cvi(59, 80, 70) == 69, "C3 veto-capped CVI (ACE59 ART80 ROI70) == 69 (got %d)" % cvi(59, 80, 70))
# input-vector + result presence (false-pass guard, mirrors CORE/CITE)
check("ACE_avg=90 ART_avg=80 ROI=70" in c3_text, "C3 no-veto input vector present in c3-benchmark")
check("floor(504000^(1/3)) = 79" in c3_text, "C3 no-veto stated CVI 79 present in c3-benchmark")
check("ACE_avg=59 (capped)" in c3_text, "C3 veto-capped input vector present in c3-benchmark")
check("floor(330400^(1/3)) = 69" in c3_text, "C3 veto-capped stated CVI 69 present in c3-benchmark")
# cap boundary: C3 Low ceiling 59 vs runbook 60 must stay documented as band-aligned
check("≤ 59" in c3_text and "min(raw, 60) = 60" in c3_text,
      "C3 cap-reconciliation boundary (Low ≤59 vs runbook min(raw,60)=60) documented")

print("== ROAS RQS arithmetic weighted-mean: both goal-weight rows sum to 1.0; worked examples recompute ==")
roas_text = open(ROAS, encoding="utf-8").read()
wre = re.compile(r"R\s*[×xX*]\s*([\d.]+)\s*\+\s*O\s*[×xX*]\s*([\d.]+)\s*\+\s*A\s*[×xX*]\s*([\d.]+)\s*\+\s*S\s*[×xX*]\s*([\d.]+)")
rows = wre.findall(roas_text)
check(len(rows) >= 2, "found both ROAS goal-weight formulas (got %d)" % len(rows))
ex_vec = {"R": 75, "O": 80, "A": 85, "S": 78}
if len(rows) >= 2:
    dr = {k: float(v) for k, v in zip("ROAS", rows[0])}
    pr = {k: float(v) for k, v in zip("ROAS", rows[1])}
    check(abs(sum(dr.values()) - 1.0) < 1e-9, "ROAS DR weights sum to 1.0 (got %.2f)" % sum(dr.values()))
    check(abs(sum(pr.values()) - 1.0) < 1e-9, "ROAS Prospecting weights sum to 1.0 (got %.2f)" % sum(pr.values()))
    check(weighted(ex_vec, dr) == 78, "ROAS DR example (R75 O80 A85 S78) == 78 (got %d)" % weighted(ex_vec, dr))
    check(weighted(ex_vec, pr) == 80, "ROAS Prospecting example (same vector) == 80 (got %d)" % weighted(ex_vec, pr))
check("R=75 O=80 A=85 S=78" in roas_text, "ROAS input vector present in roas-benchmark")
check("floor(78.25) = 78" in roas_text, "ROAS DR result 78 present in roas-benchmark")
check("floor(80.25) = 80" in roas_text, "ROAS Prospecting result 80 present in roas-benchmark")

print("== SEND EQS arithmetic weighted-mean: all three goal-weight rows sum to 1.0; worked examples recompute ==")
send_text = open(SEND, encoding="utf-8").read()
swe = re.compile(r"S\s*[×xX*]\s*([\d.]+)\s*\+\s*E\s*[×xX*]\s*([\d.]+)\s*\+\s*N\s*[×xX*]\s*([\d.]+)\s*\+\s*D\s*[×xX*]\s*([\d.]+)")
srows = swe.findall(send_text)
check(len(srows) >= 3, "found all three SEND goal-weight formulas (got %d)" % len(srows))
send_vec = {"S": 80, "E": 75, "N": 70, "D": 78}
if len(srows) >= 3:
    promo = {k: float(v) for k, v in zip("SEND", srows[0])}
    reten = {k: float(v) for k, v in zip("SEND", srows[1])}
    cold = {k: float(v) for k, v in zip("SEND", srows[2])}
    check(abs(sum(promo.values()) - 1.0) < 1e-9, "SEND Promotional weights sum to 1.0 (got %.2f)" % sum(promo.values()))
    check(abs(sum(reten.values()) - 1.0) < 1e-9, "SEND Retention weights sum to 1.0 (got %.2f)" % sum(reten.values()))
    check(abs(sum(cold.values()) - 1.0) < 1e-9, "SEND Cold-outbound weights sum to 1.0 (got %.2f)" % sum(cold.values()))
    check(weighted(send_vec, promo) == 76, "SEND Promotional example (S80 E75 N70 D78) == 76 (got %d)" % weighted(send_vec, promo))
    check(weighted(send_vec, reten) == 74, "SEND Retention example (same vector) == 74 (got %d)" % weighted(send_vec, reten))
    check(weighted(send_vec, cold) == 76, "SEND Cold-outbound example (same vector) == 76 (got %d)" % weighted(send_vec, cold))
check("S=80 E=75 N=70 D=78" in send_text, "SEND input vector present in send-benchmark")
check("floor(76.6) = 76" in send_text, "SEND Promotional result 76 present in send-benchmark")
check("floor(74.95) = 74" in send_text, "SEND Retention result 74 present in send-benchmark")
check("floor(76.95) = 76" in send_text, "SEND Cold-outbound result 76 present in send-benchmark")

print()
if fails:
    print("GOLDEN MATH FAILED — %d check(s):" % len(fails))
    for f in fails:
        print("  - " + f)
    sys.exit(1)
print("All auditor golden-math checks passed.")
sys.exit(0)
