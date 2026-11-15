# %% [markdown]
# # Lab 3.4 · A contract that rejects a breaking change
#
# Day 3 · Session 4 (A data contract) · 25 min.
#
# Abdulelah's pipeline produces `complaints_prepared`; Hatoon's monthly report consumes it. Today the
# agreement between them lives in their heads. You write it down as a contract in the Open Data
# Contract Standard (ODCS v3.2.0): the schema, the quality clauses taken from the rules, compiled to SQL
# and run. Then the producer makes two changes; the contract must reject the one that breaks Hatoon's
# report and accept the one that does not.
#
# **Reference state.** The prepared table, built here with the pipeline's own steps from
# `data/sources_clean/`; the rule set in `pipeline/rules.py`.
#
# **Tasks**
# - [ ] 1 · The schema part of the contract (7')
# - [ ] 2 · Quality clauses from the rules (5')
# - [ ] 3 · Compile the clauses to SQL and run them (7')
# - [ ] 4 · A breaking change fails; an added column passes (6')
# - [ ] ✱ Stretch · The version number each change needs

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

import yaml
import pandas as pd
import bayyin as B
import steps

con = steps.connect()
steps.extract(con, B.DATA / "sources_clean", B.DATA / "sources_clean" / "regions.csv", "2026-09-05")
steps.gate(con)
steps.clean(con)
steps.dedupe(con)
steps.enrich(con)
con.execute("CREATE OR REPLACE TABLE complaints_prepared AS SELECT * FROM prepared")
print(steps.count(con, "complaints_prepared"), "rows")
print(con.execute("DESCRIBE complaints_prepared").df()[["column_name", "column_type", "null"]].to_string(index=False))

# %% [markdown]
# ## 1 · The schema part of the contract (7')
#
# An ODCS contract describes each table as a schema object with `properties`, one per column: a name,
# a `logicalType` (string, date, number, integer…), the `physicalType` the producer promises, whether
# it is `required`, `unique` or the `primaryKey`, and a description the consumer can read.
#
# ✏️ **Exercise** · Complete `PROPERTIES` for the ten columns above. The first is given. Use the types
# DuckDB reports as `physicalType`; mark as required the columns Hatoon's rate cannot do without.

# %%
PROPERTIES = [
    dict(name="complaint_id", logicalType="string", physicalType="VARCHAR", required=True, unique=True, primaryKey=True,
         description="The portal's complaint number, one row per complaint after de-duplication"),
]
try:
    # BEGIN SOLUTION
    PROPERTIES += [
        dict(name="received_date", logicalType="date", physicalType="DATE", required=True, description="Day the portal received the complaint"),
        dict(name="month", logicalType="string", physicalType="VARCHAR", required=True, description="YYYY-MM of received_date; the rate's period"),
        dict(name="channel", logicalType="string", physicalType="VARCHAR", required=True, description="app, web or call centre"),
        dict(name="merchant_id", logicalType="string", physicalType="VARCHAR", required=False, description="Registry id; empty when the portal had none"),
        dict(name="category", logicalType="string", physicalType="VARCHAR", required=True, description="One of the six codes of guideline v1.1"),
        dict(name="amount_sar", logicalType="number", physicalType="DECIMAL(12,2)", required=False, description="Disputed amount in Saudi riyals"),
        dict(name="region_code", logicalType="string", physicalType="VARCHAR", required=True, description="One of the thirteen regions; joins the population table"),
        dict(name="status", logicalType="string", physicalType="VARCHAR", required=True, description="Case status at extract time"),
        dict(name="days_to_close", logicalType="integer", physicalType="BIGINT", required=False, description="Days from received to closed; empty while open"),
    ]
    # END SOLUTION
except NotImplementedError:
    PROPERTIES = yaml.safe_load((B.REF / "contract.odcs.yaml").read_text(encoding="utf-8"))["schema"][0]["properties"]
    for p in PROPERTIES:
        p.pop("quality", None)
actual = dict(con.execute("SELECT column_name, column_type FROM (DESCRIBE complaints_prepared)").fetchall())
B.check([p["name"] for p in PROPERTIES] == list(actual), "one property per column, in the table's order")
B.check(all(p["physicalType"].replace(" ", "") == actual[p["name"]].replace(" ", "") for p in PROPERTIES), "every physicalType is the type the table has")

# %% [markdown]
# ## 2 · Quality clauses from the rules (5')
#
# ODCS v3.2.0 names a small library of metrics, each compared with an operator such as `mustBe`,
# `mustBeLessThan` or `mustBeGreaterThan`: `nullValues`, `missingValues`, `invalidValues` (with
# `arguments.validValues`), `duplicateValues` and `rowCount`. Anything else is a `type: sql` clause
# whose query returns one number, with `${object}` and `${property}` standing for the table and column.
#
# ✏️ **Exercise** · Attach clauses that carry Day 3's rules into the contract: category in the six
# codes, region in the thirteen, no amount above SAR 50,000, no negative `days_to_close`, and at least
# 20,000 rows a month's extract. Two are given.

# %%
SIX = ["REFUND", "DEFECT", "DELIVERY", "PRICE", "AD", "WARRANTY"]
REGIONS = [f"R{i:02d}" for i in range(1, 14)]
QUALITY = {  # property name (or "*" for the table) -> clauses
    "complaint_id": [dict(metric="duplicateValues", mustBe=0, description="One row per complaint (rule U01)")],
    "*": [dict(metric="rowCount", mustBeGreaterThan=20000, description="A whole extract, not a partial one")],
}
try:
    # BEGIN SOLUTION
    QUALITY |= {
        "category": [dict(metric="invalidValues", arguments=dict(validValues=SIX), mustBe=0, description="The six codes of the guideline (rule V02)")],
        "region_code": [dict(metric="invalidValues", arguments=dict(validValues=REGIONS), mustBe=0, description="The thirteen regions (rule V01)")],
        "amount_sar": [dict(type="sql", query="SELECT count(*) FROM ${object} WHERE ${property} > 50000", mustBe=0,
                            description="No consumer amount above SAR 50,000 (rule A01)")],
        "days_to_close": [dict(type="sql", query="SELECT count(*) FROM ${object} WHERE ${property} < 0", mustBe=0,
                               description="Closed on or after received (rule K01)")],
    }
    # END SOLUTION
except NotImplementedError:
    _ref = yaml.safe_load((B.REF / "contract.odcs.yaml").read_text(encoding="utf-8"))["schema"][0]
    QUALITY |= {p["name"]: p["quality"] for p in _ref["properties"] if "quality" in p and p["name"] not in QUALITY}

contract = {
    "apiVersion": "v3.2.0", "kind": "DataContract", "id": "bayyin-complaints-prepared", "name": "Complaints, prepared",
    "version": "1.0.0", "status": "active", "domain": "consumer-protection",
    "description": {"purpose": "Monthly complaint rate per 100,000 residents by region, for Bayyin's market monitoring",
                    "usage": "Join region_code to the regions table of the same version; count rows per month and region",
                    "limitations": "Synthetic training data. Labels follow guideline v1.1; WARRANTY agreement is the lowest of the six"},
    "team": {"name": "Bayyin data preparation", "members": [{"username": "abdulelah", "role": "producer"}, {"username": "hatoon", "role": "consumer"}]},
    "schema": [{"name": "complaints_prepared", "physicalName": "complaints_prepared", "logicalType": "object", "physicalType": "table",
                "description": "One row per complaint after the quality gate and de-duplication",
                "properties": [dict(p, **({"quality": QUALITY[p["name"]]} if p["name"] in QUALITY else {})) for p in PROPERTIES],
                "quality": QUALITY["*"]}],
}
out = B.art("d3_4")
_ = (out / "contract.odcs.yaml").write_text(yaml.safe_dump(contract, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")
print((out / "contract.odcs.yaml").read_text(encoding="utf-8")[:1400])
n_clauses = sum(len(v) for v in QUALITY.values())
B.check(n_clauses >= 6, f"{n_clauses} quality clauses")

# %% [markdown]
# ## 3 · Compile the clauses to SQL and run them (7')
#
# A contract nobody runs is documentation. Each clause becomes one query that returns a number, and the
# operator decides pass or fail. `required: true` is a clause too: no NULL values.
#
# ✏️ **Exercise** · Write `compile_clause(table, column, clause)` returning the SQL for the five library
# metrics and for `type: sql`; `run_contract` (given) applies the operators.

# %%
OPS = {"mustBe": lambda v, t: v == t, "mustNotBe": lambda v, t: v != t, "mustBeGreaterThan": lambda v, t: v > t,
       "mustBeGreaterOrEqualTo": lambda v, t: v >= t, "mustBeLessThan": lambda v, t: v < t, "mustBeLessOrEqualTo": lambda v, t: v <= t}


def compile_clause(table: str, column: str | None, c: dict) -> str:
    # BEGIN SOLUTION
    if c.get("type") == "sql":
        return c["query"].replace("${object}", table).replace("${property}", column or "")
    m = c["metric"]
    if m == "rowCount":
        return f"SELECT count(*) FROM {table}"
    if m == "nullValues":
        return f"SELECT count(*) FROM {table} WHERE {column} IS NULL"
    if m == "missingValues":
        return f"SELECT count(*) FROM {table} WHERE {column} IS NULL OR trim(CAST({column} AS VARCHAR)) = ''"
    if m == "duplicateValues":
        return f"SELECT count({column}) - count(DISTINCT {column}) FROM {table}"
    if m == "invalidValues":
        vals = ", ".join("'" + str(v).replace("'", "''") + "'" for v in c["arguments"]["validValues"])
        return f"SELECT count(*) FROM {table} WHERE {column} IS NOT NULL AND CAST({column} AS VARCHAR) NOT IN ({vals})"
    raise ValueError(f"unknown metric {m}")
    # END SOLUTION


def run_contract(con, contract: dict, table: str) -> pd.DataFrame:
    rows = []
    obj = contract["schema"][0]
    have = dict(con.execute(f"SELECT column_name, column_type FROM (DESCRIBE {table})").fetchall())
    for p in obj["properties"]:
        col = p["name"]
        if col not in have:
            rows.append(dict(check=f"{col}: column present", value=None, expected="present", status="fail"))
            continue
        same = p["physicalType"].replace(" ", "") == have[col].replace(" ", "")
        rows.append(dict(check=f"{col}: type", value=have[col], expected=p["physicalType"], status="pass" if same else "fail"))
        clauses = ([dict(metric="nullValues", mustBe=0, description="required")] if p.get("required") else []) + p.get("quality", [])
        for c in clauses:
            if not same and c.get("type") == "sql":
                rows.append(dict(check=f"{col}: {c.get('description', 'sql')}", value=None, expected="-", status="fail"))
                continue
            v = con.execute(compile_clause(table, col, c)).fetchone()[0]
            op = next(k for k in OPS if k in c)
            rows.append(dict(check=f"{col}: {c.get('metric', 'sql')} {op} {c[op]}", value=v, expected=c[op], status="pass" if OPS[op](v, c[op]) else "fail"))
    for c in obj.get("quality", []):
        v = con.execute(compile_clause(table, None, c)).fetchone()[0]
        op = next(k for k in OPS if k in c)
        rows.append(dict(check=f"table: {c.get('metric', 'sql')} {op} {c[op]}", value=v, expected=c[op], status="pass" if OPS[op](v, c[op]) else "fail"))
    return pd.DataFrame(rows)


try:
    today = run_contract(con, contract, "complaints_prepared")
    print(today.to_string(index=False))
    B.check((today.status == "pass").all(), "today's table meets its contract")
except NotImplementedError:
    print("compile_clause() not written yet")

# %% [markdown]
# ## 4 · A breaking change fails; an added column passes (6')
#
# Abdulelah proposes two changes. **A**: rename `region_code` to `region` and send `amount_sar` as text
# with a currency sign ("SAR 120.00"). **B**: add a nullable column `merchant_name` for the analysts.
#
# ✏️ **Exercise** · Build both tables from `complaints_prepared`, run the contract on each, and say
# which change Hatoon's report survives.

# %%
try:
    # BEGIN SOLUTION
    con.execute("""CREATE OR REPLACE TABLE change_a AS SELECT * EXCLUDE (region_code, amount_sar),
                   region_code AS region, 'SAR ' || CAST(amount_sar AS VARCHAR) AS amount_sar FROM complaints_prepared""")
    con.execute("CREATE OR REPLACE TABLE change_b AS SELECT *, CAST(NULL AS VARCHAR) AS merchant_name FROM complaints_prepared")
    # END SOLUTION
    res_a = run_contract(con, contract, "change_a")
    res_b = run_contract(con, contract, "change_b")
    print("A:\n", res_a[res_a.status == "fail"].to_string(index=False))
    print("B failures:", int((res_b.status == "fail").sum()))
    B.check((res_a.status == "fail").any() and (res_b.status == "pass").all(), "the rename and the type change fail; the added column passes")
except NotImplementedError:
    print("not done yet")

# %% [markdown]
# 🔍 **Look at** why B passes: the contract lists what the consumer relies on, not every column the
# table may have. A consumer who selects named columns is not hurt by a new one.

# %% [markdown]
# ## ✱ Stretch · The version number each change needs
#
# Contracts use semantic versions: a change the consumer must adapt to raises the major number; an
# added optional column the minor; a corrected description the patch.

# %%
try:
    # BEGIN SOLUTION
    print({"A: rename and retype": "2.0.0", "B: add nullable merchant_name": "1.1.0", "fix a description": "1.0.1"})
    # END SOLUTION
except NotImplementedError:
    print("stretch not done")

# %% [markdown]
# ## Checkpoint
#
# 1. Who should own the contract, the producer or the consumer?
#    <details><summary>Answer</summary>Both sign it; the producer runs it before publishing, the consumer can run it on arrival. Here Abdulelah runs it in the pipeline and Hatoon agrees the clauses.</details>
# 2. Why did the amount clause fail on change A before any value was checked?
#    <details><summary>Answer</summary>The type no longer matches, so a numeric comparison has no meaning; the type check fails first.</details>
# 3. Is a contract the same as the rules of Lab 3.2?
#    <details><summary>Answer</summary>No: the rules gate the raw extract inside the pipeline; the contract states what the published table promises to its consumer. Some clauses repeat rules, on the output side.</details>
#
# **Carry forward.** `artifacts/d3_4/contract.odcs.yaml`; Day 4's pipeline runs it before publishing.
