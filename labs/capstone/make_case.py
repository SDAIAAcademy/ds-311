"""Al-Ghadaf Municipality (بلدية الغضف): synthetic maintenance requests for the DS-311 capstone.

    python make_case.py --out data                       # the case, seed 2027
    python make_case.py --out data --seed 41             # another team's variant
    python make_case.py --out seeded --defect cost_units # the assessor's seeded defect (see DEFECTS)

Standard library only. Writes:
  requests_text.csv     2,000 requests (id, text, language variety) to label
  pilot_round1.csv      150 of them labelled by three raters (R1 to R3) under a first guideline
  pilot_round2.csv      the same 150 after a revision (agreement rises, unevenly)
  sources/requests_extract.csv.gz, contractors.csv, districts.csv, work_orders.csv.gz
                        the four source tables of the preparation pipeline, as of 2027-03-05
Every run with the same seed writes the same bytes. The categories, the raters' habits and the
defects are fictional; no real person or request is described.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import random
from datetime import date, timedelta
from pathlib import Path

CATS = ["ROAD", "LIGHT", "WATER", "WASTE", "PARK"]
DISTRICTS = [("D01", "Al-Rawdah", 41000), ("D02", "Al-Nakheel", 28500), ("D03", "Al-Safa", 36200), ("D04", "Al-Wurud", 19800),
             ("D05", "Al-Faisaliyah", 33100), ("D06", "Al-Aziziyah", 25400), ("D07", "Al-Shifa", 30700)]
CONTRACTORS = ["Al-Bina", "Al-Itqan", "Al-Masar", "Al-Ruwad", "Al-Watan", "Al-Jazeera", "Al-Amal", "Al-Fajr"]
PHRASES = {
    "ROAD": {"msa": ["حفرة كبيرة في الشارع أمام المنزل", "تشقق في الإسفلت بعد الأمطار"], "gulf": ["فيه حفرة بالشارع خربت كفر السيارة", "الطريق مكسر من شهر"],
             "english": ["A large pothole on the street outside my house", "The asphalt cracked after the rain"]},
    "LIGHT": {"msa": ["عمود الإنارة لا يعمل منذ أسبوع", "الإنارة مطفأة في الممر"], "gulf": ["لمبة الشارع طافية من أسبوع", "الشارع ظلام ما فيه إنارة"],
              "english": ["The street light has been off for a week", "The walkway lights are out"]},
    "WATER": {"msa": ["تسرب مياه من الشبكة في الحي", "انسداد في تصريف مياه الأمطار"], "gulf": ["فيه موية تطلع من الأرض", "المجاري مسدودة عند البيت"],
              "english": ["Water leaking from the main in our street", "The storm drain is blocked"]},
    "WASTE": {"msa": ["الحاوية ممتلئة ولم تفرغ منذ أيام", "مخلفات بناء مرمية على الرصيف"], "gulf": ["الزبالة ما انشالت من ثلاث أيام", "أحد رامي مخلفات بناء جنب البيت"],
              "english": ["The bin has not been emptied for days", "Building waste dumped on the pavement"]},
    "PARK": {"msa": ["ألعاب الأطفال في الحديقة مكسورة", "أشجار الحديقة تحتاج إلى ري"], "gulf": ["المراجيح بالحديقة مكسرة", "الزرع بالحديقة يبس"],
             "english": ["The playground swings in the park are broken", "The park trees need watering"]},
}
# Requests that sit on a boundary: the guideline must decide them
BOUNDARY = {("WATER", "ROAD"): {"msa": "تسرب مياه أحدث حفرة في الطريق", "gulf": "الموية خربت الشارع وصار فيه حفرة", "english": "A water leak has opened a hole in the road"},
            ("PARK", "LIGHT"): {"msa": "الإنارة داخل الحديقة لا تعمل", "gulf": "إنارة الحديقة طافية", "english": "The lights inside the park are off"},
            ("WASTE", "PARK"): {"msa": "نفايات متراكمة داخل الحديقة", "gulf": "الحديقة مليانة زبالة", "english": "Rubbish piling up inside the park"}}
DEFECTS = {
    "duplicates": "40 requests exported twice with the same id",
    "district_codes": "120 requests with an empty or unknown district code",
    "cost_units": "the February work orders of one contractor in halalas instead of riyals",
    "closed_before": "30 requests closed before they were opened",
    "future_dates": "8 requests dated after the extract",
}


def write_csv(path: Path, rows: list[dict], gz: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    data = buf.getvalue().encode("utf-8")
    path.write_bytes(gzip.compress(data, mtime=0) if gz else data)


def make(out: Path, seed: int, defect: str | None) -> None:
    rng = random.Random(seed)
    requests = []
    start = date(2026, 3, 1)
    for k in range(2000):
        var = rng.choices(["msa", "gulf", "english", "mixed"], [0.4, 0.35, 0.15, 0.10])[0]
        boundary = rng.random() < 0.12
        if boundary:
            (a, b), txts = rng.choice(list(BOUNDARY.items()))
            truth = a  # the reference decision: the cause, not the place
            text = txts["english" if var == "english" else ("gulf" if var in ("gulf", "mixed") else "msa")]
        else:
            truth = rng.choices(CATS, [0.3, 0.2, 0.2, 0.2, 0.1])[0]
            text = rng.choice(PHRASES[truth]["english" if var == "english" else ("gulf" if var in ("gulf", "mixed") else "msa")])
        if var == "mixed":
            text += rng.choice([" please fix it", " urgent", " ASAP لو سمحتوا"])
        d = start + timedelta(days=rng.randrange(365))
        district = rng.choice(DISTRICTS)[0]
        requests.append(dict(request_id=f"G{500001 + k}", text=text, variety=var, truth=truth, boundary=int(boundary),
                             opened_date=d.isoformat(), district_code=district))
    write_csv(out / "requests_text.csv", [{k: r[k] for k in ("request_id", "text", "variety")} for r in requests])

    # Pilot: three raters, two rounds. Round 1 leaves the boundaries undecided; round 2 decides them.
    pilot = rng.sample(requests, 150)
    habits = {"R1": {"WATER": "ROAD"}, "R2": {"PARK": "LIGHT"}, "R3": {"WASTE": "PARK"}}
    for rnd, (p_err, p_bound) in ((1, (0.08, 0.55)), (2, (0.05, 0.2))):
        rows = []
        for r in pilot:
            row = {"request_id": r["request_id"], "text": r["text"], "variety": r["variety"]}
            for rater, habit in habits.items():
                lab = r["truth"]
                if r["boundary"] and rng.random() < p_bound:
                    lab = next(b for (a, b) in BOUNDARY if a == r["truth"])
                elif rng.random() < p_err * (1.6 if r["variety"] == "mixed" else 1):
                    lab = habit.get(r["truth"], rng.choice(CATS))
                row[rater] = lab
            rows.append(row)
        write_csv(out / f"pilot_round{rnd}.csv", rows)

    # Source tables for the pipeline, extract of 2027-03-05
    contractors = [dict(contractor_id=f"K{101 + i}", name=n, cr_number=f"40{rng.randrange(10**7, 10**8)}") for i, n in enumerate(CONTRACTORS)]
    extract, orders = [], []
    for r in requests:
        status = rng.choices(["closed", "open"], [0.8, 0.2])[0]
        closed = (date.fromisoformat(r["opened_date"]) + timedelta(days=rng.randint(1, 30))).isoformat() if status == "closed" else ""
        if closed and closed > "2027-03-05":
            closed, status = "", "open"
        extract.append(dict(request_id=r["request_id"], opened_date=r["opened_date"], district_code=r["district_code"],
                            category=r["truth"], channel=rng.choice(["app", "call_centre", "web"]), status=status, closed_date=closed))
        if status == "closed":
            orders.append(dict(order_id=f"W{700001 + len(orders)}", request_id=r["request_id"], contractor_id=rng.choice(contractors)["contractor_id"],
                               cost_sar=f"{rng.lognormvariate(6.3, 0.7):.2f}", order_date=closed))
    if defect == "duplicates":
        extract += [dict(r) for r in rng.sample(extract, 40)]
    elif defect == "district_codes":
        for r in rng.sample(extract, 120):
            r["district_code"] = rng.choice(["", "D99"])
    elif defect == "cost_units":
        k = contractors[0]["contractor_id"]
        for o in orders:
            if o["contractor_id"] == k and o["order_date"].startswith("2027-02"):
                o["cost_sar"] = f"{float(o['cost_sar']) * 100:.2f}"
    elif defect == "closed_before":
        for r in rng.sample([r for r in extract if r["closed_date"]], 30):
            r["closed_date"] = (date.fromisoformat(r["opened_date"]) - timedelta(days=rng.randint(1, 9))).isoformat()
    elif defect == "future_dates":
        for r in rng.sample(extract, 8):
            r["opened_date"] = (date(2027, 3, 5) + timedelta(days=rng.randint(10, 200))).isoformat()
    extract.sort(key=lambda r: r["request_id"])
    src = out / "sources"
    write_csv(src / "requests_extract.csv.gz", extract, gz=True)
    write_csv(src / "contractors.csv", contractors)
    write_csv(src / "districts.csv", [dict(district_code=c, name_en=n, population=p, version="2027.1") for c, n, p in DISTRICTS])
    write_csv(src / "work_orders.csv.gz", orders, gz=True)
    print(f"Al-Ghadaf case, seed {seed}{', defect ' + defect if defect else ''}: {len(requests)} requests, 150 in the pilot, "
          f"{len(extract)} extract rows, {len(orders)} work orders -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=Path("data"))
    ap.add_argument("--seed", type=int, default=2027)
    ap.add_argument("--defect", choices=sorted(DEFECTS))
    a = ap.parse_args()
    make(a.out, a.seed, a.defect)
