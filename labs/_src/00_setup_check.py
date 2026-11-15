# %% [markdown]
# # Setup check · DS-311 Data Quality, Labelling and Pipelines for Analysis
#
# Pre-work, about 10 minutes. Run every cell once before Day 1. It imports every package the labs
# use, reads one file of each kind, runs a two-line DuckDB query, and tries the one model call of the
# course (Lab 2.4). Every line should print ✅; a ❌ says what to fix.

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

# %%
import importlib

for name in ["pandas", "duckdb", "pandera", "yaml", "rapidfuzz"]:
    try:
        m = importlib.import_module(name)
        print("✅", name, getattr(m, "__version__", ""))
    except ImportError as e:
        print("❌", name, "missing: run `uv sync` in labs/ (or the first cell in Colab)", e)
print("python", sys.version.split()[0])

# %%
import bayyin as B

corpus = B.read("corpus/complaints_text.csv.gz")
B.check(len(corpus) == 30000, f"complaint texts: {len(corpus):,} rows")
pilot = B.read("pilot/pilot_round1.csv")
B.check(len(pilot) == 300, f"pilot labels: {len(pilot)} complaints x 3 raters")
ops = B.read("ops/ops_round.csv")
B.check(len(ops) > 2000, f"operations round: {len(ops):,} labels")

# %%
import duckdb

con = duckdb.connect()
n = con.execute("SELECT count(*) FROM read_csv('data/sources/complaints_extract.csv.gz', all_varchar = true)").fetchone()[0]
B.check(n == 30300, f"DuckDB reads the seeded extract: {n:,} rows")

# %% [markdown]
# ## The model call (optional)
#
# Lab 2.4 sends masked complaints to a free hosted model through a chat-completions endpoint. Put a
# free OpenRouter key in `labs/.env` as `OPENROUTER_API_KEY=...` (or in Colab's Secrets). Without a
# key, the lab runs on a scripted stand-in and says so: nothing else in the course needs a model.

# %%
reply = B.chat([{"role": "user", "content": "Reply with the single word OK."}], max_tokens=5)
src = B.LAST_SOURCE["source"]
if src == "stand-in":
    print("ℹ️ no working key: Lab 2.4 will use the scripted stand-in")
else:
    B.check(bool(reply.strip()), f"the model answered through {src}: {reply.strip()[:20]}")
