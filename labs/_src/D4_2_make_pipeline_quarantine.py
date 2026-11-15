# %% [markdown]
# # Lab 4.2 · Quarantine and block
#
# Day 4 · Session 2 (Gates in the pipeline) · 25 min · AI-tutor.
#
# Day 3's rules now run inside the pipeline, after extraction and before anything is published. You
# write the quarantine step for one rule, run the pipeline on the seeded extract (stopped, nothing
# published) and on a corrected August batch (published, bad rows set aside), repeat both from a clean
# checkout of the repository, and read the CI workflow that does the same on every push.
#
# **Reference state.** `pipeline/` (steps, rules, contract, runner), `pipeline/ci/pipeline.yml`,
# `data/sources/` (seeded) and `data/sources_clean/`.
#
# **Tasks**
# - [ ] 1 · Quarantine rows with a reason (7')
# - [ ] 2 · Stop on a blocking rule; publish only after every gate (7')
# - [ ] 3 · From a clean checkout: pass on clean, fail on the defect (7')
# - [ ] 4 · The CI workflow that runs it (4')
# - [ ] ✱ Stretch · A warning that becomes a block after three runs

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

import gzip
import json
import shutil
import tempfile
import pandas as pd
import yaml
import bayyin as B
import steps
from rules import RULES

pd.set_option("display.width", 160)
LABS = Path.cwd()

# %% [markdown]
# ## 1 · Quarantine rows with a reason (7')
#
# A quarantined row leaves the table but not the record: it goes to a `quarantine` table with the rule
# that caught it, so someone can fix it at the source and nothing is lost silently.
#
# ✏️ **Exercise** · Write the two statements for one rule: insert its failing rows into `quarantine`
# with the table name, the row id and the rule id; then delete them from their table.

# %%
con = steps.connect()
steps.extract(con, B.DATA / "sources", B.DATA / "sources" / "regions.csv", "2026-09-05")
con.execute("CREATE OR REPLACE TABLE quarantine (tbl VARCHAR, rid BIGINT, rule_id VARCHAR)")
before = steps.count(con, "complaints")


def quarantine(con, rule: dict) -> None:
    # BEGIN SOLUTION
    con.execute(f"INSERT INTO quarantine SELECT '{rule['table']}', rid, '{rule['id']}' FROM ({rule['sql']})")
    con.execute(f"DELETE FROM {rule['table']} WHERE rid IN (SELECT rid FROM quarantine WHERE rule_id = '{rule['id']}')")
    # END SOLUTION


try:
    for r in RULES:
        if r["severity"] == "quarantine":
            quarantine(con, r)
    q = con.execute("SELECT rule_id, count(*) AS rows FROM quarantine GROUP BY 1 ORDER BY 1").df()
    print(q.to_string(index=False))
    print(before, "complaints before,", steps.count(con, "complaints"), "after")
    B.check(con.execute("SELECT count(*) FROM quarantine WHERE rule_id IS NULL").fetchone()[0] == 0 and len(q) == 7,
            "seven quarantine rules set rows aside, each row with the rule that caught it")
except NotImplementedError:
    print("quarantine() not written yet")

# %% [markdown]
# 🔍 **Look at** I01: 970 orphan actions here, against 150 in Lab 3.2. Deleting a quarantined complaint
# orphans its actions, so a rule run after a delete judges a different table. `steps.gate` runs every
# rule on the untouched tables first and deletes only at the end: the counts in task 2 match Lab 3.2.

# %% [markdown]
# ## 2 · Stop on a blocking rule; publish only after every gate (7')
#
# The runner calls the steps in order and writes `published/` only at the end. A blocking rule raises
# `Blocked` before that, so a stopped run leaves a run log and nothing a report could pick up.
#
# ✏️ **Exercise** · Write `run_pipeline(raw, out)`: run `pipeline/run.py` as a separate process,
# return its exit code and its run log. Then build `corrected/`: the seeded extract with the August app
# amounts divided by 100 (the vendor's fix), and run the pipeline on it.

# %%
def run_pipeline(raw: Path, out: Path, cwd: Path = LABS) -> tuple[int, dict]:
    # BEGIN SOLUTION
    shutil.rmtree(out, ignore_errors=True)
    r = subprocess.run([sys.executable, "pipeline/run.py", "--raw", str(raw), "--regions", str(raw / "regions.csv"),
                        "--out", str(out), "--run-id", out.name], cwd=cwd, capture_output=True, text=True)
    print(r.stdout.strip(), r.stderr[-300:])
    return r.returncode, json.loads((out / "run_log.json").read_text(encoding="utf-8"))
    # END SOLUTION


def corrected_extract(dst: Path) -> Path:
    dst.mkdir(parents=True, exist_ok=True)
    for f in (B.DATA / "sources").iterdir():
        shutil.copy(f, dst / f.name)
    # BEGIN SOLUTION
    df = pd.read_csv(B.DATA / "sources" / "complaints_extract.csv.gz", dtype=str, keep_default_na=False)
    batch = (df.channel == "app") & df.received_date.str.startswith("2026-08")
    df.loc[batch, "amount_sar"] = (pd.to_numeric(df.loc[batch, "amount_sar"]) / 100).map(lambda v: f"{v:.2f}")
    with gzip.open(dst / "complaints_extract.csv.gz", "wt", encoding="utf-8", newline="") as f:
        df.to_csv(f, index=False)
    # END SOLUTION
    return dst


out = B.art("d4_2")
try:
    code_s, log_s = run_pipeline(B.DATA / "sources", out / "seeded")
    B.check(code_s == 2 and log_s["blocked_by"] == ["A01", "A02"] and not (out / "seeded" / "published").exists(),
            "the seeded extract is stopped by A01 and A02, and nothing is published")
    code_c, log_c = run_pipeline(corrected_extract(out / "corrected_src"), out / "corrected")
    print("quarantined:", log_c["quarantined"])
    B.check(code_c == 0 and (out / "corrected" / "published" / "complaints_prepared.csv").exists(),
            "the corrected batch passes the gates and the contract, and is published")
except NotImplementedError:
    print("not written yet")

# %% [markdown]
# ## 3 · From a clean checkout: pass on clean, fail on the defect (7')
#
# "It works on my laptop" is not evidence: a file you forgot to commit, or a package only you have,
# will break the pipeline for everyone else. Clone the repository into an empty folder and run there.
#
# ✏️ **Exercise** · Clone, run the pipeline on the clean extract and on the seeded one inside the
# clone, and compare the clean table's hash with your own run's.

# %%
try:
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip()
except Exception:
    top = None
if top:
    tmp = Path(tempfile.mkdtemp(prefix="ds311-"))
    try:
        # BEGIN SOLUTION
        subprocess.run(["git", "clone", "-q", top, str(tmp / "repo")], check=True)
        clone_labs = tmp / "repo" / "labs"
        code_cc, log_cc = run_pipeline(clone_labs / "data" / "sources_clean", tmp / "clean", cwd=clone_labs)
        code_cs, log_cs = run_pipeline(clone_labs / "data" / "sources", tmp / "seeded", cwd=clone_labs)
        _, log_here = run_pipeline(B.DATA / "sources_clean", out / "clean")
        print("code version in the clone:", log_cc["code_version"])
        B.check(code_cc == 0 and code_cs == 2, "from a clean checkout: clean publishes, seeded is blocked")
        B.check(log_cc["outputs"] == log_here["outputs"], "the clone and this folder publish the same bytes")
        # END SOLUTION
    except NotImplementedError:
        print("not written yet")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
else:
    print("this folder is not a git checkout: clone the course repository to do this task")

# %% [markdown]
# ## 4 · The CI workflow that runs it (4')
#
# `pipeline/ci/pipeline.yml` is a GitHub Actions workflow that does task 3 on every push.
#
# ✏️ **Exercise** · Read it and fill `CI`: the command that installs the pinned versions, and what each
# of the two runs must end with.

# %%
wf = yaml.safe_load((LABS / "pipeline" / "ci" / "pipeline.yml").read_text(encoding="utf-8"))
for s in wf["jobs"]["run"]["steps"]:
    print("-", s.get("name", s.get("uses")))
try:
    # BEGIN SOLUTION
    CI = {"install": "uv sync --locked", "clean": "exit 0, published", "seeded": "exit 2, nothing published"}
    # END SOLUTION
except NotImplementedError:
    CI = {}
text = (LABS / "pipeline" / "ci" / "pipeline.yml").read_text(encoding="utf-8")
B.check(CI.get("install", "-") in text and "2" in CI.get("seeded", ""), "the workflow installs from the lock file and expects the seeded run to stop")

# %% [markdown]
# ## ✱ Stretch · A warning that becomes a block after three runs
#
# U02 (registry duplicates) is a warning. If the registry team never fixes it, a warning nobody acts on
# is noise. Escalate: a warning that fails in three consecutive runs blocks the fourth.

# %%
try:
    # BEGIN SOLUTION
    def escalate(history: list[dict], rule: str, runs: int = 3) -> str:
        last = [h["rules"].get(rule) for h in history[-runs:]]
        return "block" if len(last) == runs and all(s == "fail" for s in last) else "warn"
    hist = [{"rules": {"U02": "fail"}}] * 3
    print("U02 after three failing runs:", escalate(hist, "U02"), "| after two:", escalate(hist[:2], "U02"))
    # END SOLUTION
except NotImplementedError:
    print("stretch not done")

# %% [markdown]
# ## Checkpoint
#
# 1. Why is the corrected batch published while 927 complaints and 150 actions sit in quarantine?
#    <details><summary>Answer</summary>Each quarantine rule stayed under its owner's threshold; the rows that are left are right, and the set-aside rows are kept with their reasons.</details>
# 2. The seeded run stopped. What does Hatoon's report see?
#    <details><summary>Answer</summary>Last month's published table, unchanged: nothing was written to published/. The run log says why.</details>
# 3. What does the clean checkout prove that your own folder cannot?
#    <details><summary>Answer</summary>That everything the pipeline needs is committed and pinned: no forgotten file, no package only you have.</details>
#
# **Carry forward.** The run logs in `artifacts/d4_2/`; Lab 4.4 writes the datasheet from a run log.
