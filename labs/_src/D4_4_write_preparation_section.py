# %% [markdown]
# # Lab 4.4 · The datasheet's preparation section
#
# Day 4 · Session 4 (Handing over prepared data) · 25 min · AI-tutor: an assistant may help with
# wording, never with the numbers.
#
# Hatoon will hand `complaints_prepared` to analysts who were not in the room this week. A datasheet
# (Gebru et al.) answers their questions; its "collection, preprocessing and labelling" part is yours.
# You write it from a run log, the rule results and the agreement report, then check mechanically that
# every number in it appears in those sources.
#
# **Reference state.** A pipeline run on the corrected September extract (made here, as in Lab 4.2);
# `data/reference/agreement_r1_r2.csv` (the pilot's agreement by category and variety, rounds 1 and 2);
# `pipeline/contract.odcs.yaml`.
#
# **Tasks**
# - [ ] 1 · What a user of the table needs to know (4')
# - [ ] 2 · Fill the section from the run log and rule results (9')
# - [ ] 3 · Agreement by variety, and the known limits (7')
# - [ ] 4 · Every number traced to the run (5')
# - [ ] ✱ Stretch · The contract and the datasheet name the same columns

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

import gzip
import json
import re
import shutil
import pandas as pd
import yaml
import bayyin as B

out = B.art("d4_4")
src = out / "corrected_src"
src.mkdir(parents=True, exist_ok=True)
for f in (B.DATA / "sources").iterdir():
    shutil.copy(f, src / f.name)
df = pd.read_csv(B.DATA / "sources" / "complaints_extract.csv.gz", dtype=str, keep_default_na=False)
batch = (df.channel == "app") & df.received_date.str.startswith("2026-08")
df.loc[batch, "amount_sar"] = (pd.to_numeric(df.loc[batch, "amount_sar"]) / 100).map(lambda v: f"{v:.2f}")
with gzip.open(src / "complaints_extract.csv.gz", "wt", encoding="utf-8", newline="") as f:
    df.to_csv(f, index=False)
r = subprocess.run([sys.executable, "pipeline/run.py", "--raw", str(src), "--regions", str(src / "regions.csv"),
                    "--out", str(out / "run"), "--run-id", "2026-09-corrected"], capture_output=True, text=True)
print(r.stdout.strip(), r.stderr[-300:])
LOG = json.loads((out / "run" / "run_log.json").read_text(encoding="utf-8"))
AGREE = pd.read_csv(B.REF / "agreement_r1_r2.csv", index_col=0)
print(json.dumps({k: LOG[k] for k in ("run_id", "extract_date", "code_version", "steps", "quarantined", "contract")}, indent=1)[:1800])

# %% [markdown]
# ## 1 · What a user of the table needs to know (4')
#
# The datasheet questions for this part ask: what preprocessing was done, what was removed and why,
# how the labels were made and how reliable they are, and whether the raw data was kept.
#
# ✏️ **Exercise** · List the questions an analyst would ask before computing a rate from this table,
# at least five, in `QUESTIONS`.

# %%
try:
    # BEGIN SOLUTION
    QUESTIONS = [
        "Which extract and which code produced this table?",
        "How many rows were removed, by which rule, and where are they?",
        "How were duplicates and resubmissions treated?",
        "How were the categories labelled, and how far do raters agree, by language variety?",
        "Which population figures are used for the rate?",
        "What is known to be weak or missing?",
    ]
    # END SOLUTION
except NotImplementedError:
    QUESTIONS = []
B.check(len(QUESTIONS) >= 5, f"{len(QUESTIONS)} questions")

# %% [markdown]
# ## 2 · Fill the section from the run log and rule results (9')
#
# Never type a number: take each from `LOG`. The rows a step removed are its `rows_in` minus its
# `rows_out`.
#
# ✏️ **Exercise** · Complete `facts`, the numbers the section uses, then `section_prep(facts)`.

# %%
steps_ = {s["step"]: s for s in LOG["steps"]}
try:
    # BEGIN SOLUTION
    facts = {
        "extract_rows": steps_["extract"]["rows_in"],
        "quarantined_complaints": steps_["gate"]["rows_in"] - steps_["gate"]["rows_out"],
        "by_rule": {k: v for k, v in LOG["quarantined"].items() if k != "I01"},
        "orphan_actions": LOG["quarantined"].get("I01", 0),
        "resubmissions": steps_["dedupe"]["rows_in"] - steps_["dedupe"]["rows_out"],
        "published_rows": steps_["publish"]["rows_out"],
        "regions_version": steps_["enrich"]["params"]["regions_version"],
        "contract_checks": LOG["contract"]["checks"],
    }
    # END SOLUTION
except NotImplementedError:
    facts = {}


def section_prep(f: dict) -> str:
    # BEGIN SOLUTION
    rules = ", ".join(f"{k} {v:,}" for k, v in sorted(f["by_rule"].items()))
    return (f"### Preprocessing and cleaning\n\n"
            f"- Source: the portal extract of {LOG['extract_date']}, {f['extract_rows']:,} complaints; pipeline commit {LOG['code_version']}, run {LOG['run_id']}.\n"
            f"- Quality gate: {f['quarantined_complaints']:,} complaints set aside in quarantine with the rule that caught them ({rules}); "
            f"{f['orphan_actions']:,} case actions without a complaint also set aside. The rows are kept in quarantine.csv, not deleted.\n"
            f"- The August app batch arrived in halalas and was corrected by the vendor before this run; the accuracy rules A01 and A02 pass.\n"
            f"- Resubmissions: {f['resubmissions']:,} complaints removed as the same customer, merchant and product within one day; repeat complaints about other products are kept.\n"
            f"- Published: {f['published_rows']:,} complaints. Rates use the regions table version {f['regions_version']}.\n"
            f"- The table met all {f['contract_checks']} checks of its data contract (contract.odcs.yaml, version 1.0.0) before publishing.\n")
    # END SOLUTION


try:
    prep_md = section_prep(facts)
    print(prep_md)
except (NotImplementedError, KeyError):
    prep_md = ""

# %% [markdown]
# ## 3 · Agreement by variety, and the known limits (7')
#
# The category was labelled under guideline v1.1. Report agreement where it is weakest, with the
# variety, not only the overall figure.
#
# ✏️ **Exercise** · Write `section_labels()` from `AGREE` (round 2): the overall alpha, the four
# varieties, the weakest category; then at least three known limits.

# %%
print(AGREE.to_string())


def section_labels() -> str:
    # BEGIN SOLUTION
    r2 = AGREE["round 2"]
    var = {i.split()[1]: r2[i] for i in r2.index if i.startswith("variety")}
    cats = r2[[c for c in B.CATS]]
    weakest = cats.idxmin()
    lines = [f"### Labelling\n",
             f"- Category labelled under guideline v1.1; pilot round 2, three raters on 300 complaints: Krippendorff's alpha {r2['ALL']}.",
             "- By language variety: " + ", ".join(f"{k} {v}" for k, v in var.items()) + ".",
             f"- Weakest category: {weakest} (alpha {cats[weakest]}).",
             "\n### Known limits\n",
             f"- Mixed Arabic-English complaints have the lowest agreement ({var['mixed']}); treat category shares in mixed text with care.",
             f"- {weakest} is often confused with DEFECT; its counts are the least reliable.",
             "- Complaints without a region are quarantined, not imputed: regional rates slightly understate the total.",
             "- Merchant ids come from the portal; complaints that give only a merchant name have no merchant id here."]
    return "\n".join(lines) + "\n"
    # END SOLUTION


try:
    labels_md = section_labels()
    print(labels_md)
except NotImplementedError:
    labels_md = ""
section = prep_md + "\n" + labels_md
(out / "datasheet_preparation.md").write_text(section, encoding="utf-8")

# %% [markdown]
# ## 4 · Every number traced to the run (5')
#
# A datasheet with one wrong number loses the reader's trust in all of them. Check mechanically: every
# number in the section must appear in the run log (or be the rows a step removed), the agreement
# report or the contract.
#
# ✏️ **Exercise** · Write `untraced(text)`: find each number in the text and return those that are in
# none of the sources.

# %%
def numbers_in(obj) -> set[str]:
    s = json.dumps(obj, ensure_ascii=False) if not isinstance(obj, str) else obj
    return {n.replace(",", "") for n in re.findall(r"\d[\d,]*(?:\.\d+)?", s)}


SOURCES = numbers_in(LOG) | numbers_in(AGREE.to_csv()) | numbers_in((Path("pipeline") / "contract.odcs.yaml").read_text(encoding="utf-8"))
SOURCES |= {"1.1", "300", "3"}  # the guideline version and the pilot's design, from Day 1
SOURCES |= {str(s["rows_in"] - s["rows_out"]) for s in LOG["steps"] if "rows_in" in s}  # rows each step removed


def untraced(text: str) -> list[str]:
    # BEGIN SOLUTION
    text = re.sub(r"\b[A-Z]\d{2}\b", "", text)  # rule ids such as C01 are names, not numbers
    return sorted(n for n in numbers_in(text) if n not in SOURCES)
    # END SOLUTION


try:
    missing = untraced(section)
    print("numbers not found in any source:", missing)
    B.check(section != "\n" and not missing, "every number in the section is traced to the run, the agreement report or the contract")
except NotImplementedError:
    print("untraced() not written yet")

# %% [markdown]
# ## ✱ Stretch · The contract and the datasheet name the same columns
#
# The datasheet should describe each published column; the contract already does. Compare them.

# %%
try:
    # BEGIN SOLUTION
    contract_cols = [p["name"] for p in yaml.safe_load(Path("pipeline/contract.odcs.yaml").read_text(encoding="utf-8"))["schema"][0]["properties"]]
    table_cols = list(pd.read_csv(out / "run" / "published" / "complaints_prepared.csv", nrows=1).columns)
    print("in the table, not in the contract:", sorted(set(table_cols) - set(contract_cols)))
    print("in the contract, not in the table:", sorted(set(contract_cols) - set(table_cols)))
    B.check(contract_cols == table_cols, "the contract and the published table list the same columns in the same order")
    # END SOLUTION
except NotImplementedError:
    print("stretch not done")

# %% [markdown]
# ## Checkpoint
#
# 1. Why take every number from the run log instead of typing it?
#    <details><summary>Answer</summary>A typed number goes stale on the next run; a number taken from the log can be regenerated and checked.</details>
# 2. Why report agreement by variety and not only overall?
#    <details><summary>Answer</summary>The overall alpha hides that mixed text is the weakest: an analyst using mixed-text complaints needs that figure.</details>
# 3. The section says complaints without a region were quarantined. What does that do to the rates?
#    <details><summary>Answer</summary>Regional rates slightly understate the total; the limit says so, and the quarantined rows can be counted.</details>
#
# **Carry forward.** `artifacts/d4_4/datasheet_preparation.md`: the capstone's README has the same section
# for Al-Ghadaf.
