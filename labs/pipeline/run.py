"""Run Bayyin's complaints preparation from raw extracts to the analysis-ready table.

    uv run run.py --raw ../data/sources_clean --regions ../data/sources_clean/regions.csv --out out --extract-date 2026-09-05

Exit code 0: published. Exit code 2: stopped by a blocking rule or a failed contract check, nothing published.
Writes <out>/run_log.json and <out>/lineage.jsonl in every case.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

import duckdb

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import steps  # noqa: E402
import contract  # noqa: E402


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def code_version() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=HERE, capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "uncommitted"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, type=Path)
    ap.add_argument("--regions", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--extract-date", default="2026-09-05")
    ap.add_argument("--run-id", default="run")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    lock = HERE / "uv.lock"
    log = {"run_id": a.run_id, "extract_date": a.extract_date, "code_version": code_version(),
           "lock_file_sha256": sha(lock) if lock.exists() else None,
           "python": platform.python_version(), "duckdb": duckdb.__version__,
           "inputs": {f.name: sha(f) for f in sorted(a.raw.glob("*.csv*"))} | {"regions": sha(a.regions)},
           "steps": [], "status": "running"}
    con = steps.connect()
    events = []

    def record(name, info):
        log["steps"].append({"step": name, **info})
        events.append({"eventType": "COMPLETE", "eventDate": a.extract_date,
                       "run": {"runId": f"{a.run_id}-{name}", "facets": {"parent": a.run_id, "code_version": log["code_version"], "params": info.get("params", {})}},
                       "job": {"namespace": "bayyin-prep", "name": name},
                       "outputs": [{"namespace": "bayyin-prep", "name": f"complaints_{name}", "facets": {"rows": info.get("rows_out")}}]})

    code = 0
    try:
        record("extract", steps.extract(con, a.raw, a.regions, a.extract_date))
        g = steps.gate(con)
        log["rules"] = g["results"]
        log["quarantined"] = g["quarantined"]
        record("gate", {"rows_in": log["steps"][-1]["rows_out"], "rows_out": g["rows_out"]})
        record("clean", steps.clean(con))
        record("dedupe", steps.dedupe(con))
        record("enrich", steps.enrich(con))
        checks = contract.check(con, HERE / "contract.odcs.yaml")
        log["contract"] = {"checks": len(checks), "failed": [c["check"] for c in checks if c["status"] == "fail"]}
        if log["contract"]["failed"]:
            raise steps.Blocked({"results": log["rules"], "quarantined": log["quarantined"], "blocked_by": ["contract"]})
        record("publish", steps.publish(con, a.out / "published"))
        log["outputs"] = {f.name: sha(f) for f in sorted((a.out / "published").glob("*.csv"))}
        log["status"] = "published"
    except steps.Blocked as e:
        info = e.args[0]
        log["rules"] = info["results"]
        log["quarantined"] = info["quarantined"]
        log["status"] = "blocked"
        log["blocked_by"] = info["blocked_by"]
        events.append({"eventType": "FAIL", "eventDate": a.extract_date, "run": {"runId": f"{a.run_id}-gate"},
                       "job": {"namespace": "bayyin-prep", "name": "gate"}, "facets": {"blocked_by": info["blocked_by"]}})
        code = 2
    (a.out / "run_log.json").write_text(json.dumps(log, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    (a.out / "lineage.jsonl").write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events), encoding="utf-8", newline="\n")
    print(f"{a.run_id}: {log['status']}" + (f" by {', '.join(log.get('blocked_by', []))}" if code else ""))
    return code


if __name__ == "__main__":
    sys.exit(main())
