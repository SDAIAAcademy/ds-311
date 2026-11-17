"""The steps of Bayyin's complaints preparation. Each step reads named tables and writes named tables
in one DuckDB connection, and returns its row counts. Nothing reads the clock, nothing samples, and
every output is sorted, so two runs on the same inputs write the same bytes."""

from __future__ import annotations

from pathlib import Path

import duckdb

from rules import RULES


class Blocked(Exception):
    """A blocking rule failed: nothing is published."""


def count(con, table: str) -> int:
    return con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]


def extract(con, raw: Path, regions: Path, extract_date: str) -> dict:
    """Load the four source tables as text, give every row a stable row id (rid)."""
    con.execute("CREATE OR REPLACE TABLE params AS SELECT CAST(? AS DATE) AS extract_date", [extract_date])
    for name, file in (("complaints", "complaints_extract.csv.gz"), ("actions", "case_actions.csv.gz"), ("merchants", "merchants.csv")):
        con.execute(f"""CREATE OR REPLACE TABLE {name} AS
            SELECT row_number() OVER () AS rid, * FROM read_csv(?, all_varchar = true, header = true)""", [str(raw / file)])
    con.execute("CREATE OR REPLACE TABLE regions AS SELECT * FROM read_csv(?, header = true, all_varchar = true)", [str(regions)])
    con.execute("CREATE OR REPLACE TABLE regions AS SELECT region_code, name_en, CAST(population AS BIGINT) AS population, version FROM regions")
    return {"rows_in": count(con, "complaints"), "rows_out": count(con, "complaints"),
            "actions": count(con, "actions"), "merchants": count(con, "merchants"),
            "regions_version": con.execute("SELECT min(version) FROM regions").fetchone()[0]}


def gate(con, rules=RULES) -> dict:
    """Run every rule. Quarantine failing rows; stop on a failed blocking rule or a quarantine above its limit."""
    con.execute("CREATE OR REPLACE TABLE quarantine (tbl VARCHAR, rid BIGINT, rule_id VARCHAR)")
    results, stop = [], []
    for r in rules:
        failing = con.execute(f"SELECT count(*) FROM ({r['sql']})").fetchone()[0]
        total = count(con, r["table"])
        rate = failing / total if total else 0.0
        status = "pass" if rate <= r["max_rate"] else "fail"
        if r["severity"] == "quarantine" and failing:
            con.execute(f"INSERT INTO quarantine SELECT '{r['table']}', rid, '{r['id']}' FROM ({r['sql']})")
        if status == "fail" and r["severity"] in ("block", "quarantine"):
            stop.append(r["id"])
        results.append(dict(rule=r["id"], dimension=r["dimension"], severity=r["severity"], owner=r["owner"],
                            failing=failing, rate=round(rate, 5), max_rate=r["max_rate"], status=status))
    for t in ("complaints", "actions", "merchants"):
        con.execute(f"DELETE FROM {t} WHERE rid IN (SELECT rid FROM quarantine WHERE tbl = '{t}')")
    q = con.execute("SELECT rule_id, count(*) FROM quarantine GROUP BY rule_id ORDER BY rule_id").fetchall()
    out = {"results": results, "quarantined": {k: v for k, v in q}, "blocked_by": stop,
           "rows_out": count(con, "complaints")}
    if stop:
        raise Blocked(out)
    return out


def clean(con) -> dict:
    """Types and trimmed text. Runs after the gate, so every cast here is known to succeed."""
    n = count(con, "complaints")
    con.execute("""CREATE OR REPLACE TABLE complaints AS SELECT
        rid, complaint_id, CAST(received_date AS DATE) AS received_date, channel, nullif(trim(merchant_ref), '') AS merchant_ref,
        trim(merchant_name_raw) AS merchant_name_raw, product, category_code AS category,
        CAST(amount_sar AS DECIMAL(12, 2)) AS amount_sar, region_code, status,
        TRY_CAST(nullif(closed_date, '') AS DATE) AS closed_date, customer_key
        FROM complaints""")
    return {"rows_in": n, "rows_out": count(con, "complaints")}


def dedupe(con, key=("customer_key", "merchant_name_raw", "product"), window_days: int = 1) -> dict:
    """Drop resubmissions: the same customer, merchant and product within `window_days`; keep the first."""
    n = count(con, "complaints")
    k = ", ".join(key)
    con.execute(f"""CREATE OR REPLACE TABLE complaints AS
        SELECT * EXCLUDE (prev) FROM (
          SELECT *, lag(received_date) OVER (PARTITION BY {k} ORDER BY received_date, complaint_id) AS prev FROM complaints)
        WHERE prev IS NULL OR received_date - prev > {int(window_days)}""")
    return {"rows_in": n, "rows_out": count(con, "complaints"), "params": {"key": list(key), "window_days": window_days}}


def enrich(con) -> dict:
    n = count(con, "complaints")
    con.execute("""CREATE OR REPLACE TABLE prepared AS SELECT
        c.complaint_id, c.received_date, strftime(c.received_date, '%Y-%m') AS month, c.channel,
        m.merchant_id, c.category, c.amount_sar, c.region_code, c.status,
        CASE WHEN c.closed_date IS NULL THEN NULL ELSE c.closed_date - c.received_date END AS days_to_close
        FROM complaints c LEFT JOIN merchants m ON m.merchant_id = c.merchant_ref
        ORDER BY c.complaint_id""")
    return {"rows_in": n, "rows_out": count(con, "prepared"),
            "params": {"regions_version": con.execute("SELECT min(version) FROM regions").fetchone()[0]}}


def publish(con, out: Path) -> dict:
    """Write the prepared table and the monthly rate by region. Written to a temporary name, then renamed."""
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "complaints_prepared.csv.tmp"
    con.execute(f"COPY (SELECT * FROM prepared ORDER BY complaint_id) TO '{tmp.as_posix()}' (HEADER, DELIMITER ',')")
    tmp.replace(out / "complaints_prepared.csv")
    tmp = out / "monthly_rate.csv.tmp"
    con.execute(f"""COPY (SELECT p.month, p.region_code, count(*) AS complaints,
                       round(count(*) / any_value(r.population) * 100000, 2) AS rate_per_100k
                FROM prepared p JOIN regions r USING (region_code)
                GROUP BY p.month, p.region_code ORDER BY p.month, p.region_code) TO '{tmp.as_posix()}' (HEADER, DELIMITER ',')""")
    tmp.replace(out / "monthly_rate.csv")
    q = out / "quarantine.csv"
    con.execute(f"COPY (SELECT * FROM quarantine ORDER BY tbl, rid, rule_id) TO '{q.as_posix()}' (HEADER, DELIMITER ',')")
    return {"rows_in": count(con, "prepared"), "rows_out": count(con, "prepared")}


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("SET threads TO 1")  # one thread: the same row order on every machine
    return con
