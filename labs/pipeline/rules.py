"""Quality rules for Bayyin's complaints preparation, each with the fields the NDMO Data Quality domain
asks of a rule: an owner, a business description, a dimension, the attributes it checks and a metric.

A rule is a SQL query that returns the keys of the failing rows. `max_rate` is the share of failing
rows the owner accepts. Severity says what happens:
  warn        a failure is logged, the run goes on
  quarantine  failing rows are moved to the quarantine table with the rule id; above max_rate the run stops
  block       above max_rate the run stops before anything is published
"""

RULES = [
    dict(id="U01", dimension="uniqueness", owner="Abdulelah Al-Batal", table="complaints", key="rid",
         description="One row per complaint id: a second copy of an id is an export fault",
         attributes=["complaint_id"], severity="quarantine", max_rate=0.005,
         sql="SELECT rid FROM (SELECT rid, row_number() OVER (PARTITION BY complaint_id ORDER BY rid) AS k FROM complaints) WHERE k > 1"),
    dict(id="C01", dimension="completeness", owner="Hatoon Al-Furaih", table="complaints", key="rid",
         description="Every complaint has a region: the monthly rate is published by region",
         attributes=["region_code"], severity="quarantine", max_rate=0.03,
         sql="SELECT rid FROM complaints WHERE region_code IS NULL OR trim(region_code) = ''"),
    dict(id="V01", dimension="validity", owner="Hatoon Al-Furaih", table="complaints", key="rid",
         description="The region code is one of the thirteen in the regions table",
         attributes=["region_code"], severity="quarantine", max_rate=0.03,
         sql="SELECT rid FROM complaints WHERE coalesce(trim(region_code), '') <> '' AND region_code NOT IN (SELECT region_code FROM regions)"),
    dict(id="V02", dimension="validity", owner="Khulood Bin Saedan", table="complaints", key="rid",
         description="The category code is one of the six codes of the guideline",
         attributes=["category_code"], severity="quarantine", max_rate=0.01,
         sql="SELECT rid FROM complaints WHERE category_code NOT IN ('REFUND','DEFECT','DELIVERY','PRICE','AD','WARRANTY')"),
    dict(id="V03", dimension="validity", owner="Abdulelah Al-Batal", table="complaints", key="rid",
         description="No complaint is received after the extract was taken",
         attributes=["received_date"], severity="quarantine", max_rate=0.001,
         sql="SELECT rid FROM complaints WHERE TRY_CAST(received_date AS DATE) IS NULL OR CAST(received_date AS DATE) > (SELECT extract_date FROM params)"),
    dict(id="K01", dimension="consistency", owner="Abdulelah Al-Batal", table="complaints", key="rid",
         description="A complaint is closed on or after the day it was received",
         attributes=["received_date", "closed_date"], severity="quarantine", max_rate=0.005,
         sql="SELECT rid FROM complaints WHERE coalesce(closed_date, '') <> '' AND TRY_CAST(closed_date AS DATE) < TRY_CAST(received_date AS DATE)"),
    dict(id="A01", dimension="accuracy", owner="Hatoon Al-Furaih", table="complaints", key="rid",
         description="No consumer complaint is above SAR 50,000: larger amounts mean a unit error",
         attributes=["amount_sar"], severity="block", max_rate=0.001,
         sql="SELECT rid FROM complaints WHERE TRY_CAST(amount_sar AS DOUBLE) > 50000"),
    dict(id="A02", dimension="accuracy", owner="Hatoon Al-Furaih", table="complaints", key="rid",
         description="A month's median amount in a channel stays within three times that channel's usual median",
         attributes=["amount_sar", "channel", "received_date"], severity="block", max_rate=0.001,
         sql="""WITH m AS (SELECT left(received_date, 7) AS mon, channel, median(TRY_CAST(amount_sar AS DOUBLE)) AS med
                         FROM complaints GROUP BY ALL),
                     b AS (SELECT channel, median(med) AS base FROM m GROUP BY channel)
                SELECT c.rid FROM complaints c JOIN m ON left(c.received_date, 7) = m.mon AND c.channel = m.channel
                JOIN b ON b.channel = m.channel WHERE m.med > 3 * b.base"""),
    dict(id="I01", dimension="consistency", owner="Abdulelah Al-Batal", table="actions", key="rid",
         description="Every case action belongs to a complaint in the extract",
         attributes=["complaint_id"], severity="quarantine", max_rate=0.01,
         sql="SELECT rid FROM actions WHERE complaint_id NOT IN (SELECT complaint_id FROM complaints)"),
    dict(id="U02", dimension="uniqueness", owner="Abdulelah Al-Batal", table="merchants", key="rid",
         description="One registry entry per commercial registration number",
         attributes=["cr_number"], severity="warn", max_rate=0.0,
         sql="SELECT rid FROM (SELECT rid, row_number() OVER (PARTITION BY cr_number ORDER BY rid) AS k FROM merchants) WHERE k > 1"),
    dict(id="T01", dimension="timeliness", owner="Hatoon Al-Furaih", table="complaints", key="rid",
         description="The newest complaint is at most ten days older than the extract date",
         attributes=["received_date"], severity="warn", max_rate=0.0,
         sql="SELECT rid FROM complaints WHERE (SELECT max(TRY_CAST(received_date AS DATE)) FROM complaints WHERE TRY_CAST(received_date AS DATE) <= (SELECT extract_date FROM params)) < (SELECT extract_date FROM params) - INTERVAL 10 DAY LIMIT 1"),
]
