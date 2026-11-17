# Pre-work and follow-up

## Before Day 1 (about two hours)

1. Run `00_setup_check.ipynb` locally or on Colab until every check is green. A missing model key is
   fine: the labs use a scripted stand-in when no key is set.
2. Re-read the six data-quality dimensions (completeness, uniqueness, validity, consistency,
   accuracy, timeliness) from DS-202, and the lock-file and Git sections of FN-102.
3. Read the Data Classification Policy's four levels (Top Secret, Secret, Restricted, Public) and the
   rule in the Generative AI Guidelines for Government against entering Restricted data into
   generative AI tools. Day 2's masking lab depends on both.

## The tracked follow-up task (within four weeks)

Take one table from your own work that someone else reads or publishes from.

1. Profile it and write at least five rules, each with an owner, a dimension, a threshold and a
   severity.
2. Write an ODCS v3.2.0 contract for the table your consumers read, and compile it to SQL checks.
3. Run both twice in a pipeline that writes a run log: once on the current data, once on a copy where
   you seeded one defect of your own choosing.
4. Send the trainer the two run logs, the rules and the contract, with three sentences: what the
   rules found on the real data, who owns each threshold, and what you changed as a result.

If the table holds personal or Restricted data, send the run logs and the rules only, never the data,
and mask any example values.
