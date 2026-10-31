#!/usr/bin/env python3
# Copyright 2026 Munim, Inc.
# SPDX-License-Identifier: Apache-2.0
# Made with AI agents working in the name of MV2 of Munim, Inc. (mv2@munimtech.com).
"""Download CPython main's Doc/ tree and peps.json, run citecheck, write /out."""
import argparse
import csv
import hashlib
import json
import os
import tarfile
import time
import urllib.request

import citecheck

TARBALL = "https://codeload.github.com/python/cpython/tar.gz/refs/heads/main"
PEPS = "https://peps.python.org/api/peps.json"
UA = "mv2-pep-citation-audit/1.0 (MV2, Munim, Inc.; mv2@munimtech.com)"


def fetch(url, path, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=300) as r, open(path + ".part", "wb") as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b)
            os.replace(path + ".part", path)
            return
        except Exception as e:  # network hiccup: retry
            print("fetch retry", url, repr(e), flush=True)
            time.sleep(10 * (i + 1))
    raise SystemExit("download failed: " + url)


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    os.makedirs(a.data_dir, exist_ok=True)
    fetched_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    tpath = os.path.join(a.data_dir, "citecheck-cpython-main.tar.gz")
    ppath = os.path.join(a.data_dir, "citecheck-peps.json")
    fetch(TARBALL, tpath)
    fetch(PEPS, ppath)

    with open(ppath, "rb") as f:
        raw = f.read()
    peps = {int(k): v["title"] for k, v in json.loads(raw).items()}

    docs, doc_sha = {}, {}
    with tarfile.open(tpath, "r:gz") as tf:
        for m in tf:
            if not m.isfile():
                continue
            parts = m.name.split("/", 1)
            if len(parts) != 2:
                continue
            rel = parts[1]
            if rel.startswith("Doc/") and rel.endswith(".rst"):
                b = tf.extractfile(m).read()
                docs[rel] = b.decode("utf-8", "replace")
                doc_sha[rel] = sha256(b)
        commit = tf.pax_headers.get("comment", "")
    with open(tpath, "rb") as f:
        tar_sha = sha256(f.read())

    rows = citecheck.audit(docs, peps)
    summary = citecheck.grade(rows)
    summary["source"] = {
        "cpython_tarball": TARBALL,
        "cpython_commit": commit,
        "cpython_tarball_sha256": tar_sha,
        "peps_json_url": PEPS,
        "peps_json_sha256": sha256(raw),
        "fetched_at": fetched_at,
        "n_doc_rst_files": len(docs),
        "n_peps": len(peps),
    }

    snap = os.path.join(a.out_dir, "snapshot")
    os.makedirs(snap, exist_ok=True)
    with open(os.path.join(snap, "peps.json"), "wb") as f:
        f.write(raw)
    with open(os.path.join(snap, "doc_rst_sha256.json"), "w") as f:
        json.dump(doc_sha, f, indent=1, sort_keys=True)
    with open(os.path.join(a.out_dir, "rows.json"), "w") as f:
        json.dump(rows, f, indent=1)
    fields = ["file", "line", "pep", "sep", "flag", "cited_score", "best_other",
              "best_other_score", "label", "cited_title", "best_other_title", "from_next_line"]
    for name, sel in (("rows.csv", rows),
                      ("flagged.csv", [r for r in rows if r["flag"] != "ok"])):
        with open(os.path.join(a.out_dir, name), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in sel:
                w.writerow({k: r.get(k) for k in fields})
    with open(os.path.join(a.out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)
    print("P1", summary["P1_positive_control"]["verdict"])
    print("P2", summary["P2_dash_titles_match"])
    print("flags", summary["flags"], "miscite leads", len(summary["miscite_leads"]))
    for r in summary["miscite_leads"]:
        print("LEAD", r["file"], r["line"], r["pep"], "->", r["best_other"], "|", r["label"][:100])


if __name__ == "__main__":
    main()
