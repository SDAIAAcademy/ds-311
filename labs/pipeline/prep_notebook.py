"""The preparation notebook Bayyin used before the pipeline, kept as its cells. Lab 4.1 runs it twice.

Each entry of CELLS is one notebook cell, run in a shared namespace in the order it is given, as a
person would run them. Do not fix it here: Lab 4.1 is about finding what makes it unrepeatable."""

CELLS = {
    1: """
import datetime, duckdb, pandas as pd
con = duckdb.connect()
df = con.execute(f"SELECT * FROM read_csv('{RAW}/complaints_extract.csv.gz', all_varchar = true)").df()
regions = pd.read_csv(f"{RAW}/regions.csv")
""",
    2: """
prepared_at = datetime.datetime.now().isoformat(timespec="seconds")
df["prepared_at"] = prepared_at
""",
    3: """
# mid-year population: last year's figure plus 1% growth
regions["population"] = regions["population"] * 1.01
""",
    4: """
df = df.sample(frac=1)   # shuffle so the dedupe does not favour the portal's order
df = df.drop_duplicates(subset=["customer_key", "merchant_name_raw", "product"], keep="first")
""",
    5: """
categories = list(set(df.category_code))
df["month"] = df.received_date.str[:7]
rate = (df.merge(regions, on="region_code").groupby(["month", "region_code"])
          .agg(complaints=("complaint_id", "size"), population=("population", "first")).reset_index())
rate["rate_per_100k"] = (rate.complaints / rate.population * 100000).round(2)
pivot = df.pivot_table(index="region_code", columns="category_code", values="complaint_id", aggfunc="count").reindex(columns=categories)
df.to_csv(f"{OUT}/complaints_prepared.csv", index=False)
rate.to_csv(f"{OUT}/monthly_rate.csv", index=False)
pivot.to_csv(f"{OUT}/category_by_region.csv")
""",
}
