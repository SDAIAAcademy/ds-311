# %% [markdown]
# # Lab 4.3 · Why the August rate changed
#
# Day 4 · Session 3 (Tracing a changed figure) · 25 min · AI-tutor.
#
# In September Bayyin published August's complaint rate for region R04: 48.06 per 100,000 residents.
# The October refresh republished August at 39.14. A deputy minister's office asks Hatoon which figure
# is right. You read the two runs' logs and lineage, recompute the figure one change at a time, list the
# affected outputs and write the incident note with the answer.
#
# **Reference state.** `data/runs/`: for each run (`run_a`, September; `run_b`, October) the staged
# extract, `run_log.json`, `lineage.jsonl` (OpenLineage events) and `figures.csv`; the two versions of
# the regions table; `git_log.txt`, the commits between the runs.
#
# **Tasks**
# - [ ] 1 · What changed between the two runs (6')
# - [ ] 2 · Recompute one change at a time (9')
# - [ ] 3 · Which outputs are affected (4')
# - [ ] 4 · The incident note, and the answer to the stakeholder (6')
# - [ ] ✱ Stretch · A lineage check that would have warned

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
from datetime import date
import pandas as pd
import bayyin as B

pd.set_option("display.width", 160)
RUNS = B.DATA / "runs"
logs = {r: json.loads((RUNS / r / "run_log.json").read_text(encoding="utf-8")) for r in ("run_a", "run_b")}
lineage = {r: [json.loads(l) for l in (RUNS / r / "lineage.jsonl").read_text(encoding="utf-8").splitlines()] for r in ("run_a", "run_b")}
figs = {r: pd.read_csv(RUNS / r / "figures.csv", dtype={"region_code": str}) for r in ("run_a", "run_b")}
print({r: figs[r].set_index("region_code").loc["R04", "rate_per_100k"] for r in figs})
print((RUNS / "git_log.txt").read_text(encoding="utf-8"))

# %% [markdown]
# ## 1 · What changed between the two runs (6')
#
# ✏️ **Exercise** · Write `changes(a, b)`: compare the two run logs and return each difference as
# `(what, run_a, run_b)`: the refresh date, the code version, the extract's row count, the regions
# version, and the parameters of every step whose parameters differ. Then confirm with the lineage
# events of the `dedupe` and `enrich` jobs.

# %%
def changes(a: dict, b: dict) -> list[tuple]:
    out = []
    # BEGIN SOLUTION
    for k in ("refresh_date", "code_version"):
        if a[k] != b[k]:
            out.append((k, a[k], b[k]))
    ia, ib = {i["name"]: i for i in a["inputs"]}, {i["name"]: i for i in b["inputs"]}
    if ia["complaints_extract"]["rows"] != ib["complaints_extract"]["rows"]:
        out.append(("extract rows", ia["complaints_extract"]["rows"], ib["complaints_extract"]["rows"]))
    if ia["regions"]["version"] != ib["regions"]["version"]:
        out.append(("regions version", ia["regions"]["version"], ib["regions"]["version"]))
    sa, sb = {s["step"]: s for s in a["steps"]}, {s["step"]: s for s in b["steps"]}
    for step in sa:
        if sa[step].get("params") != sb[step].get("params"):
            out.append((f"{step} params", sa[step].get("params"), sb[step].get("params")))
    # END SOLUTION
    return out


try:
    found = changes(logs["run_a"], logs["run_b"])
except NotImplementedError:
    found = []
for c in found:
    print(c)
for r in ("run_a", "run_b"):
    for e in lineage[r]:
        if e["job"]["name"] in ("dedupe", "enrich"):
            print(r, e["job"]["name"], e["run"]["facets"]["params"], [i["name"] + str(i["facets"]) for i in e["inputs"]])
B.check(any("dedupe" in str(c[0]) for c in found) and any("regions" in str(c[0]) for c in found) and any("rows" in str(c[0]) for c in found),
        "three changes found: more rows, a new population, a new dedupe key")

# %% [markdown]
# ## 2 · Recompute one change at a time (9')
#
# Three things changed at once. To know how much of the drop each one caused, start from September's
# run and apply the changes one by one, in the order they reached the pipeline, recomputing R04's August
# rate each time.
#
# ✏️ **Exercise** · Write `dedupe(rows, key)` (keep the first row of each key, in order of received date
# then complaint id) and `rate(rows, regions)` (August complaints in R04 per 100,000 residents, two
# decimals). The keys are given.

# %%
stage = {r: B.read(f"runs/{r}/stage_clean.csv.gz") for r in ("run_a", "run_b")}
regions = {v: B.read(f"runs/regions_v{v.replace('.', '_')}.csv") for v in ("2026.1", "2026.2")}
KEY_ID = ["complaint_id"]
KEY_DAY = ["customer_key", "merchant_name_raw", "received_date"]


def dedupe(rows: pd.DataFrame, key: list[str]) -> pd.DataFrame:
    # BEGIN SOLUTION
    return rows.sort_values(["received_date", "complaint_id"]).drop_duplicates(subset=key, keep="first")
    # END SOLUTION


def rate(rows: pd.DataFrame, regs: pd.DataFrame, region: str = "R04", month: str = "2026-08") -> tuple[int, float]:
    # BEGIN SOLUTION
    pop = int(regs.set_index("region_code").loc[region, "population"])
    n = int(((rows.region_code == region) & rows.received_date.str.startswith(month)).sum())
    return n, round(n / pop * 100000, 2)
    # END SOLUTION


try:
    steps_ = {
        "September run": rate(dedupe(stage["run_a"], KEY_ID), regions["2026.1"]),
        "+ late arrivals": rate(dedupe(stage["run_b"], KEY_ID), regions["2026.1"]),
        "+ new population": rate(dedupe(stage["run_b"], KEY_ID), regions["2026.2"]),
        "+ new dedupe key": rate(dedupe(stage["run_b"], KEY_DAY), regions["2026.2"]),
    }
except NotImplementedError:
    ref = B.reference("d4_3_attribution")
    steps_ = {k: (ref[r]["n"], ref[r]["rate"]) for k, r in [("September run", "run_a"), ("+ late arrivals", "late_arrivals"),
                                                              ("+ new population", "new_population"), ("+ new dedupe key", "new_dedupe_key")]}
att = pd.DataFrame([dict(step=k, complaints=n, rate=r) for k, (n, r) in steps_.items()])
att["change"] = att.rate.diff().round(2)
print(att.to_string(index=False))
ref = B.reference("d4_3_attribution")
B.check(att.rate.iloc[0] == ref["run_a"]["rate"] and att.rate.iloc[-1] == ref["run_b"]["rate"], "the chain starts at September's 48.06 and ends at October's 39.14")

# %% [markdown]
# 🔍 **Look at** the size of each change. Late arrivals raised the figure; the new population lowered it
# a little; the new dedupe key removed 72 complaints in R04 alone. Which of those is a correction, and
# which is a defect?

# %%
try:
    gone = dedupe(stage["run_b"], KEY_ID)
    kept = dedupe(stage["run_b"], KEY_DAY)
    dropped = gone[~gone.complaint_id.isin(kept.complaint_id) & (gone.region_code == "R04") & gone.received_date.str.startswith("2026-08")]
    print(len(dropped), "R04 August complaints dropped by the new key; same product as an earlier one that day:",
          int(dropped.merge(gone, on=["customer_key", "merchant_name_raw", "received_date"]).query("complaint_id_x != complaint_id_y and product_x == product_y").complaint_id_x.nunique()))
    print(dropped.head(6)[["complaint_id", "customer_key", "merchant_name_raw", "product", "received_date"]].to_string(index=False))
except NotImplementedError:
    print("write dedupe() first")

# %% [markdown]
# The key "customer, merchant, day" treats two complaints about **different products** bought from one
# merchant on one day as one. In R04 a cluster of such complaints arrived in August. The correction
# Bayyin adopts: keep the late arrivals and the new population (both are right), and de-duplicate
# resubmissions as the pipeline of Lab 4.1 does: same customer, merchant **and product** within one day.

# %%
def dedupe_window(rows: pd.DataFrame) -> pd.DataFrame:
    """Drop a resubmission: the same customer, merchant and product within one day of the last kept row."""
    keep, last = [], {}
    for r in rows.sort_values(["received_date", "complaint_id"]).itertuples():
        k, d = (r.customer_key, r.merchant_name_raw, r.product), date.fromisoformat(r.received_date)
        if k in last and (d - last[k]).days <= 1:
            continue
        last[k] = d
        keep.append(r.Index)
    return rows.loc[keep]


fixed = dedupe_window(stage["run_b"])
try:
    corrected = rate(fixed, regions["2026.2"])
except NotImplementedError:
    corrected = (ref["corrected"]["n"], ref["corrected"]["rate"])
print("corrected:", corrected)
B.check(corrected[1] == ref["corrected"]["rate"], f"the corrected figure is {ref['corrected']['rate']}")

# %% [markdown]
# ## 3 · Which outputs are affected (4')
#
# The dedupe key ran on every region, not only R04. The incident note must list every published figure
# that was wrong in October.
#
# ✏️ **Exercise** · For every region, compare October's published August rate (`figures.csv` of run B)
# with the corrected one, and list the regions where October's figure is off by more than 1%.

# %%
cmp = figs["run_b"][["region_code", "rate_per_100k"]].rename(columns={"rate_per_100k": "october"})
try:
    # BEGIN SOLUTION
    cmp["corrected"] = [rate(fixed, regions["2026.2"], r)[1] for r in cmp.region_code]
    cmp["off_pct"] = ((cmp.october / cmp.corrected - 1) * 100).round(1)
    affected = cmp[cmp.off_pct.abs() > 1].region_code.tolist()
    # END SOLUTION
except NotImplementedError:
    affected = []
print(cmp.to_string(index=False))
print("affected:", affected)
B.check("R04" in affected and len(affected) > 1, "R04 is the largest error, and not the only one")
downstream = [e["job"]["name"] for e in lineage["run_b"]]
print("jobs from the dedupe step on, from the lineage:", downstream[downstream.index("dedupe"):])

# %% [markdown]
# ## 4 · The incident note, and the answer to the stakeholder (6')
#
# ✏️ **Exercise** · Fill the note. Every number must come from your tables above.

# %%
try:
    # BEGIN SOLUTION
    NOTE = {
        "what happened": "August's complaint rate for R04 was published at 48.06 per 100,000 in September and republished at 39.14 in October.",
        "root cause": "Commit c9d05b3 changed the dedupe key to customer, merchant and day. It merges complaints about different products from one merchant on one day: it dropped 72 R04 August complaints, of which only 4 were resubmissions.",
        "other changes, both correct": "260 late arrivals for August (+30 in R04) and the regions table 2026.2 (R04 population up 5.5%).",
        "affected outputs": f"the prepared table, and the August rate of {len(affected)} regions off by more than 1% ({', '.join(affected)}); R04 by far the most.",
        "correction": "Dedupe on customer, merchant and product within one day; keep the late arrivals and the new population.",
        "answer to the stakeholder": f"Neither: the corrected figure is {corrected[1]} per 100,000 ({corrected[0]} complaints). September's 48.06 missed late arrivals; October's 39.14 dropped real complaints.",
        "prevention": "A lineage check that warns when a step's parameters change between runs, and a review of the figure before republishing.",
    }
    # END SOLUTION
except NotImplementedError:
    NOTE = {}
md = "## Incident note: R04 August complaint rate\n\n" + "\n".join(f"- **{k}**: {v}" for k, v in NOTE.items())
_ = (B.art("d4_3") / "incident_note.md").write_text(md, encoding="utf-8")
print(md)
B.check(all(x in md for x in ("48.06", "39.14", str(corrected[1]))), "the note gives the two published figures and the corrected one")

# %% [markdown]
# ## ✱ Stretch · A lineage check that would have warned
#
# Before publishing run B, compare each job's parameters with the previous run's lineage and warn on
# any change.

# %%
try:
    # BEGIN SOLUTION
    prev = {e["job"]["name"]: e["run"]["facets"]["params"] for e in lineage["run_a"]}
    for e in lineage["run_b"]:
        p = e["run"]["facets"]["params"]
        if prev.get(e["job"]["name"]) != p:
            print(f"WARNING {e['job']['name']}: parameters changed {prev.get(e['job']['name'])} -> {p}; review the figures before publishing")
    # END SOLUTION
except NotImplementedError:
    print("stretch not done")

# %% [markdown]
# ## Checkpoint
#
# 1. Why recompute one change at a time instead of comparing the two runs directly?
#    <details><summary>Answer</summary>Three changes moved the figure at once, in different directions; only one at a time shows how much each contributed and which one is the defect.</details>
# 2. The October figure was produced by newer code and fresher data. Why is it not the right one?
#    <details><summary>Answer</summary>The new dedupe key removed real complaints. Newer is not more correct: the change has to be checked against what the figure means.</details>
# 3. What would have caught this before publication?
#    <details><summary>Answer</summary>A check on parameter changes between runs, from the lineage, and a review of large changes in a published figure.</details>
#
# **Carry forward.** `artifacts/d4_3/incident_note.md`.
