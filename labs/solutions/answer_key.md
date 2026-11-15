# Answer key for trainers

The numbers each solution notebook prints with the data of `prepare_data.py` (seed 311). A
participant's numbers should match wherever the lab fixes the method; where the lab asks for a
judgement (a guideline's wording, the list of anomalies), the key gives one defensible answer.

| Lab | What the solution shows |
|---|---|
| 1.1 Label 40 complaints | 26 of 40 complaints get the same label from all three; the most split pairs are DEFECT/REFUND (6) and AD/PRICE (6). |
| 1.2 Definitions and rules | Guideline v1.0 with six definitions and ordered decision rules; it passes the lint and decides all 12 edge cases. |
| 1.3 Kappa and alpha | Pairwise kappa 0.601, 0.619, 0.564; alpha 0.594. WARRANTY alpha 0.164 (0.061 to 0.267). Varieties: MSA 0.669, Gulf 0.470, English 0.674, mixed 0.340. Largest coincidence pair DEFECT-REFUND (36.5). |
| 1.4 Adjudicate 30 | Adjudication matches the reference on all 30; R3 chose DEFECT six times where the rule says REFUND; 8 of 28 majorities overturned (example C103462). Round 2 alpha 0.789 (0.744 to 0.825). |
| 2.1 Stratified golden set | Random 240: 4 WARRANTY, 18 mixed. Stratified with a floor of six: 29 WARRANTY, 42 mixed. Weighted WARRANTY share 0.034 against 0.025 in the corpus. |
| 2.2 Gold and queues | Gold accuracy R5 0.712, R6 0.725, both on watch, and R3 0.888 on watch by a hair (lower bound 0.7998, shown as 0.800 when rounded). Queues: accept 1,081, re-label 731, adjudicate 139, restricted 64; no breach of the routing rules. |
| 2.3 Drifting rater | R5 from 0.975 to 0.375 (z = 5.37): drift, 211 labels to re-check. R6 steadily low. R4 had 69.4 minutes of distressing content on day 7. |
| 2.4 Cost per accepted label | A naive phone pattern leaves 19 of 40 with an identifier. Double SAR 1.94 at 0.3% error; audited single SAR 0.93 at 5.0%; model-assisted SAR 0.37 at 10.0%. 28% of wrong pre-labels confirmed. |
| 3.1 Profile, propose rules | Anomalies: 60 duplicate ids, 170 invalid codes, 619 amounts above SAR 50,000 (max 694,783), 12 future dates, 85 closed before received, 600 bad regions, 150 orphan actions, 3 registry duplicates. Nine proposed rules over six dimensions. |
| 3.2 Warning and blocking | A01 (619) and A02 (1,195) stop the run; the other rules quarantine or log. Every listed defect caught in full; no rule fires on the clean tables. Pandera: 120, 170, 619. |
| 3.3 Merchant names | Arabic and English registry names give the same key for all 150 merchants. Precision 1.000 and recall 0.981 at threshold 60; five misses, all misspelt sector words. Blocking: 1,354 comparisons of 90,000. |
| 3.4 Contract | 23 of 23 checks pass on the 30,000-row table. Change A (rename, text amounts) fails 3 checks; change B (added nullable column) passes. Versions 2.0.0, 1.1.0, 1.0.1. |
| 4.1 Steps and runner | Causes in cells 2 (clock), 3 (state changed in place), 4 (unseeded shuffle), 5 (set order). Two runs write the same bytes; DuckDB 2.0.0 as pinned. |
| 4.2 Quarantine and block | Rule-by-rule quarantine counts 970 orphan actions (150 when all rules judge first). Seeded: exit 2, blocked by A01 and A02. Corrected: exit 0, 915 complaints and 150 actions quarantined. The clone publishes the same bytes. |
| 4.3 Changed figure | R04 August: 48.06 → 52.90 (late arrivals) → 50.15 (population) → 39.14 (dedupe key). Corrected 49.53 (324 complaints). All 13 regions' October figures off by more than 1%; R04 by 21%. |
| 4.4 Datasheet section | 30,300 extracted, 915 quarantined, 231 resubmissions removed, 29,154 published, 23 contract checks; alpha 0.789, mixed 0.743, WARRANTY 0.68. Every number traced. |

## Which labs call a model

Only Lab 2.4 (pre-labels by Fahis) calls a hosted model, through `bayyin.chat()`. With a free
OpenRouter key it uses the model named in `.env`; without one, or when the key is refused, it uses
the scripted stand-in and says so. The numbers above for Lab 2.4 come from the stand-in.
