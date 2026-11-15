# %% [markdown]
# # Lab 4.1 · Steps, a runner and a lock file
#
# Day 4 · Session 1 (From notebook to pipeline) · 25 min · AI-tutor.
#
# Until this month Abdulelah prepared the complaints table in a notebook. Run it twice and you get two
# different tables. You find the four reasons, then use the pipeline's steps (each with explicit inputs
# and outputs), write the runner that calls them and records a run log, and show that two runs give the
# same bytes with the versions the lock file pins.
#
# **Reference state.** `pipeline/prep_notebook.py` (the old notebook as its cells), `pipeline/steps.py`
# (the steps), `pipeline/uv.lock` (the pinned versions) and `data/sources_clean/`.
#
# **Tasks**
# - [ ] 1 · Four sources of nondeterminism (5')
# - [ ] 2 · Steps with explicit inputs and outputs (9')
# - [ ] 3 · A runner that writes a run log (6')
# - [ ] 4 · Two runs, the same bytes, the pinned versions (5')
# - [ ] ✱ Stretch · A task runner for the steps

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

import hashlib
import json
import time
import tomllib
import duckdb
import bayyin as B
import steps
from prep_notebook import CELLS

RAW = (B.DATA / "sources_clean").as_posix()


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]


def run_notebook(order, out: Path) -> dict:
    """Run the old notebook's cells in the given order; return the hash of each file it wrote."""
    out.mkdir(parents=True, exist_ok=True)
    ns = {"RAW": RAW, "OUT": out.as_posix()}
    for i in order:
        exec(CELLS[i], ns)
    return {f.name: sha(f) for f in sorted(out.glob("*.csv"))}


for i, src in CELLS.items():
    print(f"--- cell {i}{src}")

# %% [markdown]
# ## 1 · Four sources of nondeterminism (5')
#
# Monday's run went top to bottom. On Tuesday Abdulelah re-ran cell 3 after editing a comment, then
# carried on. Both runs read the same extract.

# %%
monday = run_notebook([1, 2, 3, 4, 5], B.art("d4_1") / "monday")
time.sleep(1.1)
tuesday = run_notebook([1, 2, 3, 3, 4, 5], B.art("d4_1") / "tuesday")
for f in monday:
    print(f"{f:28s} {monday[f]}  {tuesday[f]}  {'same' if monday[f] == tuesday[f] else 'DIFFERENT'}")

# %% [markdown]
# ✏️ **Exercise** · Name the four causes: for each, the cell and what makes it unrepeatable. Two show
# in the hashes above; two would show on another day or another machine.

# %%
try:
    # BEGIN SOLUTION
    CAUSES = {
        2: "reads the clock: prepared_at differs on every run",
        3: "changes state in place: running the cell twice multiplies the population twice",
        4: "an unseeded shuffle: which copy of a resubmission is kept changes on every run",
        5: "iterates over a set of strings: the column order of the pivot changes with Python's hash seed",
    }
    # END SOLUTION
except NotImplementedError:
    CAUSES = {}
for c, why in CAUSES.items():
    print(f"cell {c}: {why}")
B.check(set(CAUSES) == {2, 3, 4, 5}, "the four cells that make the notebook unrepeatable")

# %% [markdown]
# ## 2 · Steps with explicit inputs and outputs (9')
#
# `pipeline/steps.py` holds the same preparation as functions. Each reads named tables of one DuckDB
# connection, writes named tables, and returns its row counts. None reads the clock, none samples,
# every output is sorted, and the connection uses one thread.
#
# ✏️ **Exercise** · Write `prepare(raw, regions, extract_date)`: open a connection with
# `steps.connect()`, call `extract`, `gate`, `clean`, `dedupe` and `enrich` in order, and return the
# connection and a list of `{"step": name, **counts}`. The extract date is a parameter, not the clock.

# %%
def prepare(raw: Path, regions: Path, extract_date: str):
    # BEGIN SOLUTION
    con = steps.connect()
    log = [{"step": "extract", **steps.extract(con, raw, regions, extract_date)}]
    g = steps.gate(con)
    log.append({"step": "gate", "rows_out": g["rows_out"], "quarantined": g["quarantined"]})
    for name in ("clean", "dedupe", "enrich"):
        log.append({"step": name, **getattr(steps, name)(con)})
    return con, log
    # END SOLUTION


try:
    con, step_log = prepare(B.DATA / "sources_clean", B.DATA / "sources_clean" / "regions.csv", "2026-09-05")
    for s in step_log:
        print(s)
    B.check([s["step"] for s in step_log] == ["extract", "gate", "clean", "dedupe", "enrich"], "five steps in order")
except NotImplementedError:
    print("prepare() not written yet")

# %% [markdown]
# ## 3 · A runner that writes a run log (6')
#
# The run log is what lets anyone answer "which code, which inputs, which versions made this table?"
# months later.
#
# ✏️ **Exercise** · Write `run(out)`: call `prepare`, then `steps.publish(con, out / "published")`,
# and write `out / "run_log.json"` with the input hashes, the steps, the output hashes, the Python and
# DuckDB versions and the hash of `pipeline/uv.lock`.

# %%
def run(out: Path) -> dict:
    raw = B.DATA / "sources_clean"
    # BEGIN SOLUTION
    con, log_steps = prepare(raw, raw / "regions.csv", "2026-09-05")
    pub = steps.publish(con, out / "published")
    log = {"extract_date": "2026-09-05",
           "inputs": {f.name: sha(f) for f in sorted(raw.glob("*.csv*"))},
           "steps": log_steps + [{"step": "publish", **pub}],
           "outputs": {f.name: sha(f) for f in sorted((out / "published").glob("*.csv"))},
           "python": sys.version.split()[0], "duckdb": duckdb.__version__,
           "lock_file_sha256": sha(Path("pipeline/uv.lock"))}
    (out / "run_log.json").write_text(json.dumps(log, indent=1), encoding="utf-8")
    return log
    # END SOLUTION


try:
    log1 = run(B.art("d4_1") / "run1")
    print(json.dumps({k: log1[k] for k in ("inputs", "outputs", "duckdb", "lock_file_sha256")}, indent=1))
except NotImplementedError:
    log1 = None
    print("run() not written yet")

# %% [markdown]
# ## 4 · Two runs, the same bytes, the pinned versions (5')
#
# Run again into another folder, a second later. Then compare what you have installed with what the
# lock file pins: the same code on another DuckDB may order or round differently. On Colab, which installs
# from `requirements-colab.txt` without pins, the last check may fail: that is the point it makes.

# %%
if log1:
    time.sleep(1.1)
    log2 = run(B.art("d4_1") / "run2")
    for f in log1["outputs"]:
        print(f"{f:28s} {log1['outputs'][f]}  {log2['outputs'][f]}")
    B.check(log1["outputs"] == log2["outputs"], "two runs wrote the same bytes")
lock = tomllib.loads(Path("pipeline/uv.lock").read_text(encoding="utf-8"))
pinned = {p["name"]: p["version"] for p in lock["package"] if p["name"] in ("duckdb", "pyyaml")}
print("pinned by pipeline/uv.lock:", pinned, "| installed duckdb:", duckdb.__version__)
B.check(pinned.get("duckdb") == duckdb.__version__, "the DuckDB you ran is the one the lock file pins")

# %% [markdown]
# 🔍 **Look at** the reference runner, `pipeline/run.py`. It does the same, adds the quality gate's
# results, the git commit of the code and a lineage record per step, and runs the contract of Lab 3.4
# before publishing. From here on, the pipeline is run with it:
#
# ```
# cd labs/pipeline
# uv run run.py --raw ../data/sources_clean --regions ../data/sources_clean/regions.csv --out out
# ```

# %%
r = subprocess.run([sys.executable, "pipeline/run.py", "--raw", "data/sources_clean", "--regions", "data/sources_clean/regions.csv",
                    "--out", str(B.art("d4_1") / "reference_run"), "--run-id", "lab41"], capture_output=True, text=True)
print(r.stdout, r.stderr[-500:])
ref_log = json.loads((B.art("d4_1") / "reference_run" / "run_log.json").read_text(encoding="utf-8"))
if log1:
    B.check(ref_log["outputs"]["complaints_prepared.csv"] == log1["outputs"]["complaints_prepared.csv"], "your runner and the reference runner write the same table")

# %% [markdown]
# ## ✱ Stretch · A task runner
#
# A task runner gives each command a name, so nobody has to remember the flags. Write a `Makefile` (or
# a `justfile`) with the targets `clean-run`, `seeded-run` and `test`.

# %%
try:
    # BEGIN SOLUTION
    MAKEFILE = """RUN = uv run run.py --regions ../data/sources_clean/regions.csv

clean-run:
\t$(RUN) --raw ../data/sources_clean --out out/clean --run-id clean

seeded-run:
\t$(RUN) --raw ../data/sources --out out/seeded --run-id seeded; test $$? -eq 2

test: clean-run seeded-run
"""
    (B.art("d4_1") / "Makefile").write_text(MAKEFILE, encoding="utf-8")
    print(MAKEFILE)
    # END SOLUTION
except NotImplementedError:
    print("stretch not done")

# %% [markdown]
# ## Checkpoint
#
# 1. The two runs of your runner wrote the same bytes. Name two things in the steps that make that true.
#    <details><summary>Answer</summary>The extract date is a parameter, not the clock; nothing samples; every output is sorted; one DuckDB thread.</details>
# 2. Why record the hash of the lock file in the run log?
#    <details><summary>Answer</summary>It names the exact versions the run used; a different hash explains a difference that the code alone cannot.</details>
# 3. Cell 3 was harmless on Monday. Why is it still a defect?
#    <details><summary>Answer</summary>A cell that changes its own input gives a different result each time it runs; in a notebook, re-running cells is normal.</details>
#
# **Carry forward.** `pipeline/run.py`, the reference runner, is used in Labs 4.2 to 4.4.
