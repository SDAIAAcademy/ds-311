"""Generate the synthetic data of the Bayyin Consumer Protection Office case (DS-311).

    uv run python prepare_data.py

Standard library only, fixed seed (311): the same bytes on every run. Everything is invented:
the office, the merchants, the regions, the complainants and their personal data.
Writes labs/data/ and the reference results the labs' safety nets read.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import random
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

SEED = 311
LABS = Path(__file__).resolve().parent
DATA = LABS / "data"
REF = DATA / "reference"

CATS = ["REFUND", "DEFECT", "DELIVERY", "PRICE", "AD", "WARRANTY"]
CAT_P = [0.27, 0.23, 0.21, 0.14, 0.125, 0.025]
VARS = ["msa", "gulf", "english", "mixed"]
VAR_P = [0.48, 0.28, 0.18, 0.06]
CHANNELS = ["app", "web", "call_centre", "email"]
CHAN_P = [0.42, 0.30, 0.18, 0.10]
START = date(2025, 9, 1)
END = date(2026, 8, 31)

# ---------------------------------------------------------------- merchants
ROOTS = [("النور", "Al-Noor", ["Al Nour", "Alnoor", "Al-Nur"]), ("الريان", "Al-Rayyan", ["Al Rayan", "Alrayyan"]),
         ("الأفق", "Al-Ofuq", ["Al Ufuq", "Alofuq"]), ("السحاب", "Al-Sahab", ["Al Sahaab", "Alsahab"]),
         ("الأمل", "Al-Amal", ["Al Amal", "Alamal"]), ("الفجر", "Al-Fajr", ["Al Fajer", "Alfajr"]),
         ("المدار", "Al-Madar", ["Al Madaar", "Almadar"]), ("اللؤلؤة", "Al-Lulua", ["Al Lulu", "Al Luluah"]),
         ("النخبة", "Al-Nukhba", ["Al Nokhba", "Alnukhba"]), ("الصفوة", "Al-Safwa", ["Al Safwah", "Alsafwa"]),
         ("الريم", "Al-Reem", ["Al Rim", "Alreem"]), ("الجود", "Al-Jood", ["Al Joud", "Aljood"]),
         ("التميز", "Al-Tamayuz", ["Al Tamayoz", "Altamayuz"]), ("الإتقان", "Al-Itqan", ["Al Etqan", "Alitqan"]),
         ("المسار", "Al-Masar", ["Al Massar", "Almasar"]), ("الأصالة", "Al-Asala", ["Al Asalah", "Alasala"]),
         ("الهدى", "Al-Huda", ["Al Hoda", "Alhuda"]), ("الرواد", "Al-Rowad", ["Al Ruwad", "Alrowad"]),
         ("النجمة", "Al-Najma", ["Al Najmah", "Alnajma"]), ("الشروق", "Al-Shorouq", ["Al Shorooq", "Alshorouq"]),
         ("الغدير", "Al-Ghadir", ["Al Ghadeer", "Alghadir"]), ("الفارس", "Al-Faris", ["Al Fares", "Alfaris"]),
         ("الكرم", "Al-Karam", ["Al Karm", "Alkaram"]), ("الياسمين", "Al-Yasmin", ["Al Yasmeen", "Alyasmin"]),
         ("الوفاق", "Al-Wifaq", ["Al Wefaq", "Alwifaq"])]
SECTORS = [("للإلكترونيات", "Electronics", "Elec.", ["هاتف", "حاسب محمول", "شاشة"], ["a phone", "a laptop", "a TV screen"]),
           ("للأثاث", "Furniture", "Furn.", ["كنبة", "طاولة طعام", "خزانة"], ["a sofa", "a dining table", "a wardrobe"]),
           ("للأجهزة المنزلية", "Home Appliances", "Appl.", ["غسالة", "مكيف", "ثلاجة"], ["a washing machine", "an air conditioner", "a fridge"]),
           ("للأزياء", "Fashion", "Fash.", ["حذاء رياضي", "عباءة", "حقيبة"], ["running shoes", "an abaya", "a handbag"]),
           ("لقطع غيار السيارات", "Auto Parts", "Auto", ["بطارية سيارة", "إطارات", "مساحات"], ["a car battery", "tyres", "wiper blades"]),
           ("للمجوهرات", "Jewellery", "Jewel.", ["عقد ذهب", "خاتم", "ساعة"], ["a gold necklace", "a ring", "a watch"])]
UNKNOWN = [("الوفاء للألعاب", "Al-Wafa Toys"), ("الضياء للعطور", "Al-Diyaa Perfumes"), ("السنبلة للتمور", "Al-Sunbula Dates"),
           ("البشائر للسفر", "Al-Bashaer Travel"), ("القمة للرياضة", "Al-Qimma Sports"), ("الندى للزهور", "Al-Nada Flowers")]

REGIONS = [(f"R{i:02d}", f"Region {i:02d}", f"المنطقة {i:02d}") for i in range(1, 14)]


def wr(path: Path, rows: list[dict], fields: list[str] | None = None, gz: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or list(rows[0].keys())
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in fields})
    data = buf.getvalue().encode("utf-8")
    if gz:
        with open(path, "wb") as f:
            f.write(gzip.compress(data, mtime=0))
    else:
        path.write_bytes(data)


def wj(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=False) + "\n", encoding="utf-8", newline="\n")


def pick(rng, items, p):
    return rng.choices(items, weights=p, k=1)[0]


# ---------------------------------------------------------------- phrases
PH = {
 "english": {
  "intro": ["I bought {product} from {merchant}.", "I ordered {product} online from {merchant}.", "Last week I paid for {product} at {merchant}."],
  "faulty": ["It stopped working after {n} days.", "It arrived broken.", "It has a fault: it overheats."],
  "nad": ["It is not the model shown on the website.", "The size and colour are different from the listing."],
  "refund": ["I asked for a refund and they refused.", "The store refused to give my money back."],
  "warranty": ["It is still under warranty, but the service centre refused to repair it.", "They refused the warranty repair although I have the warranty card."],
  "late": ["They promised delivery in 3 days; it came after {n} days.", "The delivery is {n} days late."],
  "nodeliv": ["The order never arrived.", "It was marked delivered but I never received it."],
  "price": ["The shelf price was {a} SAR but I was charged {b} SAR.", "The app showed {a} SAR and the invoice says {b} SAR."],
  "ad": ["The advert promised {p}% off, but there was no discount.", "The offer said free installation, then they charged for it."],
  "adprice": ["The advert said {p}% off and the shelf showed {a} SAR, but I was charged {b} SAR."],
  "distress": ["The staff shouted at me and threatened me when I complained."],
  "phone": "My number is {v}.", "email": "Email me at {v}.", "nid": "My ID number is {v}.", "iban": "Please refund to {v}.",
 },
 "msa": {
  "intro": ["اشتريت {product} من {merchant}.", "طلبت {product} عبر الإنترنت من {merchant}.", "دفعت الأسبوع الماضي ثمن {product} في {merchant}."],
  "faulty": ["توقف عن العمل بعد {n} أيام.", "وصل مكسوراً.", "به عيب في التشغيل، فهو يسخن كثيراً."],
  "nad": ["ليس الطراز المعروض في الموقع.", "المقاس واللون يختلفان عن الوصف."],
  "refund": ["طلبت استرداد المبلغ فرفضوا.", "رفض المتجر إعادة المبلغ."],
  "warranty": ["ما زال في فترة الضمان لكن مركز الصيانة رفض إصلاحه.", "رفضوا الإصلاح بالضمان رغم وجود بطاقة الضمان."],
  "late": ["وعدوا بالتوصيل خلال 3 أيام ووصل بعد {n} يوماً.", "تأخر التوصيل {n} أيام."],
  "nodeliv": ["لم يصل الطلب أبداً.", "ظهر الطلب كأنه سُلّم ولم أستلمه."],
  "price": ["السعر على الرف {a} ريال لكن دفعت {b} ريال.", "التطبيق أظهر {a} ريال والفاتورة {b} ريال."],
  "ad": ["الإعلان وعد بخصم {p}% ولم يكن هناك خصم.", "العرض قال تركيب مجاني ثم طلبوا رسوم التركيب."],
  "adprice": ["الإعلان قال خصم {p}% والرف أظهر {a} ريال لكن دفعت {b} ريال."],
  "distress": ["صرخ الموظف في وجهي وهددني عندما اشتكيت."],
  "phone": "رقم جوالي {v}.", "email": "بريدي الإلكتروني {v}.", "nid": "رقم هويتي {v}.", "iban": "حوّلوا المبلغ إلى {v}.",
 },
 "gulf": {
  "intro": ["شريت {product} من {merchant}.", "طلبت {product} من {merchant} أونلاين.", "الأسبوع اللي فات دفعت حق {product} في {merchant}."],
  "faulty": ["خرب بعد {n} أيام.", "وصلني مكسور.", "فيه خراب، يسخن مرة."],
  "nad": ["مو نفس الموديل اللي بالموقع.", "المقاس واللون غير عن اللي بالصورة."],
  "refund": ["طلبت فلوسي ورفضوا.", "قالوا ما نرجع فلوس."],
  "warranty": ["لسا عليه ضمان والصيانة رفضوا يصلحونه.", "رفضوا يصلحونه بالضمان مع إن معي كرت الضمان."],
  "late": ["قالوا يوصل بثلاث أيام ووصل بعد {n} يوم.", "التوصيل متأخر {n} أيام."],
  "nodeliv": ["الطلب ما وصل للحين.", "مكتوب تم التوصيل وأنا ما استلمت شي."],
  "price": ["السعر على الرف {a} ريال وحاسبوني {b}.", "بالتطبيق {a} ريال وبالفاتورة {b}."],
  "ad": ["الإعلان يقول خصم {p}% وطلع كذب.", "العرض يقول تركيب مجاني وبعدين طلبوا فلوس التركيب."],
  "adprice": ["الإعلان يقول خصم {p}% والرف {a} ريال وحاسبوني {b}."],
  "distress": ["الموظف صارخ علي وهددني لما اشتكيت."],
  "phone": "رقمي {v}.", "email": "ايميلي {v}.", "nid": "هويتي {v}.", "iban": "رجعوا الفلوس على {v}.",
 },
 "mixed": {
  "intro": ["شريت {product} من {merchant} online.", "طلبت {product} من {merchant} عن طريق الـ app."],
  "faulty": ["صار فيه defect بعد {n} أيام.", "وصل damaged."],
  "nad": ["مو نفس الـ model اللي بالـ website.", "الـ size غير عن الـ listing."],
  "refund": ["طلبت refund ورفضوا.", "قالوا no refund policy."],
  "warranty": ["عليه warranty والـ service centre رفض الـ repair.", "الـ warranty card معي ورفضوا الـ repair."],
  "late": ["الـ delivery تأخر {n} أيام.", "قالوا 3 days ووصل بعد {n} أيام."],
  "nodeliv": ["الـ order ما وصل أبداً.", "مكتوب delivered وأنا ما استلمت."],
  "price": ["الـ price بالـ app {a} وحاسبوني {b}.", "على الـ shelf {a} SAR والـ invoice {b}."],
  "ad": ["الـ offer يقول {p}% off وطلع fake.", "الـ ad قال free installation وبعدين charged."],
  "adprice": ["الـ ad يقول {p}% off والـ shelf {a} وحاسبوني {b}."],
  "distress": ["الـ staff صرخوا علي وهددوني."],
  "phone": "رقمي {v}.", "email": "my email {v}.", "nid": "هويتي {v}.", "iban": "IBAN {v}.",
 },
}

AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


def facts_for(cat: str, rng: random.Random) -> tuple[dict, str]:
    """Facts of one complaint and its ambiguity pair ('' when unambiguous). Truth follows guideline v1.1."""
    f = dict(asked_refund=0, refund_refused=0, faulty=0, not_as_described=0, within_warranty=0, repair_refused=0,
             late=0, not_delivered=0, charged_more=0, advert_claim=0)
    amb = ""
    if cat == "REFUND":
        f.update(asked_refund=1, refund_refused=1)
        u = rng.random()
        if u < 0.30:
            f["faulty"] = 1; amb = "REFUND|DEFECT"
        elif u < 0.42:
            f["not_delivered"] = 1; amb = "REFUND|DELIVERY"
    elif cat == "DEFECT":
        f["faulty" if rng.random() < 0.7 else "not_as_described"] = 1
    elif cat == "WARRANTY":
        f.update(faulty=1, within_warranty=1, repair_refused=1); amb = "WARRANTY|DEFECT"
    elif cat == "DELIVERY":
        f["late" if rng.random() < 0.6 else "not_delivered"] = 1
    elif cat == "PRICE":
        f["charged_more"] = 1
        if rng.random() < 0.30:
            f["advert_claim"] = 1; amb = "PRICE|AD"
    elif cat == "AD":
        f["advert_claim"] = 1
    return f, amb


def apply_rules_v11(f: dict) -> str:
    """Guideline v1.1 decision rules, in order. The truth of every complaint is defined by them."""
    if f["within_warranty"] and f["repair_refused"]:
        return "WARRANTY"
    if f["asked_refund"] and f["refund_refused"]:
        return "REFUND"
    if f["faulty"] or f["not_as_described"]:
        return "DEFECT"
    if f["late"] or f["not_delivered"]:
        return "DELIVERY"
    if f["charged_more"]:
        return "PRICE"
    if f["advert_claim"]:
        return "AD"
    return "OTHER"


def make_text(rng, var, merchant, product, f, pii, distress):
    P = PH[var]
    n, a = rng.randint(4, 21), rng.choice([99, 149, 249, 399, 899, 1299])
    b = a + rng.choice([20, 50, 100, 150])
    pct = rng.choice([20, 30, 50])
    s = [rng.choice(P["intro"]).format(product=product, merchant=merchant).replace("..", ".")]
    if f["faulty"]:
        s.append(rng.choice(P["faulty"]).format(n=n))
    if f["not_as_described"]:
        s.append(rng.choice(P["nad"]))
    if f["within_warranty"]:
        s.append(rng.choice(P["warranty"]))
    if f["late"]:
        s.append(rng.choice(P["late"]).format(n=n))
    if f["not_delivered"]:
        s.append(rng.choice(P["nodeliv"]))
    if f["charged_more"] and f["advert_claim"]:
        s.append(P["adprice"][0].format(a=a, b=b, p=pct))
    elif f["charged_more"]:
        s.append(rng.choice(P["price"]).format(a=a, b=b))
    elif f["advert_claim"]:
        s.append(rng.choice(P["ad"]).format(p=pct))
    if f["asked_refund"]:
        s.append(rng.choice(P["refund"]))
    if distress:
        s.append(P["distress"][0])
    for kind, val in pii:
        s.append(P[kind].format(v=val))
    return " ".join(s)


def fake_pii(rng):
    kinds = rng.sample(["phone", "email", "nid", "iban"], k=rng.choice([1, 1, 1, 2]))
    out = []
    for k in kinds:
        if k == "phone":
            v = "05" + "".join(rng.choice("0123456789") for _ in range(8))
            if rng.random() < 0.12:
                v = v.translate(AR_DIGITS)  # Arabic-Indic digits: a naive pattern misses them
        elif k == "email":
            v = rng.choice(["noura", "m.salem", "abu.fahad", "rana88", "k.otaibi", "user2026"]) + str(rng.randint(1, 99)) + "@mail.example"
        elif k == "nid":
            v = rng.choice("12") + "".join(rng.choice("0123456789") for _ in range(9))
        else:
            v = "SA" + "".join(rng.choice("0123456789") for _ in range(22))
        out.append((k, v))
    return out


def main() -> None:
    rng = random.Random(SEED)
    DATA.mkdir(exist_ok=True)

    # ---------------- merchants registry
    merchants = []
    mid = 1001
    for ri, (rar, ren, _) in enumerate(ROOTS):
        for si, (sar, sen, _, _, _) in enumerate(SECTORS):
            merchants.append(dict(merchant_id=f"M{mid}", name_ar=f"{rar} {sar}", name_en=f"{ren} {sen}",
                                  cr_number=str(1010000000 + rng.randint(100000, 999999)), sector=sen,
                                  region_code=REGIONS[(ri + si) % 13][0], root=ri, sec=si))
            mid += 1
    # registry defect: three merchants registered twice under a second id with the same CR number
    dup_reg = []
    for m in rng.sample(merchants, 3):
        d = dict(m); d["merchant_id"] = f"M{mid}"; mid += 1
        dup_reg.append(d)
    registry = merchants + dup_reg

    def raw_variant(m, rng, script=None):
        rar, ren, ren_alts = ROOTS[m["root"]]
        sar, sen, sabbr, _, _ = SECTORS[m["sec"]]
        script = script or rng.choice(["ar", "ar", "en", "en", "mixed"])
        if script == "ar":
            root = rar
            if rng.random() < 0.3: root = root.replace("أ", "ا").replace("إ", "ا")
            if rng.random() < 0.3: root = root.replace("ة", "ه")
            if rng.random() < 0.2: root = root[2:]  # without the article
            if rng.random() < 0.15: root = root.replace("ى", "ي")
            name = f"{root} {sar}"
            pre = rng.choice(["", "", "شركة ", "مؤسسة ", "متجر "])
            suf = rng.choice(["", "", "", " المحدودة"])
            name = pre + name + suf
            if rng.random() < 0.1 and len(name) > 6:
                i = rng.randrange(3, len(name) - 1); name = name[:i] + name[i + 1:]
        elif script == "en":
            root = rng.choice([ren] + ren_alts)
            sec = sen if rng.random() < 0.7 else sabbr
            name = f"{root} {sec}"
            name = name + rng.choice(["", "", " Co.", " Est.", " LLC"])
            name = rng.choice([name, name.upper(), name.lower()])
            if rng.random() < 0.1 and len(name) > 6:
                i = rng.randrange(3, len(name) - 1); name = name[:i] + name[i + 1:]
        else:
            name = f"{rar} {sen}" if rng.random() < 0.5 else f"{rng.choice([ren] + ren_alts)} {sar}"
        return " ".join(name.split())

    # ---------------- corpus: 30,000 complaints
    days = (END - START).days + 1
    corpus, truth = [], []
    nid_pool = [hashlib.sha256(f"c{i}".encode()).hexdigest()[:12] for i in range(21000)]
    for i in range(30000):
        cid = f"C{100001 + i}"
        cat = pick(rng, CATS, CAT_P)
        var = pick(rng, VARS, VAR_P)
        ch = pick(rng, CHANNELS, CHAN_P)
        m = rng.choice(merchants)
        f, amb = facts_for(cat, rng)
        assert apply_rules_v11(f) == cat
        script = "en" if var == "english" else ("mixed" if var == "mixed" else "ar")
        mname = raw_variant(m, rng, script if script != "mixed" else rng.choice(["ar", "en"]))
        prod_i = rng.randrange(3)
        product = SECTORS[m["sec"]][4 if var == "english" else 3][prod_i]
        pii = fake_pii(rng) if rng.random() < 0.18 else []
        distress = rng.random() < 0.03
        text = make_text(rng, var, mname, product, f, pii, distress)
        rd = START + timedelta(days=rng.randrange(days))
        corpus.append(dict(complaint_id=cid, received_date=rd.isoformat(), channel=ch, variety=var, text=text))
        truth.append(dict(complaint_id=cid, category=cat, amb_pair=amb, distressing=int(distress), has_pii=int(bool(pii)),
                          pii_kinds="|".join(k for k, _ in pii), merchant_id=m["merchant_id"], merchant_raw=mname,
                          product=SECTORS[m["sec"]][4][prod_i], **f))
    T = {t["complaint_id"]: t for t in truth}
    C = {c["complaint_id"]: c for c in corpus}
    wr(DATA / "corpus" / "complaints_text.csv.gz", corpus, gz=True)
    wr(REF / "truth_labels.csv.gz", truth, gz=True)

    # pre-label proxy known before labelling (a keyword step): right about 80% of the time
    index = []
    for c in corpus:
        t = T[c["complaint_id"]]
        pl = t["category"]
        if rng.random() < (0.20 if c["variety"] in ("msa", "english") else 0.30):
            pl = rng.choice([x for x in CATS if x != pl])
        if t["amb_pair"] and rng.random() < 0.5:
            pl = t["amb_pair"].split("|")[1]
        index.append(dict(complaint_id=c["complaint_id"], variety=c["variety"], channel=c["channel"], prelabel=pl))
    wr(DATA / "corpus" / "corpus_index.csv.gz", index, gz=True)

    # ---------------- Day 1 pilot: 300 complaints, three raters, two rounds
    pool = [c for c in corpus if not T[c["complaint_id"]]["distressing"]]
    amb_pool = [c for c in pool if T[c["complaint_id"]]["amb_pair"]]
    plain_pool = [c for c in pool if not T[c["complaint_id"]]["amb_pair"]]
    warr = [c for c in amb_pool if T[c["complaint_id"]]["category"] == "WARRANTY"]
    other_amb = [c for c in amb_pool if T[c["complaint_id"]]["category"] != "WARRANTY"]
    pilot = rng.sample(warr, 15) + rng.sample(other_amb, 80) + rng.sample(plain_pool, 205)
    # ensure a few mixed and warranty items
    rng.shuffle(pilot)
    pilot_ids = [c["complaint_id"] for c in pilot]

    def rater_label(rng, rater, t, var, rnd):
        cat = t["category"]
        if rnd == 1 and rater == "R3" and cat == "WARRANTY":
            return "DEFECT"
        err = (0.07 if rnd == 1 else 0.04) + ((0.09 if rnd == 1 else 0.04) if var in ("gulf", "mixed") else 0.0)
        if t["amb_pair"]:
            other = [x for x in t["amb_pair"].split("|") if x != cat][0]
            bias = {"R1": 0.45, "R2": 0.30, "R3": 0.55}[rater] if rnd == 1 else 0.10
            if cat == "WARRANTY":
                bias = {"R1": 0.15, "R2": 0.10, "R3": 0.0}[rater] if rnd == 1 else 0.08
            if rng.random() < bias:
                return other
        if rng.random() < err:
            return rng.choice([x for x in CATS if x != cat])
        return cat

    r1, r2 = [], []
    for c in pilot:
        t = T[c["complaint_id"]]
        row1 = dict(complaint_id=c["complaint_id"], variety=c["variety"], text=c["text"])
        row2 = dict(row1)
        for r in ("R1", "R2", "R3"):
            row1[r] = rater_label(rng, r, t, c["variety"], 1)
            row2[r] = rater_label(rng, r, t, c["variety"], 2)
        r1.append(row1); r2.append(row2)
    fields = ["complaint_id", "variety", "text", "R1", "R2", "R3"]
    wr(DATA / "pilot" / "pilot_round1.csv", r1, fields)
    wr(DATA / "pilot" / "pilot_round2.csv", r2, fields)

    # Lab 1.1: forty complaints for the participant, and two neighbours' labels (round-1 style)
    forty = pilot[:40]
    wr(DATA / "pilot" / "my40.csv", [dict(complaint_id=c["complaint_id"], variety=c["variety"], text=c["text"], label="") for c in forty])
    for name, rr in (("neighbour_a", "R1"), ("neighbour_b", "R2"), ("example_me", "R3")):
        wr(DATA / "pilot" / f"{name}.csv", [dict(complaint_id=c["complaint_id"], label=rater_label(rng, rr, T[c["complaint_id"]], c["variety"], 1)) for c in forty])

    # Lab 1.2: twelve edge cases with facts read by the labelling lead and the expected label
    edge = []
    combos = [dict(asked_refund=1, refund_refused=1, faulty=1), dict(faulty=1, within_warranty=1, repair_refused=1),
              dict(charged_more=1, advert_claim=1), dict(not_delivered=1, asked_refund=1, refund_refused=1),
              dict(not_as_described=1), dict(advert_claim=1), dict(late=1), dict(faulty=1, within_warranty=1, repair_refused=1, asked_refund=1, refund_refused=1),
              dict(charged_more=1), dict(not_as_described=1, asked_refund=1, refund_refused=1), dict(late=1, faulty=1), dict(advert_claim=1, not_delivered=1)]
    base = dict(asked_refund=0, refund_refused=0, faulty=0, not_as_described=0, within_warranty=0, repair_refused=0, late=0, not_delivered=0, charged_more=0, advert_claim=0)
    for i, cmb in enumerate(combos):
        f = dict(base, **cmb)
        var = ["msa", "gulf", "english", "mixed"][i % 4]
        m = merchants[(i * 13) % len(merchants)]
        text = make_text(rng, var, raw_variant(m, rng, "en" if var == "english" else "ar"), SECTORS[m["sec"]][4 if var == "english" else 3][0], f, [], False)
        edge.append(dict(case=f"E{i + 1:02d}", variety=var, text=text, expected=apply_rules_v11(f), **f))
    wr(DATA / "pilot" / "edge_cases.csv", edge)

    # Lab 1.4: thirty disagreements from round 1, with the facts the adjudicator reads from each text
    dis = [row for row in r1 if len({row["R1"], row["R2"], row["R3"]}) > 1]
    dis.sort(key=lambda r: (T[r["complaint_id"]]["amb_pair"] == "", r["complaint_id"]))
    pick30 = dis[:22] + [r for r in dis[22:] if T[r["complaint_id"]]["amb_pair"] == ""][:8]
    rows30 = []
    for row in pick30:
        t = T[row["complaint_id"]]
        rows30.append(dict(complaint_id=row["complaint_id"], variety=row["variety"], text=row["text"], R1=row["R1"], R2=row["R2"], R3=row["R3"],
                           **{k: t[k] for k in base}))
    wr(DATA / "pilot" / "disagreements30.csv", rows30)
    wr(REF / "adjudicator_decisions.csv", [dict(complaint_id=r["complaint_id"], decision=T[r["complaint_id"]]["category"]) for r in rows30])

    # ---------------- Day 2: golden-set expert labels come from truth; the operations round
    rest = [c for c in corpus if c["complaint_id"] not in set(pilot_ids)]
    gold_pool = rng.sample([c for c in rest if not T[c["complaint_id"]]["distressing"]], 400)
    gold_ids = [c["complaint_id"] for c in gold_pool]
    wr(DATA / "ops" / "gold_bank.csv", [dict(complaint_id=c["complaint_id"], variety=c["variety"], gold_label=T[c["complaint_id"]]["category"]) for c in gold_pool])
    used = set(pilot_ids) | set(gold_ids)
    work = rng.sample([c for c in rest if c["complaint_id"] not in used], 2000)
    raters = ["R1", "R2", "R3", "R4", "R5", "R6"]
    base_acc = {"R1": 0.92, "R2": 0.95, "R3": 0.90, "R4": 0.91, "R5": 0.93, "R6": 0.79}
    secs = {"R1": 40, "R2": 62, "R3": 45, "R4": 43, "R5": 41, "R6": 24}
    approved_restricted = ["R2", "R4"]

    def ops_label(rater, day, t, var):
        cat = t["category"]
        acc = base_acc[rater] - (0.04 if var in ("gulf", "mixed") else 0)
        if rater == "R5" and day >= 6:
            acc = 0.70
            if cat in ("WARRANTY", "DEFECT", "DELIVERY") and rng.random() < 0.6:
                return "REFUND"
        if rng.random() < acc:
            return cat
        if t["amb_pair"]:
            return [x for x in t["amb_pair"].split("|") if x != cat][0]
        return rng.choice([x for x in CATS if x != cat])

    ops = []
    distress_items = [c for c in work if T[c["complaint_id"]]["distressing"]]
    normal = [c for c in work if not T[c["complaint_id"]]["distressing"]]
    per_day = [normal[i::10] for i in range(10)]
    dist_day = [distress_items[i::10] for i in range(10)]
    for d in range(10):
        day = d + 1
        items = per_day[d]
        for j, c in enumerate(items):
            t = T[c["complaint_id"]]
            r = raters[(j + d) % 6]
            first = dict(day=day, rater=r, complaint_id=c["complaint_id"], variety=c["variety"], is_gold=0, distressing=0)
            first["label"] = ops_label(r, day, t, c["variety"])
            first["seconds"] = max(8, int(rng.gauss(secs[r], secs[r] * 0.25)))
            ops.append(first)
            if (j % 4) == 0:  # a quarter of the items get a second, independent label
                r2_ = raters[(j + d + 3) % 6]
                sec_row = dict(first, rater=r2_, label=ops_label(r2_, day, t, c["variety"]),
                               seconds=max(8, int(rng.gauss(secs[r2_], secs[r2_] * 0.25))))
                ops.append(sec_row)
        # distressing items: only approved raters; R4 takes most of them on day 7
        extra = dist_day[d]
        if day == 7:
            extra = extra + [c for c in normal[:0]]
        for k, c in enumerate(extra):
            t = T[c["complaint_id"]]
            r = "R4" if (day == 7 or k % 2 == 0) else "R2"
            ops.append(dict(day=day, rater=r, complaint_id=c["complaint_id"], variety=c["variety"], is_gold=0, distressing=1,
                            label=ops_label(r, day, t, c["variety"]), seconds=max(60, int(rng.gauss(200, 40)))))
        # gold questions: eight per rater per day
        for r in raters:
            for g in rng.sample(gold_pool, 8):
                t = T[g["complaint_id"]]
                ops.append(dict(day=day, rater=r, complaint_id=g["complaint_id"], variety=g["variety"], is_gold=1, distressing=0,
                                label=ops_label(r, day, t, g["variety"]), seconds=max(8, int(rng.gauss(secs[r], secs[r] * 0.25)))))
    # R4 on day 7: extra distressing items routed from the restricted queue (the overload)
    over = rng.sample([c for c in corpus if T[c["complaint_id"]]["distressing"] and c["complaint_id"] not in used], 16)
    for c in over:
        ops.append(dict(day=7, rater="R4", complaint_id=c["complaint_id"], variety=c["variety"], is_gold=0, distressing=1,
                        label=ops_label("R4", 7, T[c["complaint_id"]], c["variety"]), seconds=max(60, int(rng.gauss(200, 40)))))
    rng.shuffle(ops)
    ops.sort(key=lambda r: (r["day"], r["rater"]))
    wr(DATA / "ops" / "ops_round.csv", ops, ["day", "rater", "complaint_id", "variety", "is_gold", "distressing", "label", "seconds"])

    # Lab 2.4: a design trial on 300 gold complaints under three designs, and texts for masking
    trial = []
    trial_items = gold_pool[:300]
    for c in trial_items:
        t = T[c["complaint_id"]]
        cat = t["category"]
        # double labelling
        a = ops_label("R1", 1, t, c["variety"]); b = ops_label("R3", 1, t, c["variety"])
        trial.append(dict(design="double", complaint_id=c["complaint_id"], label_1=a, label_2=b, prelabel="",
                          seconds_1=int(rng.gauss(42, 8)), seconds_2=int(rng.gauss(45, 9)), adjudicated=int(a != b),
                          final=(a if a == b else cat), audited=0))
        # audited single: 15% get a second label; disagreement goes to adjudication
        a = ops_label("R4", 1, t, c["variety"])
        audit = rng.random() < 0.15
        b = ops_label("R2", 1, t, c["variety"]) if audit else ""
        trial.append(dict(design="audited_single", complaint_id=c["complaint_id"], label_1=a, label_2=b, prelabel="",
                          seconds_1=int(rng.gauss(43, 8)), seconds_2=int(rng.gauss(62, 10)) if audit else 0,
                          adjudicated=int(audit and a != b), final=(cat if (audit and a != b) else a), audited=int(audit)))
        # model-assisted: a pre-label on masked text, a person confirms or corrects every one
        pre = cat
        if rng.random() < (0.16 if c["variety"] in ("msa", "english") else 0.27):
            pre = [x for x in t["amb_pair"].split("|") if x != cat][0] if t["amb_pair"] else rng.choice([x for x in CATS if x != cat])
        if pre == cat:
            final = cat if rng.random() > 0.03 else rng.choice([x for x in CATS if x != cat])
        else:
            final = pre if rng.random() < 0.30 else cat  # anchoring: some wrong pre-labels are confirmed
        trial.append(dict(design="model_assisted", complaint_id=c["complaint_id"], label_1=final, label_2="", prelabel=pre,
                          seconds_1=int(rng.gauss(19 if final == pre else 38, 5)), seconds_2=0, adjudicated=0, final=final, audited=0))
    for r in trial:
        r["gold_label"] = T[r["complaint_id"]]["category"]
    wr(DATA / "ops" / "design_trial.csv", trial)
    mask_items = [c for c in corpus if T[c["complaint_id"]]["has_pii"]][:30] + [c for c in corpus if not T[c["complaint_id"]]["has_pii"]][:10]
    wr(DATA / "ops" / "to_prelabel.csv", [dict(complaint_id=c["complaint_id"], variety=c["variety"], text=c["text"]) for c in mask_items])
    wr(REF / "pii_truth.csv", [dict(complaint_id=c["complaint_id"], pii_kinds=T[c["complaint_id"]]["pii_kinds"],
                                     arabic_digits=int(any(ch in c["text"] for ch in "٠١٢٣٤٥٦٧٨٩"))) for c in mask_items])

    # ---------------- Day 3: four source tables, clean and seeded
    pops = {r[0]: rng.randrange(450, 3400) * 1000 for r in REGIONS}
    pops["R04"] = 620000
    regions = [dict(region_code=c, name_en=n, name_ar=a, population=pops[c], version="2026.1") for c, n, a in REGIONS]
    wr(DATA / "sources_clean" / "regions.csv", regions)
    wr(DATA / "sources" / "regions.csv", regions)
    reg_fields = ["merchant_id", "name_ar", "name_en", "cr_number", "sector", "region_code"]
    wr(DATA / "sources_clean" / "merchants.csv", merchants, reg_fields)
    wr(DATA / "sources" / "merchants.csv", registry, reg_fields)

    statuses = ["closed", "closed", "closed", "open", "referred"]
    extract, actions = [], []
    aid = 500001
    for c in corpus:
        t = T[c["complaint_id"]]
        rd = date.fromisoformat(c["received_date"])
        st = rng.choice(statuses)
        closed = (rd + timedelta(days=rng.randint(2, 40))).isoformat() if st == "closed" else ""
        mref = t["merchant_id"] if rng.random() > 0.20 else ""
        m = next(x for x in merchants if x["merchant_id"] == t["merchant_id"])
        region = m["region_code"] if rng.random() < 0.55 else rng.choice(REGIONS)[0]
        amount = round(rng.choice([99, 149, 249, 399, 899, 1299, 2499, 4999]) * rng.uniform(0.6, 1.4), 2)
        extract.append(dict(complaint_id=c["complaint_id"], received_date=c["received_date"], channel=c["channel"],
                            merchant_ref=mref, merchant_name_raw=t["merchant_raw"], product=t["product"], category_code=t["category"],
                            amount_sar=f"{amount:.2f}", region_code=region, status=st, closed_date=closed,
                            customer_key=rng.choice(nid_pool)))
        for _ in range(rng.choice([0, 1, 1, 2])):
            actions.append(dict(action_id=f"A{aid}", complaint_id=c["complaint_id"], action_type=rng.choice(["contact_merchant", "warning", "refund_ordered", "closed_no_action"]),
                                action_date=(rd + timedelta(days=rng.randint(1, 30))).isoformat(), officer_id=f"O{rng.randint(11, 48)}",
                                refund_sar=f"{amount:.2f}" if rng.random() < 0.2 else ""))
            aid += 1
    # legitimate same-day repeats: one customer, one merchant, one day, a different product (they must be kept)
    by_merchant = defaultdict(list)
    for e in extract:
        by_merchant[T[e["complaint_id"]]["merchant_id"]].append(e)
    touched = set()
    n_rep = 0
    for e in rng.sample(extract, 3000):
        if n_rep >= 2000 or e["complaint_id"] in touched:
            continue
        if n_rep < 60:  # a cluster in R04 in August: shoppers who report two products from one visit
            e["region_code"] = "R04"
            e["received_date"] = f"2026-08-{rng.randint(1, 28):02d}"
            e["closed_date"] = ""
            e["status"] = "open"
            C[e["complaint_id"]]["received_date"] = e["received_date"]
        cands = [x for x in by_merchant[T[e["complaint_id"]]["merchant_id"]] if x["product"] != e["product"] and x["complaint_id"] not in touched]
        if not cands:
            continue
        f2 = rng.choice(cands)
        f2.update(customer_key=e["customer_key"], received_date=e["received_date"], merchant_name_raw=e["merchant_name_raw"],
                  region_code=e["region_code"], merchant_ref=e["merchant_ref"])
        if f2["closed_date"] and f2["closed_date"] < f2["received_date"]:
            f2["closed_date"] = (date.fromisoformat(f2["received_date"]) + timedelta(days=5)).isoformat()
        C[f2["complaint_id"]]["received_date"] = e["received_date"]
        touched |= {e["complaint_id"], f2["complaint_id"]}
        n_rep += 1
    wr(DATA / "corpus" / "complaints_text.csv.gz", corpus, gz=True)
    clean = [dict(r) for r in extract]
    clean.sort(key=lambda r: r["complaint_id"])
    ex_fields = list(extract[0].keys())
    wr(DATA / "sources_clean" / "complaints_extract.csv.gz", clean, ex_fields, gz=True)
    wr(DATA / "sources_clean" / "case_actions.csv.gz", actions, gz=True)

    defects = defaultdict(list)
    resub_clean = []
    seeded = [dict(r) for r in extract]
    # D1 exact duplicate rows
    for r in rng.sample(seeded, 60):
        seeded.append(dict(r)); defects["D1_exact_duplicate"].append(r["complaint_id"])
    # D2 resubmissions: same customer, merchant and product within a day, new id and channel
    for k, r in enumerate(rng.sample(extract, 240)):
        rd = date.fromisoformat(r["received_date"]) + timedelta(days=rng.choice([0, 1]))
        if rd > END:
            rd = date.fromisoformat(r["received_date"])
        n = dict(r, complaint_id=f"C{300001 + k}", received_date=rd.isoformat(), channel=rng.choice([x for x in CHANNELS if x != r["channel"]]))
        seeded.append(n); defects["D2_resubmission"].append(n["complaint_id"]); resub_clean.append(dict(n))
    by_id = {r["complaint_id"]: r for r in seeded}
    pool_ids = sorted({r["complaint_id"] for r in extract})
    rng2 = random.Random(SEED + 1)
    # D3 closed before received
    for cid in rng2.sample([i for i in pool_ids if by_id[i]["closed_date"]], 85):
        r = by_id[cid]; r["closed_date"] = (date.fromisoformat(r["received_date"]) - timedelta(days=rng2.randint(1, 9))).isoformat()
        defects["D3_closed_before_received"].append(cid)
    # D4 amounts in halalas: app channel, August 2026
    for r in seeded:
        if r["channel"] == "app" and r["received_date"].startswith("2026-08"):
            r["amount_sar"] = f"{float(r['amount_sar']) * 100:.2f}"
            defects["D4_halalas"].append(r["complaint_id"])
    # D5 unknown or empty region
    for cid in rng2.sample(pool_ids, 600):
        r = by_id[cid]; r["region_code"] = "" if rng2.random() < 0.63 else "R99"; defects["D5_region"].append(cid)
    # D7 invalid category codes
    for cid in rng2.sample(pool_ids, 170):
        r = by_id[cid]; r["category_code"] = "C7" if rng2.random() < 0.53 else r["category_code"].lower(); defects["D7_category_code"].append(cid)
    # D8 future dates
    for cid in rng2.sample(pool_ids, 12):
        r = by_id[cid]; r["received_date"] = date(2027, rng2.randint(1, 6), rng2.randint(1, 28)).isoformat(); r["closed_date"] = ""; defects["D8_future_date"].append(cid)
    seeded.sort(key=lambda r: r["complaint_id"])
    wr(DATA / "sources" / "complaints_extract.csv.gz", seeded, ex_fields, gz=True)
    s_actions = [dict(a) for a in actions]
    for k in range(150):
        s_actions.append(dict(action_id=f"A{900001 + k}", complaint_id=f"C{rng2.randint(700000, 799999)}", action_type="warning",
                              action_date=date(2026, rng2.randint(1, 8), rng2.randint(1, 28)).isoformat(), officer_id=f"O{rng2.randint(11, 48)}", refund_sar=""))
        defects["D6_orphan_action"].append(f"A{900001 + k}")
    wr(DATA / "sources" / "case_actions.csv.gz", s_actions, gz=True)
    defects["D9_registry_duplicate"] = [d["merchant_id"] for d in dup_reg]
    wj(REF / "seeded_defects.json", {k: dict(count=len(v), examples=v[:5]) for k, v in defects.items()})

    # Lab 3.3: 600 raw merchant names, 300 of them labelled
    raw = []
    for k in range(560):
        m = rng.choice(merchants)
        raw.append(dict(raw_id=f"N{k + 1:04d}", name_raw=raw_variant(m, rng), truth=m["merchant_id"]))
    for k in range(40):
        u = UNKNOWN[k % len(UNKNOWN)]
        raw.append(dict(raw_id=f"N{561 + k:04d}", name_raw=u[0] if k % 2 else u[1], truth="NONE"))
    rng.shuffle(raw)
    wr(DATA / "matching" / "merchant_raw.csv", [dict(raw_id=r["raw_id"], name_raw=r["name_raw"]) for r in raw])
    lab = [r for r in raw if r["truth"] == "NONE"][:30] + [r for r in raw if r["truth"] != "NONE"][:270]
    lab.sort(key=lambda r: r["raw_id"])
    wr(DATA / "matching" / "labelled_300.csv", [dict(raw_id=r["raw_id"], name_raw=r["name_raw"], merchant_id=r["truth"]) for r in lab])

    # ---------------- Day 4: two refreshes and their lineage, built from the clean extract
    late = []
    for k in range(260):
        base_r = rng.choice([r for r in clean if r["received_date"].startswith("2026-08")])
        late.append(dict(base_r, complaint_id=f"C{400001 + k}", received_date=f"2026-08-{rng.randint(20, 31):02d}",
                         customer_key=rng.choice(nid_pool), status="open", closed_date=""))
    regions_v2 = [dict(r, population=int(r["population"] * (1.055 if r["region_code"] == "R04" else 1.01)), version="2026.2") for r in regions]
    # The raw extracts each refresh saw: clean rows plus the resubmissions the portal really sends
    run_a_raw = clean + resub_clean
    run_b_raw = run_a_raw + late
    runs = DATA / "runs"
    wr(runs / "regions_v2026_1.csv", regions)
    wr(runs / "regions_v2026_2.csv", regions_v2)
    wr(runs / "run_a" / "stage_clean.csv.gz", sorted(run_a_raw, key=lambda r: r["complaint_id"]), ex_fields, gz=True)
    wr(runs / "run_b" / "stage_clean.csv.gz", sorted(run_b_raw, key=lambda r: r["complaint_id"]), ex_fields, gz=True)

    def dedupe(rows, key):
        seen, out = set(), []
        for r in sorted(rows, key=lambda r: (r["received_date"], r["complaint_id"])):
            k = key(r)
            if k in seen:
                continue
            seen.add(k); out.append(r)
        return out

    def dd_id(r):
        return r["complaint_id"]

    def dd_day(r):
        return (r["customer_key"], r["merchant_name_raw"], r["received_date"])

    def rate(rows, regs, region="R04", month="2026-08"):
        pop = {r["region_code"]: r["population"] for r in regs}[region]
        n = sum(1 for r in rows if r["region_code"] == region and r["received_date"].startswith(month))
        return n, round(n / pop * 100000, 2)

    a_rows = dedupe(run_a_raw, dd_id)
    b_rows = dedupe(run_b_raw, dd_day)
    na, ra = rate(a_rows, regions)
    nb, rb = rate(b_rows, regions_v2)

    def run_log(name, refresh, raw_rows, after, regs, dedupe_key, commit):
        return {"run_id": name, "refresh_date": refresh, "code_version": commit, "lock_file_sha256": "3b1f0c9e5a7d2e64",
                "inputs": [{"name": "complaints_extract", "rows": len(raw_rows)}, {"name": "regions", "version": regs[0]["version"], "rows": len(regs)}],
                "steps": [{"step": "extract", "rows_in": len(raw_rows), "rows_out": len(raw_rows)},
                          {"step": "clean", "rows_in": len(raw_rows), "rows_out": len(raw_rows)},
                          {"step": "dedupe", "rows_in": len(raw_rows), "rows_out": len(after), "params": {"key": dedupe_key}},
                          {"step": "enrich", "rows_in": len(after), "rows_out": len(after), "params": {"regions_version": regs[0]["version"]}},
                          {"step": "publish", "rows_in": len(after), "rows_out": len(after)}],
                "rules": {"blocking_failed": 0, "warnings": 1, "quarantined": 0}}

    la = run_log("run_a", "2026-09-05", run_a_raw, a_rows, regions, ["complaint_id"], "a41c2e7")
    lb = run_log("run_b", "2026-10-05", run_b_raw, b_rows, regions_v2, ["customer_key", "merchant_name_raw", "received_date"], "c9d05b3")
    wj(runs / "run_a" / "run_log.json", la)
    wj(runs / "run_b" / "run_log.json", lb)

    def lineage(log, regs):
        ev = []
        prev = {"namespace": "bayyin-portal", "name": "complaints_extract", "facets": {"rows": log["inputs"][0]["rows"]}}
        for s in log["steps"]:
            out = {"namespace": "bayyin-prep", "name": f"complaints_{s['step']}", "facets": {"rows": s["rows_out"]}}
            inputs = [prev]
            if s["step"] == "enrich":
                inputs.append({"namespace": "bayyin-reference", "name": "regions", "facets": {"version": regs[0]["version"]}})
            ev.append({"eventType": "COMPLETE", "eventDate": log["refresh_date"], "run": {"runId": f"{log['run_id']}-{s['step']}", "facets": {"parent": log["run_id"], "code_version": log["code_version"], "params": s.get("params", {})}},
                       "job": {"namespace": "bayyin-prep", "name": s["step"]}, "inputs": inputs, "outputs": [out]})
            prev = out
        return ev

    for nm, log, regs in (("run_a", la, regions), ("run_b", lb, regions_v2)):
        (runs / nm / "lineage.jsonl").write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in lineage(log, regs)), encoding="utf-8", newline="\n")
    (runs / "git_log.txt").write_text(
        "c9d05b3 dedupe on customer, merchant and day\n"
        "7e21a90 load regions from the reference service\n"
        "a41c2e7 publish the monthly rate by region\n", encoding="utf-8", newline="\n")
    figs = {}
    for nm, rows_, regs in (("run_a", a_rows, regions), ("run_b", b_rows, regions_v2)):
        out = []
        for reg in [r[0] for r in REGIONS]:
            n, rt = rate(rows_, regs, reg)
            out.append(dict(region_code=reg, month="2026-08", complaints=n, rate_per_100k=rt))
        wr(runs / nm / "figures.csv", out)
        figs[nm] = out

    # the corrected run: late arrivals and the new population kept; resubmissions removed; repeats kept
    def dd_resub(r):
        return (r["customer_key"], r["merchant_name_raw"], r["product"])

    def dedupe_window(rows):
        out, last = [], {}
        for r in sorted(rows, key=lambda r: (r["received_date"], r["complaint_id"])):
            k = dd_resub(r); d = date.fromisoformat(r["received_date"])
            if k in last and (d - last[k]).days <= 1:
                continue
            last[k] = d; out.append(r)
        return out

    c_rows = dedupe_window(run_b_raw)
    nc, rc = rate(c_rows, regions_v2)
    steps = {}
    n1, r1_ = rate(dedupe(run_b_raw, dd_id), regions)          # late arrivals only
    n2, r2_ = rate(dedupe(run_b_raw, dd_id), regions_v2)       # + new population
    n3, r3_ = rate(b_rows, regions_v2)                         # + new dedupe key
    steps = dict(run_a=dict(n=na, rate=ra), late_arrivals=dict(n=n1, rate=r1_), new_population=dict(n=n2, rate=r2_),
                 new_dedupe_key=dict(n=n3, rate=r3_), run_b=dict(n=nb, rate=rb), corrected=dict(n=nc, rate=rc))
    wj(REF / "d4_3_attribution.json", steps)

    # ---------------- reference results for the safety nets and the answer key
    def labels_of(rows):
        return [[r["R1"], r["R2"], r["R3"]] for r in rows]

    wj(REF / "pilot_truth.json", {c["complaint_id"]: T[c["complaint_id"]]["category"] for c in pilot})
    wj(REF / "summary.json", dict(
        corpus=len(corpus), categories=dict(Counter(t["category"] for t in truth)), varieties=dict(Counter(c["variety"] for c in corpus)),
        pii_share=round(sum(t["has_pii"] for t in truth) / len(truth), 3), distressing=sum(t["distressing"] for t in truth),
        pilot_ambiguous=sum(1 for c in pilot if T[c["complaint_id"]]["amb_pair"]), ops_rows=len(ops),
        extract_clean=len(clean), extract_seeded=len(seeded), actions=len(actions), regions=len(regions), merchants=len(merchants),
        r04_aug=steps))
    print("corpus", len(corpus), "| pilot", len(pilot), "| ops rows", len(ops), "| extract", len(clean), "->", len(seeded))
    print("R04 August:", json.dumps(steps))


if __name__ == "__main__":
    main()
