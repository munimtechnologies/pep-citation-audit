# Pre-registration: do CPython's docs cite the right PEP?

MV2, Munim, Inc. (mv2@munimtech.com). Filed 2026-10-31, before the data run. Made with AI agents
working in MV2's name. Code Apache-2.0; text and results CC BY 4.0.

## Why this study exists

While grading munimtechnologies/pep-version-whatsnew-audit, a missing mention led to a real error:
What's New in Python 3.12 credits the Unstable C API tier to **PEP 697** (which is "Limited C API
for Extending Opaque Types") instead of **PEP 689** ("Unstable C API tier"), in two places. A wrong
PEP number is easy to make (two PEPs by the same author, same release) and hard to see. This study
checks every PEP number/label pair in CPython's `Doc/` tree mechanically, then has a person read
each lead.

## Prior art (searched 2026-10-31)

- python/cpython issues and PRs searched for "PEP 689" whatsnew, "PEP 697" unstable and
  "unstable C API tier" whatsnew: nothing about the 3.12 mix-up.
- Sphinx's `:pep:` role and the docs linkcheck verify that a PEP *exists*, not that the number fits
  the text around it.
- No tool or study was found that checks PEP citations against PEP titles.

## What was already seen (how blind this is)

- The 3.12 case above (it is the positive control, P1).
- After finding it, every PEP citation in a 3.x What's New section title or summary/feature
  bullet (about 230 lines, 3.0 to 3.15) was read by hand; no other wrong number was seen. So the
  What's New headline lines are not blind. The library, reference, C API, howto, tutorial and 2.x
  What's New pages, and the `seealso` blocks everywhere, are blind.

## Data (fixed before the run)

- python/cpython `main` as a tarball from codeload.github.com (commit id from the archive header and
  SHA-256 recorded); every `Doc/**/*.rst` file.
- https://peps.python.org/api/peps.json (SHA-256 recorded; a copy is saved).

## Method (fixed in citecheck.py)

- A citation pair is `:pep:`N``, `:ref:`PEP N <label>`` or plain `PEP N`, followed by a separator
  (`--`, em dash, en dash, `-`, `:` or `,`) and a label running to the end of the line. If the line
  ends at the separator, the label is the next (indented) line. If the label has fewer than 3
  content words, the next indented line is added. Labels that cite another PEP are skipped.
- Words are lower-cased, stop words dropped, and suffixes stripped consistently.
- *Score* of a PEP for a label = share of the PEP title's words found in the label.
- Flags: **miscite** if the cited PEP scores at most 0.5, some other PEP (with at least 2 title
  words) scores at least 0.75, and the gap is at least 0.4; **weak** if the cited PEP scores below
  0.34; **unknown_pep** if the number is not in peps.json; otherwise **ok**.

## Predictions

- **P1 (positive control).** Both 3.12 lines that call the unstable C API tier PEP 697 are flagged
  `miscite` with PEP 689 as the better fit. If either is missed, the detector is broken and P3/P4
  are not graded. (If upstream fixes those lines first, P1 is NOT_TESTABLE and the unit tests,
  which contain the same lines, stand in.)
- **P2.** Among pairs whose separator is a dash (the form used when quoting a PEP's title, as in
  `seealso` blocks), **at least 95%** have the cited PEP scoring at least 0.75. Expected about 98%.
- **P3.** After reading every `miscite` lead and every `unknown_pep` row by hand, **at least one
  wrong PEP number other than the 3.12 case** is confirmed somewhere in `Doc/`. Prior about 40%.
- **P4.** Of the `miscite` leads other than the control, **at least half** are confirmed errors
  (detector precision). Prior about 40%; reported even with only a few leads.

## Grading plan

Each lead is read in context in the rst file and checked against the PEP. Labels: wrong number
(error), right number but label describes a related part (not an error), label is prose that only
looks like a title (artefact). Confirmed errors go to FIXLIST.md with evidence, and are reported
upstream as one python/cpython issue (made with AI agents, said plainly). `weak` rows are counted
and sampled (20 at random, seed 0), not all read.

## Limits

- Title overlap is crude. A label can describe a feature in words that share nothing with the
  PEP title. That gives `weak` rows, which are not errors.
- Only pairs on one line (plus one continuation line) are seen. A citation inside running prose
  without a separator is not checked.
- Docs on `main` only; older branches are not checked.
