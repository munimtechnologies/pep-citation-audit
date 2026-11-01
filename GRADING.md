# Grading: do CPython's docs cite the right PEP? (run 1)

MV2, Munim, Inc. (mv2@munimtech.com). Graded 2026-11-01 against PREREG.md, which was filed on
2026-10-31 before the data run. Made with AI agents working in MV2's name; every lead below was
read in the rst source at the commit the run used. Code Apache-2.0; text and results CC BY 4.0.

## Data the run used

- python/cpython `main` at commit `9c0cfb141c236c902954841bb6cca407f86e1eeb` (tarball SHA-256
  `dbfd6da9...5ea46`), 560 `Doc/**/*.rst` files, fetched 2026-11-01T08:33Z.
- peps.json with 747 PEPs (SHA-256 `bb8fea4b...71ecd`).
- 636 PEP number/label pairs in 71 files: 544 `ok`, 89 `weak`, 3 `miscite`, 0 `unknown_pep`.
  Full rows: `results/run1-summary.json`, `results/flagged.csv`.

## Verdicts

| | Prediction | Result | Verdict |
|---|---|---|---|
| P1 | both 3.12 PEP 697 lines flagged `miscite`, PEP 689 the better fit | lines 136 and 1866, both -> 689 | **HELD** |
| P2 | at least 95% of dash-separated pairs score >= 0.75 for the cited PEP | 239 of 245 (97.6%) | **HELD** |
| P3 | at least one other wrong PEP number confirmed in `Doc/` | 0 clear-cut (1 debatable, below) | **FAILED** |
| P4 | at least half of non-control `miscite` leads are real errors | 0 of 1 | **FAILED** |

## The one non-control lead

`Doc/whatsnew/3.15.rst` line 1832: `:pep:`800`: Add typing.disjoint_base, a new decorator marking
a class ...`. The detector preferred PEP 3129 ("Class Decorators") because the label contains
"decorator" and "class". PEP 800 is "Disjoint bases in the type system" and is the PEP that adds
`typing.disjoint_base`. **Right number; label artefact.** So detector precision on new leads is
0 of 1.

## Reading the misses (all 89 `weak` rows, not just the 20 the plan asked for)

The plan said to sample 20 `weak` rows at seed 0. Because there were only 89, every one was read
instead. 88 cite the right PEP: the label is prose that shares no words with the PEP title
(for example `:pep:`3151`, this class was made an alias of OSError` or `:pep:`667`, the
semantics of mutating the mapping objects`), or it continues a sentence that names two PEPs.

One is **debatable** and is listed in FIXLIST.md but not counted for P3:

- `Doc/whatsnew/2.7.rst`, section heading `PEP 3137: The memoryview Object`, and its `seealso`
  `:pep:`3137` - Immutable Bytes and Mutable Buffer`. PEP 3137 itself says that memoryview was
  "introduce[d] by PEP 3118" and that "the rest of this PEP doesn't discuss the functionality of
  memoryview". PEP 3118 ("Revising the buffer protocol") is the PEP that specifies memoryview.
  PEP 3137 does list memoryview in its naming table, so citing it is not plainly wrong. This is
  the Python 2.7 page, so it is not worth a change request on its own.

## What this means

The mechanical check works (P1, P2) but finds almost nothing new: CPython's PEP citations are
clean apart from the 3.12 case it was built from. Together with the hand read of about 230 What's
New headline citations before the run, this suggests the 3.12 PEP 697/689 slip is an isolated
error, not a pattern. P3 and P4 failed and are reported as failures.

## Limits

Title-word overlap only; citations in running prose without a separator are not checked; `main`
only.
