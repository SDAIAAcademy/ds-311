# %% [markdown]
# # Lab 3.2 · Warning and blocking rules
#
# Day 3 · Session 2 (Rules with severity) · 25 min · AI-tutor: an assistant may explain a SQL error,
# not write the rules.
#
# A rule is a query that returns the failing rows, a threshold its owner accepts, and a severity:
# **warn** (log and go on), **quarantine** (set the failing rows aside; stop if there are too many) or
# **block** (stop before anything is published). You implement four rules of Bayyin's set, run the
# whole set on the seeded tables, show that every seeded defect is caught, and show that the same
# rules raise no alarm on clean tables.
#
# **Reference state.** `data/sources/` (seeded) and `data/sources_clean/` (the same extract without
# defects); the reference rule set in `pipeline/rules.py`; the trainer's list of seeded defects in
# `data/reference/seeded_defects.json`.
#
# **Tasks**
# - [ ] 1 · A rule as a query that returns failing rows (5')
# - [ ] 2 · The rule set with thresholds and severities (9')
# - [ ] 3 · Every seeded defect caught (6')
# - [ ] 4 · No alarm on the clean tables (5')
# - [ ] ✱ Stretch · Three of the rules again in Pandera

# %%
import os, sys, subprocess
from pathlib import Path

IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    REPO_URL = "https://github.com/SDAIAAcademy/ds-311.git"
    if not Path("/content/ds-311").exists():
        subprocess.run(["git", "clone", "-q", REPO_URL, "/content/ds-311"], check=True)
    os.chdir("/content/ds-311/labs")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements-colab.txt"], check=True)
else:
    while not Path("_tools").exists() and Path.cwd() != Path.cwd().parent:
        os.chdir("..")  # solutions/ notebooks run from labs/
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), "pipeline"))

import copy
import json
import pandas as pd
import bayyin as B
import steps
from rules import RULES as REFERENCE_RULES

pd.set_option("display.width", 160)


def load(kind: str):
    con = steps.connect()
    steps.extract(con, B.DATA / kind, B.DATA / kind / "regions.csv", "2026-09-05")
    return con


seeded = load("sources")
print({t: steps.count(seeded, t) for t in ("complaints", "actions", "merchants", "regions")})

# %% [markdown]
# ## 1 · A rule as a query that returns failing rows (5')
#
# Every table has a row id, `rid`. A rule's query returns the `rid` of each failing row, nothing else,
# so the same query counts failures, lists them and moves them to quarantine.
#
# ✏️ **Exercise** · Write the query of K01: "a complaint is closed on or after the day it was
# received" (`closed_date` may be empty; dates are text in `YYYY-MM-DD`).

# %%
try:
    # BEGIN SOLUTION
    K01_SQL = ("SELECT rid FROM complaints WHERE coalesce(closed_date, '') <> '' "
               "AND TRY_CAST(closed_date AS DATE) < TRY_CAST(received_date AS DATE)")
    # END SOLUTION
except NotImplementedError:
    K01_SQL = next(r["sql"] for r in REFERENCE_RULES if r["id"] == "K01")
print("K01 fails on", seeded.execute(f"SELECT count(*) FROM ({K01_SQL})").fetchone()[0], "rows")

# %% [markdown]
# ## 2 · The rule set with thresholds and severities (9')
#
# `RULES` starts as a copy of the reference set with three queries removed: uniqueness of the id
# (U01), the batch-level accuracy rule on monthly medians (A02), and orphan actions (I01).
#
# ✏️ **Exercise** · Write the three queries, then `run_rules(con, rules)` returning one row per rule:
# failing rows, rate, threshold, severity, status (`pass`/`fail`) and the action
# (`none`/`logged`/`quarantined`/`stop`).

# %%
RULES = copy.deepcopy(REFERENCE_RULES)
by_id = {r["id"]: r for r in RULES}
by_id["K01"]["sql"] = K01_SQL
try:
    # BEGIN SOLUTION
    by_id["U01"]["sql"] = ("SELECT rid FROM (SELECT rid, row_number() OVER (PARTITION BY complaint_id ORDER BY rid) AS k "
                           "FROM complaints) WHERE k > 1")
    by_id["A02"]["sql"] = """WITH m AS (SELECT left(received_date, 7) AS mon, channel, median(TRY_CAST(amount_sar AS DOUBLE)) AS med
                                      FROM complaints GROUP BY ALL),
                                  b AS (SELECT channel, median(med) AS base FROM m GROUP BY channel)
                             SELECT c.rid FROM complaints c JOIN m ON left(c.received_date, 7) = m.mon AND c.channel = m.channel
                             JOIN b ON b.channel = m.channel WHERE m.med > 3 * b.base"""
    by_id["I01"]["sql"] = "SELECT rid FROM actions WHERE complaint_id NOT IN (SELECT complaint_id FROM complaints)"
    # END SOLUTION
except NotImplementedError:
    for k in ("U01", "A02", "I01"):
        by_id[k]["sql"] = next(r["sql"] for r in REFERENCE_RULES if r["id"] == k)


def run_rules(con, rules) -> pd.DataFrame:
    rows = []
    for r in rules:
        # BEGIN SOLUTION
        failing = con.execute(f"SELECT count(*) FROM ({r['sql']})").fetchone()[0]
        total = steps.count(con, r["table"])
        rate = failing / total
        status = "pass" if rate <= r["max_rate"] else "fail"
        action = {"warn": "logged", "quarantine": "quarantined", "block": "stop"}[r["severity"]] if failing else "none"
        if r["severity"] == "quarantine" and status == "fail":
            action = "stop"
        if r["severity"] == "block" and status == "pass" and failing:
            action = "logged"
        rows.append(dict(rule=r["id"], dimension=r["dimension"], owner=r["owner"], failing=failing,
                         rate=round(rate, 5), threshold=r["max_rate"], severity=r["severity"], status=status, action=action))
        # END SOLUTION
    return pd.DataFrame(rows).set_index("rule")


try:
    res = run_rules(seeded, RULES)
except NotImplementedError:
    res = pd.DataFrame(B.reference("d3_2_rule_results")["seeded"])
print(res.to_string())
B.check(set(res[res.action == "stop"].index) == {"A01", "A02"}, "the two accuracy rules stop the run; everything else is quarantined or logged")

# %% [markdown]
# 🔍 **Look at** A01 and A02. The row rule catches the large amounts; the batch rule catches the whole
# August app batch, including the small amounts that stayed under SAR 50,000 after the unit error.

# %% [markdown]
# ## 3 · Every seeded defect caught (6')
#
# The trainer's list names each defect and how many rows carry it. A rule set is judged on it:
# every defect caught by at least one rule, with the same count.
#
# ✏️ **Exercise** · Fill `CATCHES`: the rule (or rules) that should catch each defect, then compare.

# %%
defects = json.loads((B.REF / "seeded_defects.json").read_text(encoding="utf-8"))
try:
    # BEGIN SOLUTION
    CATCHES = {"D1_exact_duplicate": ["U01"], "D3_closed_before_received": ["K01"], "D4_halalas": ["A02"],
               "D5_region": ["C01", "V01"], "D6_orphan_action": ["I01"], "D7_category_code": ["V02"],
               "D8_future_date": ["V03"], "D9_registry_duplicate": ["U02"]}
    # END SOLUTION
except NotImplementedError:
    CATCHES = {}
cmp = pd.DataFrame([dict(defect=d, rules="+".join(rs), seeded=defects[d]["count"], caught=int(res.loc[rs, "failing"].sum()))
                    for d, rs in CATCHES.items()], columns=["defect", "rules", "seeded", "caught"]).set_index("defect")
print(cmp.to_string())
print("not in this rule set:", sorted(set(defects) - set(CATCHES)))
B.check(len(cmp) >= 8 and (cmp.caught >= cmp.seeded).all(), "every listed defect caught in full")

# %% [markdown]
# D2, the resubmissions, is not a rule's job: the rows are valid one by one. Session 3 finds them as
# near duplicates.

# %% [markdown]
# ## 4 · No alarm on the clean tables (5')
#
# A rule that fires on good data trains people to ignore it.

# %%
clean = load("sources_clean")
try:
    res_clean = run_rules(clean, RULES)
except NotImplementedError:
    res_clean = pd.DataFrame(B.reference("d3_2_rule_results")["clean"])
print(res_clean[["failing", "status", "action"]].to_string())
B.check((res_clean.failing == 0).all(), "no rule fires on the clean tables")
_ = (B.art("d3_2") / "rule_results.json").write_text(json.dumps({"seeded": json.loads(res.to_json()), "clean": json.loads(res_clean.to_json())}, indent=1), encoding="utf-8")

# %% [markdown]
# ## ✱ Stretch · Three rules in Pandera
#
# The same checks in a validation framework: a schema over the complaints as a DataFrame.

# %%
try:
    # BEGIN SOLUTION
    import pandera.pandas as pa
    df = seeded.execute("SELECT complaint_id, category_code, TRY_CAST(amount_sar AS DOUBLE) AS amount_sar FROM complaints").df()
    schema = pa.DataFrameSchema({
        "complaint_id": pa.Column(str, unique=True),
        "category_code": pa.Column(str, pa.Check.isin(["REFUND", "DEFECT", "DELIVERY", "PRICE", "AD", "WARRANTY"])),
        "amount_sar": pa.Column(float, pa.Check.le(50000), nullable=True),
    })
    try:
        schema.validate(df, lazy=True)
    except pa.errors.SchemaErrors as e:
        print(e.failure_cases.groupby(["column", "check"]).size())
    # END SOLUTION
except NotImplementedError:
    print("stretch not done")

# %% [markdown]
# ## Checkpoint
#
# 1. Why does the halala batch need two rules?
#    <details><summary>Answer</summary>Multiplying by 100 pushes only the larger amounts above SAR 50,000; the batch rule on the monthly median by channel catches the whole batch.</details>
# 2. C01 fails on 1.4% of rows with a 3% threshold. What happens?
#    <details><summary>Answer</summary>The rows are quarantined with the rule id and the run goes on; above 3% the run would stop.</details>
# 3. Why run the rules on clean data at all?
#    <details><summary>Answer</summary>To show they do not fire falsely: a rule that cries wolf gets switched off.</details>
#
# **Carry forward.** `pipeline/rules.py` holds the same rule set; Day 4 runs it inside the pipeline.
