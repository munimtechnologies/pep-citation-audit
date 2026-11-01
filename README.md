# pep-citation-audit

Do CPython's docs cite the right PEP? This tool reads every `Doc/**/*.rst` file in python/cpython,
finds each PEP number written next to a short label (`PEP 695: Type Parameter Syntax`,
`:pep:`3156` -- Asynchronous IO ...`, `* :ref:`PEP 697 <...>`, unstable C API tier`), and checks the
label against the titles of all PEPs in https://peps.python.org/api/peps.json. When another PEP's
title fits the label much better than the cited one, the line is flagged for a person to read.

By MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Code Apache-2.0; text and results
CC BY 4.0.

## Status

- 2026-10-31: pre-registered (PREREG.md) before the data run. The positive control is a real error
  found by hand in munimtechnologies/pep-version-whatsnew-audit: What's New in Python 3.12 credits
  the Unstable C API tier to PEP 697 instead of PEP 689.
- 2026-11-01: run 1 graded (GRADING.md). 636 citation pairs in 71 files. P1 (control found) and P2
  (97.6% of dash-separated title pairs match) held. P3 and P4 **failed**: the one new lead was
  the right PEP, and a read of all 89 weak rows found no other clear-cut wrong number (one
  debatable 2.7 case). The 3.12 slip looks isolated. FIXLIST.md has the details; results are in
  `results/`.

## Run

```
python -m unittest -v
python job.py --data-dir data --out-dir out
```

Standard library only. Outputs: `out/summary.json` (verdicts, leads, source hashes and CPython
commit), `out/rows.csv` / `out/rows.json` (every pair), `out/flagged.csv` (every pair not `ok`),
`out/snapshot/` (peps.json copy and a SHA-256 for every rst file read).

## Use it on your own docs

`citecheck.audit({path: text}, {pep_number: title})` works on any reStructuredText or Markdown text
that cites PEPs, for example a library's changelog.
