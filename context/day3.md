---
course: "Data Quality, Labelling and Pipelines for Analysis"
code: "DS-311"
version: "2027.1.0"
deck: "day3"
day: 3
language: "en"
view: "trainee"
source: "https://sdaiaacademy.github.io/ds-311/slides/day3.html"
---

# Data Quality, Labelling and Pipelines for Analysis

## Day 3: Rules and contracts

Turn analysts' requirements into rules and a contract

#### [day3#title] Rules and contracts

*SDAIA Academy · Data Quality, Labelling and Pipelines for Analysis*

Day 3: Turn analysts' requirements into rules and a contract

Data Science Track · 4 teaching days + capstone day · 4 sessions · 4 labs · DS-311

#### [day3#review-day2] Who needs which response?

*Review of Day 2*

**Question:** Over ten days R5 and R6 both average about 0.72 on gold. R5 scored 0.975 in the first five days and 0.375 in the last three; R6 stayed between 0.68 and 0.79. What do you do?

- A. Coach both raters the same way
- B. Re-check R5's recent labels; coach R6 and double-label its work
- C. Re-check R6's recent labels; leave R5, whose average is the same
- D. Wait for more gold answers before doing anything

#### [day3#agenda] Rules and contracts

*Today*

- **Session 1 · Profiling to rules**: A profile of each source table, read against the six quality dimensions, becomes rules with owners and thresholds
- **Session 2 · Rules with severity**: Warn, quarantine or block: a rule as a query that returns failing rows, judged on seeded defects and on clean data
- **Session 3 · Duplicates and merchant matching**: Exact and near duplicates, and merchant names matched across Arabic and Latin spellings with measured precision
- **Session 4 · A data contract**: A contract in an open standard that the producer and the consumer of the prepared table both check

### Session 1: Profiling to rules

#### [day3#s1] Profiling to rules

*Session 1*

- Profile tables for completeness, uniqueness, validity, consistency, accuracy and timeliness
- Read anomalies from a profile without help
- Write a rule with an owner, a dimension, a threshold and a business reason

#### [day3#four-tables] Four tables feed one published rate

*What Bayyin prepares every month*

- **Complaints.** The portal extract of 5 September: 30,300 rows, one per complaint, with its category from the labels.
- **Merchants.** The registry: 153 rows, Arabic and English names, a commercial registration number.
- **Regions.** Thirteen regions with their populations: the denominator of the rate.
- **Case actions.** 30,148 actions taken by officers: warnings, referrals, refunds.

> **What goes wrong.** Each table can be correct on its own and the join still wrong: a missing region drops a complaint from the rate silently.

#### [day3#six-dimensions] Six dimensions organise what a profile can show

*The NDMO Data Quality domain*

| Dimension | The question | In Bayyin's extract |
| --- | --- | --- |
| Completeness | Is the value there? | Region empty on 414 complaints |
| Uniqueness | Is each thing recorded once? | 60 complaint ids appear twice |
| Validity | Is the value allowed? | Category "defect" and "C7"; region R99 |
| Consistency | Do related values agree? | 85 closed before they were received |
| Accuracy | Is the value true? | Amounts of SAR 694,783 |
| Timeliness | Is it recent enough? | Newest complaint against the extract date |

#### [day3#profile-as-text] Profile the values as they arrived, loaded as text

*Lab 3.1, before any rule*

```sql
-- file: profile(table)
SELECT count(*) FILTER (WHERE c IS NULL
                         OR trim(c) = '') AS empty,
       count(DISTINCT c)  AS distinct_values,
       min(c), max(c), mode(c),
       min(TRY_CAST(c AS DOUBLE)),
       max(TRY_CAST(c AS DOUBLE))
FROM complaints
```

- **Why text.** A typed load turns "warranty" or "2027-06-25" into an error or a NULL before anyone sees it.
- **AI-off.** Lab 3.1 is done without an assistant: reading a profile is the skill.

#### [day3#profile-findings] The profile points at the anomalies; one query confirms each

*Lab 3.1, read from the profile*

| What the profile shows | Confirmed by | Rows |
| --- | --- | --- |
| 30,300 rows, 30,240 distinct ids | count minus count distinct | 60 |
| 13 category codes for six categories | codes outside the six | 170 |
| Maximum amount SAR 694,783 | amounts above SAR 50,000 | 619 |
| Latest received date 2027-06-25 | after the extract date | 12 |
| 14 region codes for 13 regions; 414 empty | not in the regions table | 600 |
| Actions for 22,676 complaint ids | action without a complaint | 150 |

#### [day3#halala-batch] August's app batch arrived in halalas

*The anomaly the maximum hides*

| Item | Value |
| --- | --- |
| App, June | SAR 545 |
| App, July | SAR 694 |
| App, August | SAR 54,706 |
| Web, August | SAR 530 |

Median amount by month and channel. Multiplied by 100, only 619 of the 1,195 amounts pass SAR 50,000.

#### [day3#rule-anatomy] A rule names its owner, dimension, attributes and threshold

*What a rule must state*

```python
# file: pipeline/rules.py
dict(id="C01", dimension="completeness",
     owner="Hatoon Al-Furaih",
     table="complaints",
     description="Every complaint has a region: "
                 "the rate is published by region",
     attributes=["region_code"],
     severity="quarantine", max_rate=0.03,
     sql="SELECT rid FROM complaints WHERE "
         "region_code IS NULL OR trim(region_code) = ''")
```

- **Owner.** Who accepts the threshold and answers when the rule fires.
- **Business description.** Why the figure needs it, in the user's words.
- **Threshold.** The share of failing rows the owner accepts.

#### [day3#checkpoint-1] Is the maximum enough?

*Checkpoint*

**Question:** The profile shows a maximum amount of SAR 694,783. Abdulelah proposes one rule: "no amount above SAR 50,000". August's app batch was sent in halalas. What does his rule miss?

- A. The halala amounts that stayed under SAR 50,000; a rule on the batch's median catches them
- B. Nothing: every halala amount is above SAR 50,000
- C. The duplicated complaints of August
- D. Only amounts between SAR 40,000 and 50,000; lower the limit to 40,000

#### [day3#lab-3-1] Profile four tables, propose rules

Lab 3.1 · 25 min

Profile four source tables in DuckDB without AI help, find the anomalies, and propose rules with a dimension, an owner, a threshold and a reason.

[D3_1_profile_four_source.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D3_1_profile_four_source.ipynb)

- [ ] Profile each table in DuckDB (8 min)
- [ ] Five anomalies from the profile (7 min)
- [ ] Rules with dimension, owner and threshold (10 min)
- [ ] ✱ Stretch: Timeliness: how old is the newest complaint in each extract?

### Session 2: Rules with severity

#### [day3#s2] Rules with severity

*Session 2*

- Write a rule as a query that returns the failing rows
- Give each rule a severity: warn, quarantine or block
- Show that the rules catch each seeded defect and stay quiet on clean data

#### [day3#rule-as-query] A rule is a query that returns the failing rows

*One shape for every rule*

```sql
-- file: K01
SELECT rid FROM complaints
WHERE coalesce(closed_date, '') <> ''
  AND TRY_CAST(closed_date AS DATE)
    < TRY_CAST(received_date AS DATE)
```

- The same query **counts** failures, **lists** them and **moves** them to quarantine.
- Every table gets a row id, `rid`, so a failing row can be named.
- Rules run on text: a bad value fails the rule, not the load.

#### [day3#severity-ladder] Warn, quarantine or block

*What happens when a rule fails*

1. **Warn** log it; the run goes on
2. **Quarantine** set the failing rows aside with the rule id; stop above the threshold
3. **Block** stop before anything is published

> **Choosing.** Quarantine when the remaining rows are still right; block when the error could be in rows that look fine.

#### [day3#rule-results] Two accuracy rules stop the run; the rest quarantine or log

*Lab 3.2, the seeded extract*

| Rule | Dimension | Owner | Failing | Threshold | Action |
| --- | --- | --- | --- | --- | --- |
| U01 one row per id | uniqueness | Abdulelah | 60 | 0.5% | quarantined |
| C01 region present | completeness | Hatoon | 414 | 3% | quarantined |
| V02 category valid | validity | Khulood | 170 | 1% | quarantined |
| K01 closed after received | consistency | Abdulelah | 85 | 0.5% | quarantined |
| A01 amount ≤ SAR 50,000 | accuracy | Hatoon | 619 | 0.1% | stop |
| A02 monthly median by channel | accuracy | Hatoon | 1,195 | 0.1% | stop |
| U02 one entry per CR number | uniqueness | Abdulelah | 3 | 0 | logged |

#### [day3#judge-both-ways] Catch every seeded defect, and stay quiet on clean data

*How a rule set is judged*

- **On the seeded extract.** Eight listed defects, each caught in full by the rule meant for it: 60 duplicates, 600 regions, 170 codes, 85 dates out of order, 1,195 halala amounts, 12 future dates, 150 orphan actions, 3 registry duplicates.
- **On the clean extract.** The same eleven rules on the same month without defects: no rule fails a single row.

> **What goes wrong.** A rule that fires on good data trains people to ignore it, and then to switch it off.

#### [day3#pandera] A validation library expresses the same rules as a schema

*The same checks in a framework*

```python
# file: Pandera, stretch of Lab 3.2
pa.DataFrameSchema({
  "complaint_id": pa.Column(str, unique=True),
  "category_code": pa.Column(str,
      pa.Check.isin(SIX)),
  "amount_sar": pa.Column(float,
      pa.Check.le(50000), nullable=True),
})
```

- Finds the same failures: 120 rows in duplicated ids, 170 codes, 619 amounts.
- Keeps owners, severities and thresholds outside the schema: you still need them.
- The SQL rules run where the data is; the schema runs where the DataFrame is.

#### [day3#checkpoint-2] What should C01 do?

*Checkpoint*

**Question:** C01 (region present) is a quarantine rule with a 3% threshold. This month 414 of 30,300 complaints, 1.4%, have no region. What happens to the run?

- A. The run stops before publishing
- B. The rows are published with an empty region and a warning
- C. The 414 rows go to quarantine with C01; the run goes on
- D. The rows are given the most common region and published

#### [day3#lab-3-2] Warning and blocking rules

Lab 3.2 · 25 min

Implement the rule set as SQL with thresholds and severities, catch every seeded defect in the four tables, and show no false alarm on the clean tables.

[D3_2_implement_warning_blocking.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D3_2_implement_warning_blocking.ipynb)

- [ ] A rule as a query that returns failing rows (5 min)
- [ ] The rule set with thresholds and severities (9 min)
- [ ] Every seeded defect caught (6 min)
- [ ] No alarm on the clean tables (5 min)
- [ ] ✱ Stretch: Three of the rules again in Pandera

### Session 3: Duplicates and merchant matching

#### [day3#s3] Duplicates and merchant matching

*Session 3*

- Tell exact duplicates from resubmissions
- Normalise Arabic and Latin names and compare them through a transliteration key
- Choose a match threshold from precision and recall on labelled pairs

#### [day3#exact-vs-near] An exact duplicate is an export fault; a resubmission is a person

*Duplicates*

- **Exact duplicates: 60.** The same complaint id twice. The portal's export wrote a row again. Rule U01 quarantines the second copy.
- **Resubmissions: 240.** A new id, the same customer, merchant and product, a day later: the complainant tried again. Each row is valid.

> **What goes wrong.** A key too wide merges real repeat complaints; a key too narrow counts one problem twice. The choice of key changes the rate.

#### [day3#merchant-spellings] One merchant, written a dozen ways

*The merchant on a complaint*

| As typed by the complainant | Registry |
| --- | --- |
| مؤسسة النور للإلكترونيات المحدودة | M1001 |
| AL-NOOR ELECTRONICS CO. | M1001 |
| Alnoor Elec. | M1001 |
| النور Electronics | M1001 |
| شركة الفارسللأزياء المحدودة | M1130 |

600 raw names in the lab; 300 are labelled with the right registry id, or NONE.

#### [day3#transliteration-key] Normalise, then compare consonant skeletons

*Lab 3.3, comparing across scripts*

1. **1 · Normalise** unify أ إ آ, ة, ى; drop legal forms and the article
2. **2 · Sector** stems in both scripts: «لكترون», "elec"
3. **3 · Skeleton** consonants in Latin letters
4. **4 · Key** "nr|electronics"

«النور للإلكترونيات» and "Al-Noor Electronics" both give `nr|electronics`. The Arabic and English names agree on the key for all 150 merchants.

#### [day3#precision-first] Choose the threshold by precision first

*Lab 3.3, 300 labelled names*

| Threshold | Matched | Precision | Recall |
| --- | --- | --- | --- |
| 60 | 265 | 1.000 | 0.981 |
| 70 | 262 | 1.000 | 0.970 |
| 85 | 259 | 1.000 | 0.959 |
| 100 | 258 | 1.000 | 0.956 |

A tie between two merchants returns NONE. The five misses are typing errors in the sector word.

#### [day3#blocking] Blocking compares only names that could match

*Stretch of Lab 3.3*

**1,354** comparisons when blocked by sector and first letter, of 90,000

- Fine for 600 names; essential for 30,000 complaints a month.
- A block that is too strict hides true matches: check recall after blocking.
- Libraries for record linkage do the same with more care.

#### [day3#checkpoint-3] Should a bare name match?

*Checkpoint*

**Question:** A complainant writes only «النور», with no sector. Six registry merchants share that name: electronics, furniture, appliances, fashion, auto parts and jewellery. All score 100. What should the matcher return?

- A. The first of the six in the registry
- B. The one with the most complaints this year
- C. Raise the threshold until only one remains
- D. NONE, until someone checks the complaint text

#### [day3#lab-3-3] Merchant names across two scripts

Lab 3.3 · 25 min

Normalise 600 raw merchant names, match them to the registry across Arabic and Latin spellings, choose a threshold, and measure precision and recall on 300 labelled names.

[D3_3_match_merchant_names.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D3_3_match_merchant_names.ipynb)

- [ ] Normalise Arabic and Latin names (7 min)
- [ ] A transliteration key across scripts (6 min)
- [ ] Score, and choose a threshold (6 min)
- [ ] Precision and recall on 300 labelled names (6 min)
- [ ] ✱ Stretch: Blocking: compare fewer pairs

### Session 4: A data contract

#### [day3#s4] A data contract

*Session 4*

- Write a contract for a table in the Open Data Contract Standard
- Compile its quality clauses to SQL checks
- Tell a breaking schema change from a compatible one

#### [day3#producer-consumer] A contract writes down what the consumer relies on

*A data contract*

- **Producer: Abdulelah.** Runs the preparation pipeline and publishes `complaints_prepared`. Runs the contract before publishing.
- **Consumer: Hatoon.** Builds the monthly rate from it. Agrees the clauses; can run the contract on arrival.

> **What goes wrong.** Without a contract, a renamed column breaks the report on the morning it is due, and nobody knew it was relied on.

#### [day3#odcs-schema] The schema part: one property per column the consumer uses

*The Open Data Contract Standard, v3.2.0*

```yaml
# file: contract.odcs.yaml
apiVersion: v3.2.0
kind: DataContract
id: bayyin-complaints-prepared
version: 1.0.0
schema:
- name: complaints_prepared
  properties:
  - name: complaint_id
    logicalType: string
    physicalType: VARCHAR
    required: true
    primaryKey: true
  - name: region_code
    ...
```

- An open, vendor-neutral standard maintained by the Bitol project of the Linux Foundation.
- Ten properties for the ten columns of today's table.
- `description` says purpose, usage and limitations, in words.

#### [day3#quality-clauses] A small library of metrics, or a SQL query that returns a number

*Quality clauses*

```yaml
# file: contract.odcs.yaml
- name: category
  quality:
  - metric: invalidValues
    arguments:
      validValues: [REFUND, DEFECT, DELIVERY,
                    PRICE, AD, WARRANTY]
    mustBe: 0
- name: amount_sar
  quality:
  - type: sql
    query: SELECT count(*) FROM ${object}
           WHERE ${property} > 50000
    mustBe: 0
```

- Library metrics: nullValues, missingValues, invalidValues, duplicateValues, rowCount.
- Operators: mustBe, mustBeGreaterThan, mustBeLessThan and their kin.
- Six clauses in Lab 3.4, plus "required" on seven columns.

#### [day3#compile-to-sql] Every clause becomes one query and one comparison

*Lab 3.4, a contract that runs*

```python
# file: compile_clause()
if m == "duplicateValues":
    return (f"SELECT count({col}) - "
            f"count(DISTINCT {col}) FROM {t}")
if m == "invalidValues":
    return (f"SELECT count(*) FROM {t} "
            f"WHERE {col} NOT IN ({vals})")
```

**23 of 23** checks pass on today's 30,000-row table

- **Types first.** Each column's type is checked before its values.

#### [day3#breaking-vs-compatible] A rename fails the contract; an added column passes

*Lab 3.4, two proposed changes*

| Change | Contract result | Version |
| --- | --- | --- |
| A: `region_code` renamed to `region`; `amount_sar` sent as "SAR 120.00" | 3 checks fail: column missing, type changed, amount clause cannot run | 2.0.0 |
| B: a nullable `merchant_name` added | every check passes | 1.1.0 |
| A corrected description | nothing to check | 1.0.1 |

#### [day3#checkpoint-4] Which change breaks the contract?

*Checkpoint*

**Question:** The contract for `complaints_prepared` lists ten columns. Which change by the producer should fail the contract check?

- A. Adding a nullable column `merchant_name`
- B. Sending `amount_sar` as text such as "SAR 120.00"
- C. Correcting the description of `status`
- D. Publishing 31,000 rows instead of 30,000

#### [day3#lab-3-4] A contract that rejects a breaking change

Lab 3.4 · 25 min

Write an ODCS contract for the prepared complaints table, compile its clauses to SQL, pass it on today's table, and make a producer's breaking change fail while an added column passes.

[D3_4_write_contract_prepared.ipynb](https://sdaiaacademy.github.io/ds-311/labs/D3_4_write_contract_prepared.ipynb)

- [ ] The schema part of the contract (7 min)
- [ ] Quality clauses from the rules (5 min)
- [ ] Compile the clauses to SQL and run them (7 min)
- [ ] A breaking change fails; an added column passes (6 min)
- [ ] ✱ Stretch: The version number each change needs

#### [day3#wrap-up] Three things to keep

*Day 3 · wrap-up*

- **A rule has an owner.** Dimension, attributes, threshold and a reason; judged on seeded defects and on clean data.
- **Precision before recall.** A wrong match blames someone; a tie returns NONE.
- **A contract that runs.** The consumer's columns and clauses, compiled to SQL, checked before publishing.

#### [day3#next] Day 4: Pipelines for analysis

*Next*

From a notebook to a pipeline that gives the same bytes twice, stops on a blocking rule, and explains why August's rate changed.
