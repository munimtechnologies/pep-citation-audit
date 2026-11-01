# FIXLIST: PEP citations in CPython's Doc/ (run 1)

Checked at python/cpython commit `9c0cfb141c236c902954841bb6cca407f86e1eeb` (2026-11-01).
MV2, Munim, Inc.; made with AI agents. CC BY 4.0.

## Confirmed

1. `Doc/whatsnew/3.12.rst` lines 136 and 1866 credit the Unstable C API tier to PEP 697. It is
   PEP 689 ("Unstable C API tier"); PEP 697 is "Limited C API for Extending Opaque Types", which
   the same page cites correctly further down. This is the positive control (found by hand in
   munimtechnologies/pep-version-whatsnew-audit). Upstream report: being filed as one
   python/cpython documentation issue.

## Debatable (not counted, not filed)

2. `Doc/whatsnew/2.7.rst`, `PEP 3137: The memoryview Object` and its `seealso`. memoryview is
   specified by PEP 3118; PEP 3137 mentions it only to justify dropping the old `buffer` type.

## Checked and fine

- `Doc/whatsnew/3.15.rst` line 1832, `:pep:`800``: right PEP (the detector's only new lead).
- All 89 `weak` rows (see GRADING.md).
