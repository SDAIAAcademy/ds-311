"""Run the ODCS contract of the prepared table (contract.odcs.yaml) against the table before it is published.

Each property: the column is present, its type is the promised physicalType, `required` means no NULLs, and each
quality clause (library metric or `type: sql`) is compiled to one query whose number the operator judges.
Columns the contract does not name are allowed: an added column breaks no consumer."""

from __future__ import annotations

from pathlib import Path

import yaml

OPS = {"mustBe": lambda v, t: v == t, "mustNotBe": lambda v, t: v != t, "mustBeGreaterThan": lambda v, t: v > t,
       "mustBeGreaterOrEqualTo": lambda v, t: v >= t, "mustBeLessThan": lambda v, t: v < t, "mustBeLessOrEqualTo": lambda v, t: v <= t}


def compile_clause(table: str, column: str | None, c: dict) -> str:
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


def check(con, path: Path, table: str = "prepared") -> list[dict]:
    """One row per check: name, value, expected, status."""
    obj = yaml.safe_load(Path(path).read_text(encoding="utf-8"))["schema"][0]
    have = dict(con.execute(f"SELECT column_name, column_type FROM (DESCRIBE {table})").fetchall())
    rows = []
    for p in obj["properties"]:
        col = p["name"]
        if col not in have:
            rows.append(dict(check=f"{col}: present", value=None, expected="present", status="fail"))
            continue
        same = p["physicalType"].replace(" ", "") == have[col].replace(" ", "")
        rows.append(dict(check=f"{col}: type", value=have[col], expected=p["physicalType"], status="pass" if same else "fail"))
        if not same:
            continue
        clauses = ([dict(metric="nullValues", mustBe=0)] if p.get("required") else []) + p.get("quality", [])
        for c in clauses:
            v = con.execute(compile_clause(table, col, c)).fetchone()[0]
            op = next(k for k in OPS if k in c)
            rows.append(dict(check=f"{col}: {c.get('metric', 'sql')} {op} {c[op]}", value=v, expected=c[op], status="pass" if OPS[op](v, c[op]) else "fail"))
    for c in obj.get("quality", []):
        v = con.execute(compile_clause(table, None, c)).fetchone()[0]
        op = next(k for k in OPS if k in c)
        rows.append(dict(check=f"table: {c.get('metric', 'sql')} {op} {c[op]}", value=v, expected=c[op], status="pass" if OPS[op](v, c[op]) else "fail"))
    return rows
