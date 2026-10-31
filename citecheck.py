#!/usr/bin/env python3
# Copyright 2026 Munim, Inc.
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com).
"""Cross-check PEP number / title pairs in CPython's Doc/ tree against peps.json.

A *citation pair* is a PEP reference followed by a separator and a short label, for example

    * :ref:`PEP 697 <whatsnew312-pep697>`, unstable C API tier
    :pep:`3156` -- Asynchronous IO Support Rebooted: the "asyncio" Module
    PEP 695: Type Parameter Syntax

For each pair we measure how much of the cited PEP's title appears in the label
("title containment") and whether some *other* PEP's title fits the label much better.
A much better fit elsewhere is a lead for a wrong PEP number, to be read by a person.
Standard library only.
"""
import re

STOP = frozenset(
    "a an the of for to in on and or with from by as at is be are it its new add adding added "
    "python pep peps support via into".split()
)

# A PEP reference: :pep:`N`, :ref:`PEP N <label>`, or plain "PEP N".
CITE = re.compile(r":pep:`0*(\d+)`|:ref:`PEP 0*(\d+)\s*<[^`>]*>`|\bPEP 0*(\d+)\b")
# Separator after the reference, then the label.
SEP = re.compile(r"^\s*(--|—|–|-|:|,)\s+(\S.*)$")
BARE_SEPS = (":", ",", "--", "-", "—", "–")
DASH_SEPS = ("--", "—", "–", "-")
ROLE_TXT = re.compile(r":[a-zA-Z:+-]+:`([^`<]*?)\s*(?:<[^`>]*>)?`")
LINK_TXT = re.compile(r"`([^`<]*?)\s*(?:<[^`>]*>)?`_{1,2}")
TOKEN = re.compile(r"[a-z0-9]+")
NESTED = re.compile(r":pep:`|\bPEP \d")

# Flag thresholds (fixed in PREREG.md).
MISCITE_CITED_MAX = 0.5
MISCITE_OTHER_MIN = 0.75
MISCITE_GAP_MIN = 0.4
WEAK_MAX = 0.34


def stem(t):
    """A tiny suffix stripper; only needs to be consistent, not linguistic."""
    if t.endswith("sses"):
        t = t[:-2]
    elif t.endswith("ies") and len(t) > 4:
        t = t[:-3] + "i"
    elif t.endswith("s") and len(t) > 3 and not t.endswith(("ss", "us", "is")):
        t = t[:-1]
    if t.endswith("ing") and len(t) - 3 >= 3:
        t = t[:-3]
    elif t.endswith("ed") and len(t) - 2 >= 3:
        t = t[:-2]
    if t.endswith("e") and len(t) > 4:
        t = t[:-1]
    if t.endswith("y") and len(t) > 3:
        t = t[:-1] + "i"
    return t


def clean(s):
    s = ROLE_TXT.sub(r"\1", s)
    s = s.replace("``", "")
    s = LINK_TXT.sub(r"\1", s)
    return s


def content_tokens(text):
    out = []
    for t in TOKEN.findall(text.lower()):
        if t in STOP:
            continue
        out.append(stem(t))
    return out


def title_tokens(title):
    return sorted(set(content_tokens(clean(title))))


def containment(ttoks, label_set):
    if not ttoks:
        return 0.0
    hit = sum(1 for t in ttoks if t in label_set)
    return hit / len(ttoks)


def _is_continuation(line):
    return line is not None and line[:1].isspace() and line.strip() != ""


def extract(lines):
    """Yield (line_no, pep, sep, label, from_next_line) for each citation pair."""
    out = []
    for i, line in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        for m in CITE.finditer(line):
            num = int(m.group(1) or m.group(2) or m.group(3))
            rest = line[m.end():]
            sm = SEP.match(rest)
            from_next = False
            if sm:
                sep, label = sm.group(1), sm.group(2)
            elif rest.strip() in BARE_SEPS and _is_continuation(nxt):
                sep, label, from_next = rest.strip(), nxt.strip(), True
            else:
                continue
            if NESTED.search(label):
                continue  # several PEPs share one label; not a pair
            if not from_next and len(content_tokens(clean(label))) < 3 and _is_continuation(nxt):
                label = label + " " + nxt.strip()
                from_next = True
            out.append((i + 1, num, sep, label, from_next))
    return out


def classify(cited, best, best_ntok):
    if cited is None:
        return "unknown_pep"
    if (cited <= MISCITE_CITED_MAX and best >= MISCITE_OTHER_MIN
            and best - cited >= MISCITE_GAP_MIN and best_ntok >= 2):
        return "miscite"
    if cited < WEAK_MAX:
        return "weak"
    return "ok"


def audit(docs, peps):
    """docs: {relpath: text}; peps: {number: title}. Returns a list of row dicts."""
    ttoks = {n: title_tokens(t) for n, t in peps.items()}
    rows = []
    for rel in sorted(docs):
        lines = docs[rel].split("\n")
        for line_no, num, sep, label, from_next in extract(lines):
            lset = set(content_tokens(clean(label)))
            cited = containment(ttoks[num], lset) if num in ttoks else None
            best_key, best_num = None, None
            for n, tt in ttoks.items():
                if n == num:
                    continue
                sc = containment(tt, lset)
                key = (sc, sum(1 for t in tt if t in lset), -n)
                if best_key is None or key > best_key:
                    best_key, best_num = key, n
            best = best_key[0] if best_key else 0.0
            best_ntok = len(ttoks[best_num]) if best_num is not None else 0
            rows.append({
                "file": rel,
                "line": line_no,
                "pep": num,
                "sep": sep,
                "label": clean(label)[:200],
                "from_next_line": from_next,
                "cited_title": peps.get(num),
                "cited_score": None if cited is None else round(cited, 4),
                "best_other": best_num,
                "best_other_title": peps.get(best_num) if best_num is not None else None,
                "best_other_score": round(best, 4),
                "flag": classify(cited, best, best_ntok),
            })
    return rows


def grade(rows):
    """Mechanical verdicts for P1 and P2; P3 and P4 need hand review."""
    control = [r for r in rows if r["file"] == "Doc/whatsnew/3.12.rst" and r["pep"] == 697
               and "unstable" in r["label"].lower()]
    if not control:
        p1 = {"verdict": "NOT_TESTABLE", "n": 0, "note": "control lines absent (fixed upstream?)"}
    else:
        ok = len(control) >= 2 and all(r["flag"] == "miscite" and r["best_other"] == 689
                                       for r in control)
        p1 = {"verdict": "HELD" if ok else "FAILED", "n": len(control),
              "rows": [{"line": r["line"], "flag": r["flag"], "best_other": r["best_other"]}
                       for r in control]}
    dash = [r for r in rows if r["sep"] in DASH_SEPS and r["flag"] != "unknown_pep"]
    good = sum(1 for r in dash if r["cited_score"] >= MISCITE_OTHER_MIN)
    share = good / len(dash) if dash else None
    p2 = {"bar": 0.95, "n": len(dash), "good": good, "share": share,
          "verdict": ("HELD" if share is not None and share >= 0.95 else
                      "FAILED" if share is not None else "NOT_TESTABLE")}
    ctl = {(r["file"], r["line"]) for r in control}
    flags = {}
    for r in rows:
        flags[r["flag"]] = flags.get(r["flag"], 0) + 1
    miscite_other = [r for r in rows if r["flag"] == "miscite" and (r["file"], r["line"]) not in ctl]
    return {
        "P1_positive_control": p1,
        "P2_dash_titles_match": p2,
        "P3_new_confirmed_miscitation": {"verdict": "PENDING_HAND_REVIEW",
                                         "leads": len(miscite_other)},
        "P4_detector_precision": {"verdict": "PENDING_HAND_REVIEW", "bar": 0.5,
                                  "leads": len(miscite_other)},
        "n_rows": len(rows),
        "n_files_with_rows": len({r["file"] for r in rows}),
        "flags": flags,
        "miscite_leads": miscite_other,
        "unknown_pep": [r for r in rows if r["flag"] == "unknown_pep"],
    }
