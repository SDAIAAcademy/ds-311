# %% [markdown]
# # Lab 3.1 · Profile four tables, propose rules
#
# Day 3 · Session 1 (Profiling to rules) · 25 min · **AI-off**: no assistant in this lab.
#
# The labels of Days 1 and 2 join four tables Bayyin's analysts prepare every month: the portal's
# complaints extract, the merchant registry, the regions table with populations, and the case-action
# log. Before any rule is written, you profile them in DuckDB, read the anomalies yourself, and
# propose rules in the form the NDMO Data Quality domain asks for: an owner, a business description,
# a dimension, the attributes, and a threshold.
#
# **Reference state.** `data/sources/`: `complaints_extract.csv.gz`, `merchants.csv`, `regions.csv`,
# `case_actions.csv.gz`, as extracted on 2026-09-05.
#
# **Tasks**
# - [ ] 1 · Profile each table in DuckDB (8')
# - [ ] 2 · Five anomalies from the profile (7')
# - [ ] 3 · Rules with dimension, owner and threshold (10')
# - [ ] ✱ Stretch · Timeliness: how old is the newest complaint in each extract?

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

import json
import duckdb
import pandas as pd
import bayyin as B

pd.set_option("display.width", 160)
con = duckdb.connect()
SRC = B.DATA / "sources"
for name, file in (("complaints", "complaints_extract.csv.gz"), ("merchants", "merchants.csv"),
                   ("regions", "regions.csv"), ("actions", "case_actions.csv.gz")):
    con.execute(f"CREATE TABLE {name} AS SELECT * FROM read_csv('{(SRC / file).as_posix()}', all_varchar = true)")
    print(name, con.execute(f"SELECT count(*) FROM {name}").fetchone()[0], "rows")

# %% [markdown]
# ## 1 · Profile each table in DuckDB (8')
#
# Everything is loaded as text on purpose: a profile must see the values as they arrived.
#
# ✏️ **Exercise** · Write `profile(table)`: one row per column with the number of empty values
# (NULL or blank), the number of distinct values, the minimum, the maximum and the most common
# value. For numeric-looking columns, also the minimum and maximum as numbers.

# %%
def profile(table: str) -> pd.DataFrame:
    cols = [r[0] for r in con.execute(f"DESCRIBE {table}").fetchall()]
    rows = []
    for c in cols:
        # BEGIN SOLUTION
        q = f"""SELECT count(*) FILTER (WHERE "{c}" IS NULL OR trim("{c}") = '') AS empty,
                       count(DISTINCT "{c}") AS distinct_values, min("{c}") AS min_text, max("{c}") AS max_text,
                       mode("{c}") AS most_common,
                       min(TRY_CAST("{c}" AS DOUBLE)) AS min_num, max(TRY_CAST("{c}" AS DOUBLE)) AS max_num
                FROM {table}"""
        rows.append(dict(column=c, **dict(zip(["empty", "distinct", "min", "max", "most_common", "min_num", "max_num"],
                                              con.execute(q).fetchone()))))
        # END SOLUTION
    return pd.DataFrame(rows).set_index("column")


profiles = {}
for t in ("complaints", "merchants", "regions", "actions"):
    try:
        profiles[t] = profile(t)
    except NotImplementedError:
        profiles[t] = pd.DataFrame(B.reference("d3_1_profile")[t])
    print(f"\n== {t}\n", profiles[t].to_string())

# %% [markdown]
# ## 2 · Five anomalies from the profile (7')
#
# Read the profiles, not the answer key. Useful questions: is any id repeated? any value outside its
# list? any date in the future or out of order? any amount out of scale? any reference to a row that
# does not exist? Confirm each suspicion with one query.
#
# ✏️ **Exercise** · Write each anomaly in `ANOMALIES` as `(table, column, what you saw, the query
# that confirms it)`, and run the queries.

# %%
try:
    # BEGIN SOLUTION
    ANOMALIES = [
        ("complaints", "complaint_id", "fewer distinct ids than rows",
         "SELECT count(*) - count(DISTINCT complaint_id) FROM complaints"),
        ("complaints", "category_code", "codes outside the six, in lower case or legacy C7",
         "SELECT category_code, count(*) FROM complaints WHERE category_code NOT IN ('REFUND','DEFECT','DELIVERY','PRICE','AD','WARRANTY') GROUP BY 1"),
        ("complaints", "amount_sar", "maximum far above any consumer purchase",
         "SELECT count(*) FROM complaints WHERE TRY_CAST(amount_sar AS DOUBLE) > 50000"),
        ("complaints", "received_date", "dates after the extract date of 2026-09-05",
         "SELECT count(*) FROM complaints WHERE received_date > '2026-09-05'"),
        ("complaints", "closed_date", "closed before received",
         "SELECT count(*) FROM complaints WHERE closed_date <> '' AND closed_date < received_date"),
        ("complaints", "region_code", "empty and R99, not in the regions table",
         "SELECT region_code, count(*) FROM complaints WHERE region_code NOT IN (SELECT region_code FROM regions) OR region_code IS NULL GROUP BY 1"),
        ("actions", "complaint_id", "actions for complaints not in the extract",
         "SELECT count(*) FROM actions WHERE complaint_id NOT IN (SELECT complaint_id FROM complaints)"),
        ("merchants", "cr_number", "fewer distinct registration numbers than merchants",
         "SELECT count(*) - count(DISTINCT cr_number) FROM merchants"),
    ]
    # END SOLUTION
except NotImplementedError:
    ANOMALIES = []
for t, c, seen, q in ANOMALIES:
    print(f"{t}.{c}: {seen} ->", con.execute(q).fetchall()[:4])
B.check(len(ANOMALIES) >= 5, "at least five anomalies, each confirmed by a query")

# %% [markdown]
# 🔍 **Look at** the amounts by month and channel. A unit error rarely shows in the overall maximum
# alone: the whole batch moves.

# %%
print(con.execute("""SELECT left(received_date, 7) AS month, channel, round(median(TRY_CAST(amount_sar AS DOUBLE))) AS median_amount
                     FROM complaints WHERE received_date BETWEEN '2026-06' AND '2026-09' GROUP BY ALL ORDER BY 1, 2""").df().to_string(index=False))

# %% [markdown]
# ## 3 · Rules with dimension, owner and threshold (10')
#
# The NDMO Data Management and Personal Data Protection Standards ask each data-quality rule to name
# its owner, describe the business requirement, assign a dimension (completeness, uniqueness,
# timeliness, validity, accuracy, consistency), list the attributes and define its metric. Owners
# here: Hatoon Al-Furaih (market monitoring, uses the rate), Abdulelah Al-Batal (data engineer),
# Khulood Bin Saedan (labelling lead).
#
# ✏️ **Exercise** · Propose at least six rules covering at least five dimensions. A threshold is the
# share of failing rows the owner accepts; take it from the profile and from what the figure needs.

# %%
try:
    # BEGIN SOLUTION
    PROPOSED = pd.DataFrame([
        dict(rule="One row per complaint id", dimension="uniqueness", table="complaints", attributes="complaint_id", owner="Abdulelah Al-Batal", threshold="0.5%", reason="duplicates inflate the rate"),
        dict(rule="Every complaint has a known region", dimension="completeness", table="complaints", attributes="region_code", owner="Hatoon Al-Furaih", threshold="3%", reason="the rate is published by region"),
        dict(rule="Region code is in the regions table", dimension="validity", table="complaints", attributes="region_code", owner="Hatoon Al-Furaih", threshold="3%", reason="unknown regions drop out of the rate"),
        dict(rule="Category code is one of the six", dimension="validity", table="complaints", attributes="category_code", owner="Khulood Bin Saedan", threshold="1%", reason="the guideline has six codes"),
        dict(rule="Closed on or after received", dimension="consistency", table="complaints", attributes="received_date, closed_date", owner="Abdulelah Al-Batal", threshold="0.5%", reason="days to close must not be negative"),
        dict(rule="No amount above SAR 50,000; monthly median stable by channel", dimension="accuracy", table="complaints", attributes="amount_sar", owner="Hatoon Al-Furaih", threshold="0.1%", reason="a unit error changes every amount figure"),
        dict(rule="No complaint after the extract date", dimension="validity", table="complaints", attributes="received_date", owner="Abdulelah Al-Batal", threshold="0.1%", reason="future dates are entry errors"),
        dict(rule="Every action belongs to a complaint", dimension="consistency", table="actions", attributes="complaint_id", owner="Abdulelah Al-Batal", threshold="1%", reason="orphan actions distort closure counts"),
        dict(rule="Newest complaint within ten days of the extract", dimension="timeliness", table="complaints", attributes="received_date", owner="Hatoon Al-Furaih", threshold="0", reason="a stale extract understates the month"),
    ])
    # END SOLUTION
except NotImplementedError:
    PROPOSED = pd.DataFrame(B.reference("d3_1_profile")["proposed"])
print(PROPOSED[["rule", "dimension", "owner", "threshold"]].to_string(index=False))
dims = set(PROPOSED.dimension)
B.check(len(PROPOSED) >= 6 and len(dims) >= 5, f"{len(PROPOSED)} rules over {len(dims)} dimensions")
B.check(PROPOSED.owner.str.len().gt(0).all(), "every rule has an owner")
out = B.art("d3_1")
(out / "profile.json").write_text(json.dumps({**{t: json.loads(p.to_json()) for t, p in profiles.items()},
                                              "proposed": PROPOSED.to_dict("records")}, ensure_ascii=False, indent=1), encoding="utf-8")

# %% [markdown]
# ## ✱ Stretch · Timeliness
#
# How many days separate the newest complaint (ignoring future dates) from the extract date?

# %%
try:
    # BEGIN SOLUTION
    print(con.execute("""SELECT DATE '2026-09-05' - max(TRY_CAST(received_date AS DATE)) AS days_old
                         FROM complaints WHERE received_date <= '2026-09-05'""").fetchone())
    # END SOLUTION
except NotImplementedError:
    print("stretch not done")

# %% [markdown]
# ## Checkpoint
#
# 1. The maximum amount is SAR 694,783. Is the rule "no amount above SAR 50,000" enough?
#    <details><summary>Answer</summary>No: a batch in halalas multiplies small amounts too, and many stay under 50,000. A batch-level rule on the monthly median by channel catches the whole batch.</details>
# 2. Why must every rule name an owner?
#    <details><summary>Answer</summary>A threshold is a business decision; someone must accept it, answer when it fires, and change it when the use changes.</details>
# 3. Why profile with every column loaded as text?
#    <details><summary>Answer</summary>Casting while loading hides the bad values (they become NULL or fail the load); the profile must see what arrived.</details>
#
# **Carry forward.** `artifacts/d3_1/profile.json`; Lab 3.2 implements a reference rule set, so it
# does not need your proposals.
